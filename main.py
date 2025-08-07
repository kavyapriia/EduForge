import os
from dotenv import load_dotenv
load_dotenv()  # ADD THIS LINE AT THE VERY TOP
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from os.path import exists
import bugsnag
from bugsnag.asgi import BugsnagMiddleware


# Import your routers properly (import modules, not attributes)
from api.routes import (
    file,
    ai,
    auth,
    task,
    chat,
    user,
    org,
    cohort,
    course,
    milestone,
    scorecard,
    code,
    hva,
    video_course_generator,
)
from api.websockets import router as websocket_router
from api.scheduler import scheduler
from api.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start scheduler and background tasks
    scheduler.start()

    # Ensure local upload folder exists
    os.makedirs(settings.local_upload_folder, exist_ok=True)

    # If you have pending background tasks to resume, enable these after implementing the functions
    # asyncio.create_task(video_course_generator.resume_pending_task_generation_jobs())
    # asyncio.create_task(video_course_generator.resume_pending_course_structure_generation_jobs())

    yield  # Run the app

    # Clean shutdown
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)


# Configure Bugsnag if API key is present
if settings.bugsnag_api_key:
    bugsnag.configure(
        api_key=settings.bugsnag_api_key,
        project_root=os.path.dirname(os.path.abspath(__file__)),
        release_stage=settings.env or "development",
        notify_release_stages=["development", "staging", "production"],
        auto_capture_sessions=True,
    )
    app.add_middleware(BugsnagMiddleware)


    @app.middleware("http")
    async def bugsnag_request_middleware(request: Request, call_next):
        bugsnag.configure_request(
            context=f"{request.method} {request.url.path}",
            request_data={
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers),
                "query_params": dict(request.query_params),
                "path_params": request.path_params,
                "client": {
                    "host": request.client.host if request.client else None,
                    "port": request.client.port if request.client else None,
                },
            },
        )
        response = await call_next(request)
        return response


# Enable CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory if it exists in settings
if exists(settings.local_upload_folder) and hasattr(settings, "UPLOAD_FOLDER_NAME"):
    app.mount(
        f"/{settings.UPLOAD_FOLDER_NAME}",
        StaticFiles(directory=settings.local_upload_folder),
        name="uploads",
    )


# Include all API routers using module.router
app.include_router(video_course_generator.router)  # Video course generation endpoints
app.include_router(file.router, prefix="/file", tags=["file"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(task.router, prefix="/tasks", tags=["tasks"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(org.router, prefix="/organizations", tags=["organizations"])
app.include_router(cohort.router, prefix="/cohorts", tags=["cohorts"])
app.include_router(course.router, prefix="/courses", tags=["courses"])
app.include_router(milestone.router, prefix="/milestones", tags=["milestones"])
app.include_router(scorecard.router, prefix="/scorecards", tags=["scorecards"])
app.include_router(code.router, prefix="/code", tags=["code"])
app.include_router(hva.router, prefix="/hva", tags=["hva"])
app.include_router(websocket_router, prefix="/ws", tags=["websockets"])


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Optional: Add root endpoint to avoid 404 at "/"
@app.get("/")
async def root():
    return {"message": "Welcome to the SensAI API backend!"}
