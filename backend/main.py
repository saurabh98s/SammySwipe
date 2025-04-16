from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import get_settings
from .db.database import db
from .api import auth, users, matches, chat

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])
app.include_router(matches.router, prefix=settings.API_V1_STR, tags=["matches"])
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])

@app.on_event("startup")
async def startup_event():
    # Create database constraints
    db.create_constraints()

@app.on_event("shutdown")
async def shutdown_event():
    # Close database connection
    db.close()

@app.get("/")
async def root():
    return {"message": "Welcome to SammySwipe API"} 