# Agent Instructions (Backend)

Backend stack: FastAPI. Responsibilities: conversation orchestration, slot filling, date/time interpretation, WeatherAPI calls, and final natural-language response grounded in retrieved data.

## Core Behavior
- For any weather-dependent query, call WeatherAPI (do not hallucinate).
- If location is missing, ask: "Which city (and country/state if needed)?"
- If timeframe is missing/ambiguous, ask: "For which day/time are you asking?"
- Ask only one question per turn. Prefer missing location first.

## Determinism & Validation
- Use strict validation (Pydantic models) for any structured LLM output or tool arguments.
- If the LLM output is invalid, retry once with a schema correction prompt; if still invalid, fall back to a clarifying question.

## WeatherAPI Usage
- Prefer Forecast endpoint for most queries; current weather only when user explicitly asks "now/current".
- Handle relative time (today/tomorrow/this weekend/Tuesday) in Python deterministically.

## Interfaces
- Expose a single primary endpoint: POST /chat
- Input: conversation messages (role + content)
- Output: one assistant message (role=assistant, content=text)

## Files to Maintain
- `backend/app/main.py` FastAPI app + CORS
- `backend/app/chat.py` orchestration loop
- `backend/app/weatherapi.py` WeatherAPI client
- `backend/app/dates.py` date parsing and resolution utilities
