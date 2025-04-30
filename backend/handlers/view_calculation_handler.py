from fastapi import APIRouter, HTTPException
import numpy as np
from scipy.spatial import cKDTree
import netCDF4 as nc
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.cm import get_cmap
from pathlib import Path
from utils.pres2alt import tranform_nc_file
from param_store import get_param
import logging
from pydantic import BaseModel
from utils.calculate_view import calculate_view_image, generateFigure
from fastapi.responses import FileResponse


logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler(f"{Path(__file__).parent.parent}/log/view_calculation_handler.log")  # Log to a file
    ]
)
router = APIRouter()

class UserParams(BaseModel):
    start_point_longitude: float
    start_point_latitude: float
    start_point_altitude: float
    start_point_index: int
    start_point_flight_id: str

class UserParams2(BaseModel):
    flight_id: str
    index: int


@router.post("/generate-figure")
def generate_figure(params: UserParams):
    try:
        home_path = Path(__file__).parent.parent
        
        start_point = {"latitude": params.start_point_latitude, "longitude": params.start_point_longitude, "altitude": params.start_point_altitude}
        end_point   = {"latitude": 35.3606583, "longitude": 138.7068067, "altitude": 1500, "x": 0, "y": 0} #3776.0}
        logging.info(f"Received start point: ({start_point['longitude']}, {start_point['latitude']}, {start_point['altitude']})")

        # if image already exists, return the path
        if (home_path / "tmp" / "fig" / f"{params.start_point_flight_id}_{params.start_point_index}.png").exists():
            logging.info(f"Figure already exists: {home_path / 'tmp' / 'fig' / f'{params.start_point_flight_id}_{params.start_point_index}.png'}")
            return {"message": "Figure already exists", "output_path": str(home_path / "tmp" / "fig" / f"{params.start_point_flight_id}_{params.start_point_index}.png")}
        else:
            topoImage, cloudImage = calculate_view_image(start_point, end_point,
                                                         model_path=home_path / "tmp" / "nc" / "20250409_170000_alt.nc",)
            generateFigure(topoImage, cloudImage, output_path=home_path / "tmp" / "fig" / f"{params.start_point_flight_id}_{params.start_point_index}.png")
            logging.info(f"Figure generated successfully: {home_path / 'tmp' / 'fig' / f'{params.start_point_flight_id}_{params.start_point_index}.png'}")
            return {"message": "Figure generated successfully", "output_path": str(home_path / "tmp" / "fig" / f"{params.start_point_flight_id}_{params.start_point_index}.png")}
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Error generating figure: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generated-figure")
def get_generated_figure(flight_id: str, index: int):
    try:
        home_path = Path(__file__).parent.parent
        figure_path = home_path / "tmp" / "fig" / f"{flight_id}_{index}.png"
        if not figure_path.exists():
            logging.error(f"Figure not found: {figure_path}")
            raise HTTPException(status_code=404, detail="Figure not found")
        
        logging.info(f"Serving figure: {figure_path}")
        return FileResponse(figure_path, media_type="image/png")
    except Exception as e:
        logging.error(f"Error serving figure: {e}")
        raise HTTPException(status_code=500, detail=str(e))
