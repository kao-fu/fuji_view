from fastapi import APIRouter
import pandas as pd
import os

router = APIRouter()

@router.get("/flight/{flight_id}")
def get_flight_path(flight_id: str):
    file_path = "data/aircraft/2025-04-09.csv"
    if not os.path.exists(file_path):
        return {"found": False, "message": "Flight data not found"}
    columnNames = ["index", "time", "id", "longitude", "latitude", "height", "temperature", "airplane_type", "wind_speed", "wind_direction", "wind_u", "wind_v"]
    df = pd.read_csv(file_path, skiprows=1, names=columnNames, header=None)
    # drop row with nans included
    df = df.dropna()
    filtered = df[df["id"] == flight_id]
    if filtered.empty:
        return {"found": False}

    coords = filtered[["latitude", "longitude", "time"]].to_dict(orient="records")
    return {"found": True, "path": coords}
