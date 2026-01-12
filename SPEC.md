# API Specification & Integration Contract

## Overview
This document defines the interface between the React frontend and the FastAPI backend. The backend is the source of truth for all conversation logic, weather data retrieval, and state interpretation.

## Environment Variables

### Backend
| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | API key for Anthropic (Claude) | Yes |
| `WEATHERAPI_KEY` | API key for WeatherAPI.com | Yes |

### Frontend
| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_API_BASE_URL` | URL of the backend API (e.g. `http://localhost:8000`) | Yes |

## API Endpoints

### 1. Chat Interaction
**Endpoint:** `POST /chat`

**Description:**
Sends the full conversation history to the backend. The backend processes the latest user message, performs necessary tool calls (WeatherAPI), and returns the assistant's response.

**Request Headers:**
- `Content-Type: application/json`

**Request Body:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What is the weather in Berlin?"
    },
    {
      "role": "assistant",
      "content": "I can help with that. When are you looking to go?"
    },
    {
      "role": "user",
      "content": "Tomorrow morning."
    }
  ]
}
```

**Response Body:**
```json
{
  "message": {
    "role": "assistant",
    "content": "The forecast for Berlin tomorrow morning is..."
  }
}
```

**Response Codes:**
- `200 OK`: Success.
- `422 Unprocessable Entity`: Invalid request format.
- `500 Internal Server Error`: Backend processing error or upstream API failure.

## Data Types

### Message
| Field | Type | Description |
|-------|------|-------------|
| `role` | `string` | "user" or "assistant" |
| `content` | `string` | The text content of the message |

### ChatRequest
| Field | Type | Description |
|-------|------|-------------|
| `messages` | `Message[]` | The full history of the conversation |

### ChatResponse
| Field | Type | Description |
|-------|------|-------------|
| `message` | `Message` | The assistant's reply |
