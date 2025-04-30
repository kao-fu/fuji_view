import numpy as np
import netCDF4 as nc
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.cm import get_cmap
#import cartopy.crs as ccrs
#import cartopy.feature as cfeature
from scipy.spatial import cKDTree
import pygrib
def verbose_info(filepath):
    print(filepath)
    with pygrib.open(filepath) as grbs:
        for i, grb in enumerate(grbs):
            print(f"--- Message {i+1} ---")
            print(f"Description             : {grb}")
            print(f"name                    : {grb.name}")
            print(f"Parameter               : {grb.parameterName}")
            print(f"Short name              : {grb.shortName}")
            print(f"Units                   : {grb.units}")
            print(f"Level type              : {grb.typeOfLevel}")
            print(f"Level                   : {grb.level}")
            print(f"Base date               : {grb.analDate}")
            print(f"Valid date              : {grb.validDate}")
            print(f"Forecast time (hours)   : {grb.forecastTime}")
            print(f"Maximum: {grb.values.max()}")
            print(f"Minimum: {grb.values.min()}")

            # ピクセル数
            print(f"Grid points (Ni x Nj)   : {grb.Ni} x {grb.Nj}")
                    
            # 緯度経度
            lats, lons = grb.latlons()
            lat_min, lat_max = lats.min(), lats.max()
            lon_min, lon_max = lons.min(), lons.max()
            print(f"Latitude range          : {lat_min:.3f} to {lat_max:.3f}")
            print(f"Longitude range         : {lon_min:.3f} to {lon_max:.3f}")

            # 解像度
            if grb.jDirectionIncrementInDegrees and grb.iDirectionIncrementInDegrees:
                print(f"Lat resolution          : {grb.jDirectionIncrementInDegrees} degrees")
                print(f"Lon resolution          : {grb.iDirectionIncrementInDegrees} degrees")
            else:
                if lats.shape[0] > 1 and lons.shape[1] > 1:
                    dlat = abs(lats[1,0] - lats[0,0])
                    dlon = abs(lons[0,1] - lons[0,0])
                    
                    print(f"Lon resolution (estimated): {dlon:.3f} degrees")
                    print(f"Lat resolution (estimated): {dlat:.3f} degrees")
            print("")
#with pygrib.open("../data/test/20250424012244.WNI_ANLSIS_JP_1KM_full") as grbs:
#    for grb in grbs:
#        print(grb)
verbose_info("../data/test/20250424002308.WNI_KAKUHO_COMPAS_PRCRIN_1KM")