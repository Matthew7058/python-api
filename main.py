from fastapi import FastAPI, Query
from uk_fuel_prices_api import UKFuelPricesApi
import math


app = FastAPI()
api = UKFuelPricesApi()


@app.on_event("startup")
async def get_prices():
    data = await api.get_prices()


@app.get("/")
async def root():
    """Root endpoint to show API is running"""
    return {
        "status": "running",
        "endpoints": {
            "get_prices": "/get_prices",
            "search": "/search?query={query}&limit={limit}",
            "site": "/site/{site_id}",
            "stations-within-radius": "/stations-within-radius?lat={lat}&lng={lng}&radius={radius}"
        }
    }


@app.get("/get_prices")
async def get_prices():
    data = await api.get_prices()
    return {"data": data}


# In your FastAPI endpoint:
@app.get("/search")
def search_stations(query: str, limit: int | None = None):
    data = api.search(query, limit)   # returns a structure containing Infinity/NaN
    data_cleaned = fix_out_of_range_floats(data)
    return {"data": data_cleaned}


# 2) Get station by site ID
@app.get("/site/{site_id}")
async def get_station_by_site_id(site_id: str):
    """
    Returns the station data for a single station by site_id.
    """
    station = api.get_station(site_id)  # if it's truly async
    return {"station": station}


@app.get("/stations-within-radius")
def get_stations_within_radius(
    lat: float = Query(...),
    lng: float = Query(...),
    radius: float = Query(..., description="Radius in km"),
):
    """
    Returns all fuel stations within the given radius (in km)
    of the specified lat/lng point.
    """
    stations = api.stationsWithinRadius(lat, lng, radius)
    return {"stations": stations}


def fix_out_of_range_floats(obj):
    """
    Recursively convert any float('inf'), float('-inf'), or float('nan')
    to None, making the data JSON-friendly.
    """
    if isinstance(obj, float):
        if math.isinf(obj) or math.isnan(obj):
            return None  # or "Infinity" if you prefer a string
        return obj
    elif isinstance(obj, dict):
        return {k: fix_out_of_range_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [fix_out_of_range_floats(v) for v in obj]
    return obj
