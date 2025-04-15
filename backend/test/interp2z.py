import numpy as np
import netCDF4 as nc
import xarray as xr
from scipy.interpolate import interp1d

def p2z(p_variable, varHeight, height_coord, topo):
    ny, nx = p_variable.shape[1], p_variable.shape[2]
    z_variable = np.zeros((len(height_coord), ny, nx))
    for iy in range(ny):
        for ix in range(nx):
            f = interp1d(varHeight[:, iy, ix], p_variable[:, iy, ix], axis=0, fill_value=-999.99, bounds_error=False)
            z_variable[:, iy, ix] = f(height_coord)
            z_variable[:, iy, ix][height_coord < topo[iy, ix]] = -999.99
    return z_variable

if __name__ == "__main__":
    data = nc.Dataset("../data/own/20250409_170000.nc")
    pressure = np.array([1000, 975, 950, 925, 900, 875, 850, 800, 750, 700, 650, 600, 550, 500, 400, 300, 200])
    npressure = len(pressure)
    height_coord = np.arange(0, 12000, 500)
    nx, ny = len(data["x"]), len(data["y"])
    latitude = np.array(data["latitude"])
    longitude = np.array(data["longitude"])
    topo = np.array(data["HGT_surface"][0])
    HGT = np.zeros(shape=(npressure, ny, nx))
    CLMR = np.zeros(shape=(npressure, ny, nx))
    ICMR = np.zeros(shape=(npressure, ny, nx))
    RWMR = np.zeros(shape=(npressure, ny, nx))
    SNMR = np.zeros(shape=(npressure, ny, nx))
    GRLE = np.zeros(shape=(npressure, ny, nx))
    for i in range(len(pressure)):
        HGT[i]  = data[f"HGT_{pressure[i]}mb"][0]
        CLMR[i] = data[f"CLMR_{pressure[i]}mb"][0]
        ICMR[i] = data[f"ICMR_{pressure[i]}mb"][0]
        RWMR[i] = data[f"RWMR_{pressure[i]}mb"][0]
        SNMR[i] = data[f"SNMR_{pressure[i]}mb"][0]
        GRLE[i] = data[f"GRLE_{pressure[i]}mb"][0]

    zCLMR = p2z(CLMR, HGT, height_coord, topo)
    zICMR = p2z(ICMR, HGT, height_coord, topo)
    zRWMR = p2z(RWMR, HGT, height_coord, topo)
    zSNMR = p2z(SNMR, HGT, height_coord, topo)
    zGRLE = p2z(GRLE, HGT, height_coord, topo)

    # write zCLMR to netcdf file
    output_file = "zMcPhy.nc"
    with xr.Dataset() as ds:
        ds["zCLMR"] = (("height", "y", "x"), zCLMR)
        ds["zICMR"] = (("height", "y", "x"), zICMR)
        ds["zRWMR"] = (("height", "y", "x"), zRWMR)
        ds["zSNMR"] = (("height", "y", "x"), zSNMR)
        ds["zGRLE"] = (("height", "y", "x"), zGRLE)
        ds["topo"] = (("y", "x"), topo)
        ds["latitude"] = (("y", "x"), latitude)
        ds["longitude"] = (("y", "x"), longitude)
        ds["height"] = height_coord
        ds["x"] = np.array(data["x"])
        ds["y"] = np.array(data["y"])
        ds.to_netcdf(output_file)