import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc
import cartopy.crs as ccrs
import cartopy.feature as cfeature

#for d in range(0, 6): 
for d in range(12, 18): 
    data = nc.Dataset(f"../data/own/20250409_{d:02d}0000.nc")
    pressure = np.array([1000, 975, 950, 925, 900, 875, 850, 800, 750, 700, 650, 600, 550, 500, 400, 300, 200])
    x, y = data["x"], data["y"]
    nx, ny = len(x), len(y)
    npressure = len(pressure)
    lat, lon = data["latitude"], data["longitude"]
    HGT = np.zeros(shape=(npressure, ny, nx))
    CLMR = np.zeros(shape=(npressure, ny, nx))
    for i in range(len(pressure)):
        HGT[i]  = data[f"HGT_{pressure[i]}mb"][0]
        CLMR[i] = data[f"CLMR_{pressure[i]}mb"][0]
    fig = plt.figure(figsize=(10, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())  # Assuming data is in lat/lon

    # Plot cloud presence
    cloud_mask = (np.sum(CLMR, axis=0) != 0)
    mesh = ax.pcolormesh(lon, lat, cloud_mask, transform=ccrs.PlateCarree())

    # Add borders and coastlines
    ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='white')
    ax.add_feature(cfeature.COASTLINE, edgecolor='white')

    # Add colorbar
    plt.colorbar(mesh, ax=ax, orientation='vertical', label='Cloud Presence')
    plt.scatter(138.7068067,35.3606583, c="red")
    plt.ylim(34.5, 36.5)
    plt.xlim(137, 141)
    # Save and clear
    plt.savefig(f"cloud{d:02d}.jpg", dpi=300)
    plt.clf()
 
