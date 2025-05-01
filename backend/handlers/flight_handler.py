from fastapi import APIRouter, HTTPException
import pandas as pd
import os

router = APIRouter()

@router.get("/flight/{date}_{flight_id}")
def get_flight_path(flight_id: str, date: str):
    file_path = f"data/aircraft/{date}.csv"
    if not os.path.exists(file_path):
        return {"found": False, "message": "Flight data not found"}
    columnNames = ["index", "time", "id", "longitude", "latitude", "height", "temperature", "airplane_type", "wind_speed", "wind_direction", "wind_u", "wind_v"]
    df = pd.read_csv(file_path, skiprows=1, names=columnNames, header=None)
    # drop row with nans included
    df = df.dropna()
    filtered = df[df["id"] == flight_id]
    if filtered.empty:
        return {"found": False}
    filtered["id"] = flight_id
    filtered["date"] = date
    coords = filtered[["id", "latitude", "longitude", "height", "time", "index", "date"]].to_dict(orient="records")
    return {"found": True, "path": coords}

@router.get("/flight-ids/{date}")
def get_flight_ids(date: str):
    file_path = f"data/aircraft/{date}.csv"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Flight data not found")

    column_names = ["index", "time", "id", "longitude", "latitude", "height", "temperature", "airplane_type", "wind_speed", "wind_direction", "wind_u", "wind_v"]
    df = pd.read_csv(file_path, skiprows=1, names=column_names, header=None)
    df = df.dropna()

    unique_ids = df["id"].unique().tolist()
    return {"flight_ids": unique_ids}
