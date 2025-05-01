import numpy as np
import netCDF4 as nc
import xarray as xr
from pathlib import Path
from datetime import datetime, timedelta
from scipy.interpolate import interp1d
import sys
sys.path.append("..")
from param_store import get_param


def pres2alt(p_variable, varHeight, height_coord, topo):
    ny, nx = p_variable.shape[1], p_variable.shape[2]
    z_variable = np.zeros((len(height_coord), ny, nx))
    for iy in range(ny):
        for ix in range(nx):
            f = interp1d(varHeight[:, iy, ix], p_variable[:, iy, ix], 
                         axis=0, fill_value=get_param("modelParameter.invalidValue"), bounds_error=False)
            z_variable[:, iy, ix] = f(height_coord)
            z_variable[:, iy, ix][height_coord < topo[iy, ix]] = get_param("modelParameter.invalidValue")
    return z_variable

def tranform_nc_file(input_path, output_path):
    nc_data = nc.Dataset(input_path)
    pressure = np.array(get_param("modelParameter.pressureCoordinateInhPa"))
    npressure = len(pressure)
    nx, ny = len(nc_data["x"]), len(nc_data["y"])
    topo = np.array(nc_data["HGT_surface"][0])
    height_coord = np.arange(0, 12001, int(get_param("modelParameter.altitudeResolutionInMeter")))
    
    considerVariable = np.array(["HGT"] + get_param("modelParameter.considerVariable"))
    considerVariableSet = np.zeros(shape=(len(considerVariable), npressure, ny, nx))
    outputVariableSet = np.zeros(shape=(len(considerVariable), len(height_coord), ny, nx))
    for i in range(npressure):
        for j in range(len(considerVariable)):
            considerVariableSet[j][i] = nc_data[f"{considerVariable[j]}_{pressure[i]}mb"][0]
    for j in range(1, len(considerVariable)):
        outputVariableSet[j] = pres2alt(considerVariableSet[j], considerVariableSet[0], height_coord, topo)
    # write to netcdf file
    with xr.Dataset() as ds:
        for j in range(1, len(considerVariable)):
            ds[f"{considerVariable[j]}"] = (("height", "y", "x"), outputVariableSet[j])
        ds["topo"] = (("y", "x"), topo)
        ds["latitude"] = (("y", "x"), np.array(nc_data["latitude"]))
        ds["longitude"] = (("y", "x"), np.array(nc_data["longitude"]))
        ds["height"] = height_coord
        ds["x"] = np.array(nc_data["x"])
        ds["y"] = np.array(nc_data["y"])
        ds.to_netcdf(output_path)


if __name__ == "__main__":
    home_path = Path(__file__).parent.parent
    #try:
    #    year  = get_param("modelParameter.year")
    #    month = get_param("modelParameter.month")
    #    day   = get_param("modelParameter.day")
    #    hour  = get_param("modelParameter.hour")
    #except Exception as e:
    #    sys.exit(1)
    # run from 2025-04-01 00:00:00 to 2025-04-04 00:00:00
    start_time = datetime(2025, 4, 9, 0, 0, 0)
    end_time = datetime(2025, 4, 11, 0, 0, 0)
    current_time = start_time

    while current_time <= end_time:
        print(current_time)
        year = current_time.year
        month = current_time.month
        day = current_time.day
        hour = current_time.hour

        file_date = f"{year:04d}{month:02d}{day:02d}_{hour:02d}0000"
        input_path = home_path / "data" / "own" / f"{file_date}.nc"
        output_path = home_path / "tmp" / "nc" / f"{file_date}_alt.nc"

        if not input_path.exists():
            current_time += timedelta(hours=1)
            continue
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            current_time += timedelta(hours=1)
            continue

        tranform_nc_file(input_path, output_path)
        current_time += timedelta(hours=1)