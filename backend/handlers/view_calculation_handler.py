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

@router.post("/generate_figure")
def generate_weather_data(params: UserParams):
    try:
        home_path = Path(__file__).parent.parent
        start_point_longitude = params.start_point_longitude
        start_point_latitude = params.start_point_latitude
        logging.info(f"Received start point: ({start_point_longitude}, {start_point_latitude})")

    topoImage, cloudImage = calculate_view_image(start_point_longitude, start_point_latitude)
    generateFigure(topoImage, cloudImage, output_path=home_path / "tmp" / "figure.png")

#        file_date = f"{year:04d}{month:02d}{day:02d}_{hour:02d}0000"
#        input_path = home_path / "data" / "own" / f"{file_date}.nc"
#        output_path = home_path / "tmp" / "nc" / f"{file_date}_alt.nc"
#
#        if not input_path.exists():
#            logging.error(f"Input file {input_path} does not exist.")
#            raise HTTPException(status_code=404, detail=f"Input file {input_path} does not exist.")
#        if not output_path.parent.exists():
#            logging.info(f"Creating output directory: {output_path.parent}")
#            output_path.parent.mkdir(parents=True, exist_ok=True)
#        if output_path.exists():
#            logging.info(f"Weather data already generated: {output_path}")
#            return {"message": "Weather data already generated", "output_path": str(output_path)}
#
#        tranform_nc_file(input_path, output_path)
#        logging.info(f"Weather data generated successfully: {output_path}")
#        return {"message": "Weather data generated successfully", "output_path": str(output_path)}
#
#    except Exception as e:
#        raise HTTPException(status_code=500, detail=str(e))
