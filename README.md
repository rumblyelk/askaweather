# Askaweather

A conversational weather assistant using FastAPI, React, and Claude.

## Prerequisites
- Python 3.9+
- Node.js 16+
- Anthropic API Key
- WeatherAPI.com API Key

## Setup

1. **Clone the repository** (if not already done)

2. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Create .env file
   cp ../.env.example .env
   # Edit .env and add your keys
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   
   # Create .env file
   echo "VITE_API_BASE_URL=http://localhost:8000" > .env
   ```

## Running the Application

1. **Start Backend**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload --port 8000
   ```

2. **Start Frontend** (in a new terminal)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Usage**
   Open http://localhost:5173 in your browser.
