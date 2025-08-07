# EduForge - SensAI Hackathon Backend
This is the backend for the SensAI Hackathon (Problem Statement 1) by HyperVerge, built using FastAPI. It supports features like video course generation, file uploads, authentication, task management, and more.

Features
- REST API with FastAPI
- Video course generation endpoints
- WebSockets integration
- Scheduler for background tasks
- Modular API routes
- CORS and static file serving
- Bugsnag integration for error reporting

Tech Stack
- Python
- FastAPI
- WebSockets
- BackgroundScheduler
- dotenv

Setup Instructions

1. Clone Repository
 git clone https://github.com/kavyapriia/EduForge.git
cd EduForge

2. Set up virtual environment
python -m venv venv
venv\Scripts\activate  
3.Install dependencies
pip install -r requirements.txt

4. Set up environment variables
Copy .env.example to .env and fill in the appropriate values.

5. Run the app
uvicorn main:app --reload
API will be available at: http://127.0.0.1:8000




