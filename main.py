from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database.db import Base, engine
from routers import farmer, customer, admin, product, order,web_maker

Base.metadata.create_all(engine)

app = FastAPI(title="Farm2Plate (Faturi)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fatirbinabdullah.github.io","https://fatirbinabdullah.github.io/Farmer2Plate","http://127.0.0.1:8080", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(farmer.router)
app.include_router(customer.router)
app.include_router(admin.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(web_maker.router)

@app.get("/")
def root():
    return {"message": "Farm2Plane (Fatir)"}