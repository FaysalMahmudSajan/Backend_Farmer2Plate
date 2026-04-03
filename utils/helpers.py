from typing import Any

# ✅ ডাটাবেস মডেলকে ডিকশনারি বা JSON ফরম্যাটে রূপান্তর করার ফাংশন
def model_to_dict(obj: Any) -> dict:
    return {c.key: getattr(obj, c.key) for c in obj.__table__.columns}

# ✅ কার্টে থাকা আইটেমগুলোর মোট দাম হিসাব করার ফাংশন
def calculate_total(items: list[dict]) -> float:
    return sum(item["price"] * item["quantity"] for item in items)

# ✅ কোনো টেক্সটকে (string) দশমিকে (float) রূপান্তর করা যায় কিনা তা চেক করা
def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False
    

# ম্যাপের অক্ষাংশ ও দ্রাঘিমাংশ (ল্যাটিচিউড-লংগিচিউড) দিয়ে দূরত্ব মাপা
from math import radians, sin, cos, sqrt, atan2

def distance_km(lat1, lon1, lat2, lon2):
    R = 6371  # পৃথিবীর ব্যাসার্ধ (কিলোমিটারে)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c