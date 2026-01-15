import os
import json
from typing import List, Dict, Any, cast
from anthropic import AsyncAnthropic
from anthropic.types import MessageParam, ToolParam, TextBlock, ToolUseBlock
from app.weatherapi import get_weather, get_sports, get_air_quality
from app.dates import get_current_date, resolve_relative_date

# Initialize Anthropic client
client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Define the tool definition for Claude
WEATHER_TOOL: ToolParam = {
    "name": "get_weather",
    "description": "Get the weather forecast for a specific location and date. usage: call this when the user asks about weather. Do NOT call this if the user has not provided a location.",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and optional state/country (e.g. 'Berlin', 'New York, NY')"
            },
            "date": {
                "type": "string",
                "description": "The date in YYYY-MM-DD format. If the user says 'tomorrow' or 'next Tuesday', you can convert it or pass the string directly (e.g. 'tomorrow'). If asking for 'now' or 'current', leave this blank."
            }
        },
        "required": ["location"]
    }
}

SPORTS_TOOL: ToolParam = {
    "name": "get_sports",
    "description": "Get recent or upcoming sports events/scores for a location. Covers Football, Cricket, and Golf.",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city or region (e.g. 'London', 'Madrid')"
            }
        },
        "required": ["location"]
    }
}

AQI_TOOL: ToolParam = {
    "name": "get_air_quality",
    "description": "Get current air quality index (AQI) and pollutant levels.",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city to check air quality for"
            }
        },
        "required": ["location"]
    }
}

SYSTEM_PROMPT = f"""
You are Askaweather, a helpful weather and lifestyle assistant.
Today's date is {get_current_date()}.

RULES:
1. You must answer user questions about weather, sports, or air quality using the appropriate tools:
   - Use 'get_weather' for forecasts, temperature, rain, etc.
   - Use 'get_sports' for match schedules, scores, or upcoming games (Football, Cricket, Golf).
   - Use 'get_air_quality' for pollution, AQI, or air cleanliness inquiries.
2. NEVER guess data. You must always use the tools.
3. If the user does not provide a location, you MUST ask for it.
4. If a user asks a complex question (e.g. "Will it rain during the next game?"), break it down:
   - First, find the date/time of the event using 'get_sports'.
   - Then, use that date to check the forecast with 'get_weather'.
   - Do NOT ask the user for the date if you can find it yourself.
5. Ask strictly ONE clarifying question per turn. Do not overload the user.
6. If the user's intent is unclear, ask for clarification.
7. Be concise and natural.
"""

async def process_conversation(conversation_history: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Orchestrates the conversation with a tool loop:
    1. Sends messages + tool def to Claude.
    2. Checks if Claude wants to call a tool.
    3. If tool call: execute it, append result, and LOOP back to step 1.
    4. If no tool call: return Claude's text response.
    
    Limits the loop to avoid infinite recursion.
    """
    MAX_TURNS = 5
    current_turn = 0
    
    # Convert generic dicts to MessageParam to satisfy type checker
    messages: List[MessageParam] = [
        {"role": m["role"], "content": m["content"]}  # type: ignore[misc]
        for m in conversation_history
    ]

    while current_turn < MAX_TURNS:
        try:
            response = await client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=messages,
                tools=[WEATHER_TOOL, SPORTS_TOOL, AQI_TOOL]
            )
        except Exception as e:
            return {"role": "assistant", "content": f"I encountered an error contacting my brain: {str(e)}"}

        stop_reason = response.stop_reason
        final_content = response.content

        # If Claude simply replies with text (end_turn), we are done.
        if stop_reason != "tool_use":
            text_content = ""
            for block in final_content:
                if isinstance(block, TextBlock):
                    text_content += block.text
            
            if not text_content:
                 # Fallback if empty
                 return {"role": "assistant", "content": "I'm not sure how to help with that."}
            
            return {"role": "assistant", "content": text_content}

        # If we are here, stop_reason is "tool_use". Handle the tools.
        tool_use_blocks = [b for b in final_content if isinstance(b, ToolUseBlock)]
        
        if tool_use_blocks:
            tool_results = []
            
            for tool_use_block in tool_use_blocks:
                tool_name = tool_use_block.name
                tool_inputs = cast(Dict[str, Any], tool_use_block.input)
                tool_use_id = tool_use_block.id
                
                tool_result_content = ""

                if tool_name == "get_weather":
                    location = str(tool_inputs.get("location"))
                    date_input = tool_inputs.get("date")
                    final_date = None
                    if date_input:
                        final_date = resolve_relative_date(str(date_input))
                    weather_data = await get_weather(location, final_date)
                    tool_result_content = json.dumps(weather_data)

                elif tool_name == "get_sports":
                    location = str(tool_inputs.get("location"))
                    sports_data = await get_sports(location)
                    tool_result_content = json.dumps(sports_data)
                
                elif tool_name == "get_air_quality":
                    location = str(tool_inputs.get("location"))
                    aqi_data = await get_air_quality(location)
                    tool_result_content = json.dumps(aqi_data)
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": tool_result_content
                })
            
            # Append the assistant's tool-use message
            messages.append({
                "role": "assistant",
                "content": final_content  # type: ignore[typeddict-item]
            })
            
            # Append the results as a user message
            messages.append({
                "role": "user",
                "content": tool_results
            })
            
            # Increment turn counter and LOOP again
            current_turn += 1

    return {"role": "assistant", "content": "I apologize, but I needed too many steps to answer your request."}
