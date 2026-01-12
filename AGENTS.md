# Agent Instructions (Repo-Wide)

This repository implements a conversational weather assistant.

## Non-Negotiable Invariants
- The assistant must not provide weather facts without using WeatherAPI data for the relevant location/timeframe.
- If required context is missing (location and/or timeframe), the assistant asks a concise clarifying question instead of guessing.
- Ask at most one clarifying question per assistant turn.
- The backend is the source of truth for intent/slot resolution, date/time interpretation, and WeatherAPI calls.
- The frontend must remain thin: chat UI + calling the backend.

## Integration Contract
- The API contract for the frontend/backend boundary is defined in `SPEC.md` (to be created).
- Do not change request/response shapes, ports, or env var names without updating `SPEC.md` and adjusting both sides.

## Security
- Never commit any code.
- Use `.env.example` templates and local `.env` files.

## Definition of Done (MVP)
- User can chat in the SPA.
- Backend responds with either:
  - a clarifying question, or
  - an answer grounded in WeatherAPI data.
- Works locally with clear README instructions.
