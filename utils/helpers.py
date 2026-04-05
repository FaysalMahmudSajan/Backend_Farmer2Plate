from typing import Any

def model_to_dict(obj: Any) -> dict:
    return {c.key: getattr(obj, c.key) for c in obj.__table__.columns}


def calculate_total(items: list[dict]) -> float:
    return sum(item["price"] * item["quantity"] for item in items)

def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False
    
from math import radians, sin, cos, sqrt, atan2

def distance_km(lat1, lon1, lat2, lon2):
    R = 6371  
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c