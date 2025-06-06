from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import user, receipt, food_image
from app.api.endpoints import nutrients
from fastapi.openapi.utils import get_openapi
from app.db.init_db import init_db

app = FastAPI(
    title="Micronutrient Radar API",
    description="Backend API for Micronutrient Radar - A smart nutrition tracking app",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(receipt.router, prefix=f"{settings.API_V1_STR}/receipts", tags=["receipts"])
app.include_router(food_image.router, prefix=f"{settings.API_V1_STR}/food-images", tags=["food-images"])
app.include_router(nutrients.router, prefix=f"{settings.API_V1_STR}/nutrients", tags=["nutrients"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Micronutrient Radar API",
        "version": "1.0.0",
        "status": "operational"
    }

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for op in path.values():
            op["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi 