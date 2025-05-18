from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products, inventory, sales
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-commerce Admin API",
    description="API for e-commerce admin dashboard providing insights into sales, revenue, and inventory",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, tags=["Products"])
app.include_router(inventory.router, tags=["Inventory"])
app.include_router(sales.router, tags=["Sales"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the E-commerce Admin API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)