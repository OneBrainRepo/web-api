import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from webapi.routes import user_routes, demo_routes, chat_routes
from webapi.db.database import create_tables

# Cors Settings
cors_allowed_origins_str = os.getenv("CORS_ALLOWED_ORIGINS", "")
origins = cors_allowed_origins_str.split(",") if cors_allowed_origins_str else ["*"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Call create tables here
create_tables()

## Add super routes
# Demo Under /demo route
app.include_router(user_routes.router,tags=["Users"],prefix="/users")
app.include_router(demo_routes.router,tags=["Demo"],prefix="/demo")
app.include_router(chat_routes.router,tags=["Chat"],prefix="/chat")