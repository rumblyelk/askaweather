import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.chat import process_conversation
from anthropic.types import TextBlock, ToolUseBlock, Message

@pytest.mark.asyncio
async def test_process_conversation_multi_step():
    # Mock conversation history
    history = [{"role": "user", "content": "Will it rain during the next Manchester game?"}]
    
    # Mock WeatherAPI responses
    mock_sports_data = {
        "football": [{"match": "Manchester Utd vs Chelsea", "start": "2024-03-25 20:00"}]
    }
    mock_weather_data = {
        "forecast": {
            "forecastday": [
                {
                    "date": "2024-03-25",
                    "day": {"condition": {"text": "Rainy"}, "daily_chance_of_rain": 80}
                }
            ]
        }
    }

    # Mock Anthropic responses
    # Turn 1: Claude decides to call get_sports
    response_1 = MagicMock()
    response_1.stop_reason = "tool_use"
    response_1.content = [
        TextBlock(text="I'll check the sports schedule.", type="text"),
        ToolUseBlock(id="tool_1", name="get_sports", input={"location": "Manchester"}, type="tool_use")
    ]

    # Turn 2: Claude receives sports data, decides to call get_weather
    response_2 = MagicMock()
    response_2.stop_reason = "tool_use"
    response_2.content = [
        TextBlock(text="Found a match on March 25th. Checking weather.", type="text"),
        ToolUseBlock(id="tool_2", name="get_weather", input={"location": "Manchester", "date": "2024-03-25"}, type="tool_use")
    ]

    # Turn 3: Claude receives weather data, gives final answer
    response_3 = MagicMock()
    response_3.stop_reason = "end_turn"
    response_3.content = [
        TextBlock(text="Yes, it looks like rain on March 25th for the match.", type="text")
    ]

    # Patch everything
    with patch("app.chat.client.messages.create", side_effect=[response_1, response_2, response_3]) as mock_create:
        # Since client.messages.create is awaited, we need the side_effect items to be awaitable
        # However, MagicMock isn't awaitable by default. We should use AsyncMock.
        # But here we are patching the method itself. 
        # A simple way is to wrap the return values in futures or use AsyncMock properly.
        
        # Let's fix the mocking strategy:
        async def side_effect(*args, **kwargs):
            return mock_create.side_effect_iterator.next()
            
        mock_create.side_effect_iterator = iter([response_1, response_2, response_3])
        mock_create.side_effect = None
        mock_create.return_value = None # clear defaults
        
        # Easier way: Just make the side_effect return values awaitable? No, side_effect on AsyncMock
        # can be an iterable of return values. But the return values must be what 'await' expects.
        # Since `create` is async, it returns a coroutine.
        # We need to configure the AsyncMock to return our response objects when awaited.
        
        pass

@pytest.mark.asyncio
async def test_process_conversation_multi_step():
    # Mock conversation history
    history = [{"role": "user", "content": "Will it rain during the next Manchester game?"}]
    
    # Data
    mock_sports_data = {"football": [{"match": "Manchester Utd vs Chelsea", "start": "2024-03-25 20:00"}]}
    mock_weather_data = {"forecast": {"forecastday": [{"date": "2024-03-25", "day": {"condition": {"text": "Rainy"}}}]}}

    # Responses
    r1 = MagicMock()
    r1.stop_reason = "tool_use"
    r1.content = [TextBlock(text="Checking sports...", type="text"), ToolUseBlock(id="t1", name="get_sports", input={"location": "Manchester"}, type="tool_use")]

    r2 = MagicMock()
    r2.stop_reason = "tool_use"
    r2.content = [TextBlock(text="Checking weather...", type="text"), ToolUseBlock(id="t2", name="get_weather", input={"location": "Manchester", "date": "2024-03-25"}, type="tool_use")]

    r3 = MagicMock()
    r3.stop_reason = "end_turn"
    r3.content = [TextBlock(text="Yes, it looks like rain.", type="text")]

    # We need to patch the AsyncAnthropic client's method properly.
    # The client is instantiated in app.chat. We patch 'app.chat.client.messages.create'.
    
    with patch("app.chat.client.messages.create", new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = [r1, r2, r3]
        
        with patch("app.chat.get_sports", return_value=mock_sports_data):
            with patch("app.chat.get_weather", return_value=mock_weather_data):
                
                result = await process_conversation(history)
                
                assert result["role"] == "assistant"
                assert "Yes, it looks like rain" in result["content"]
                assert mock_create.call_count == 3
