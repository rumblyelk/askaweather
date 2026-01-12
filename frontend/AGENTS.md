gent Instructions (Frontend)

Frontend stack: React SPA (Vite). Responsibilities: chat UI rendering, user input, calling backend, and displaying responses.

## UI Requirements
- Single page with chat transcript and input bar at bottom.
- Distinct bubble styles for user vs assistant.
- Auto-scroll to latest message on new messages.
- Loading/typing indicator while awaiting backend response.
- Disable send while a request is in flight.

## Backend Contract
- Call POST /chat using an API base URL from env (e.g., API_BASE_URL).
- Do not embed weather logic in the frontend.
- Do not change payload shapes without updating `SPEC.md` and coordinating with backend.

## State
- Keep conversation history in client state and send it to backend each turn.
- No persistence required beyond runtime (optional localStorage is allowed but not required).
