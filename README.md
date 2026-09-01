# Manufact AI Decision Support Platform

An agentic manufacturing decision support platform using a multi-agent generative AI architecture to analyze production capacity, inventory, and supply chain constraints.

## Prerequisites
- Docker Desktop (for PostgreSQL)
- Python 3.10+
- Node.js 18+

## Setup & Running

### 1. Database Setup
Ensure Docker Desktop is running, then start the PostgreSQL container:
```bash
docker-compose up -d db
```

### 2. Backend Setup
Activate the virtual environment and install dependencies:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Set your Gemini API key in your environment (or `.env` file):
```bash
export GEMINI_API_KEY="your-api-key-here"
```

Run database migrations to create the schemas and tables:
```bash
alembic upgrade head
```

Seed the database with the example "Gearbox Assembly" synthetic scenario:
```bash
python app/db/seed.py
```

Start the FastAPI backend:
```bash
uvicorn app.api.main:app --reload
```

### 3. Frontend Setup
In a new terminal window, navigate to the frontend directory:
```bash
cd frontend
npm install
npm run dev
```

### Usage
Open http://localhost:5173/ in your browser. From the dashboard, enter a manufacturing query such as:
> "Can we complete 500 gearbox assemblies by Friday?"

The system will orchestrate the Planner, Production, Inventory, and Knowledge agents to synthesize a reliable decision output.
