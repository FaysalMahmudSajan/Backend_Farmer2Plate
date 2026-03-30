from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database.db import Base, engine
from routers import farmer, customer, admin, product, order

Base.metadata.create_all(engine)

app = FastAPI(title="Farm2Plate (Faturi)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(farmer.router)
app.include_router(customer.router)
app.include_router(admin.router)
app.include_router(product.router)
app.include_router(order.router)

@app.get("/")
def root():
    return {"message": "Farm2Plane (Faturi)"}

# app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True, host="192.168.1.7")