from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products, inventory, sales
from app.database import engine
from app import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-commerce Admin API",
    description="API for e-commerce admin dashboard",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(sales.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to E-commerce Admin API",
        "docs": "/docs",
        "redoc": "/redoc"
    }