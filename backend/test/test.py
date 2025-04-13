import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc

data = nc.Dataset("../data/own/20250409_020000.nc")
pressure = np.array([1000, 975, 950, 925, 900, 875, 850, 800, 750, 700, 650, 600, 550, 500, 400, 300, 200])
nx, ny = len(data["x"]), len(data["y"])
npressure = len(pressure)
HGT = np.zeros(shape=(npressure, ny, nx))
TMP = np.zeros(shape=(npressure, ny, nx))
UGRD = np.zeros(shape=(npressure, ny, nx))
VGRD = np.zeros(shape=(npressure, ny, nx))
CLMR = np.zeros(shape=(npressure, ny, nx))
ICMR = np.zeros(shape=(npressure, ny, nx))
RWMR = np.zeros(shape=(npressure, ny, nx))
SNMR = np.zeros(shape=(npressure, ny, nx))
GRLE = np.zeros(shape=(npressure, ny, nx))
for i in range(len(pressure)):
    HGT[i]  = data[f"HGT_{pressure[i]}mb"][0]
    TMP[i]  = data[f"TMP_{pressure[i]}mb"][0]
    UGRD[i] = data[f"UGRD_{pressure[i]}mb"][0]
    VGRD[i] = data[f"VGRD_{pressure[i]}mb"][0]
    CLMR[i] = data[f"CLMR_{pressure[i]}mb"][0]
    ICMR[i] = data[f"ICMR_{pressure[i]}mb"][0]
    RWMR[i] = data[f"RWMR_{pressure[i]}mb"][0]
    SNMR[i] = data[f"SNMR_{pressure[i]}mb"][0]
    GRLE[i] = data[f"GRLE_{pressure[i]}mb"][0]
