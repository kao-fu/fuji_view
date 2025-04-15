import numpy as np
import netCDF4 as nc
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


if __name__ == "__main__":
    data = nc.Dataset("./zMcPhy.nc")
    lon, lat = data["longitude"], data["latitude"]
    cloud = np.array(data["zCLMR"])
    height = np.array(data["topo"])
    cloud[cloud == -999.99] = np.nan  # Set fill value to NaN
    print(np.sum(cloud[6] > 1e-3))
    
    fig = plt.figure(figsize=(10, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())  # Assuming data is in lat/lon
    # Plot cloud presence
    mesh = ax.pcolormesh(lon, lat, height, transform=ccrs.PlateCarree(), shading='auto')
    # Add borders and coastlines
    ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='white')
    ax.add_feature(cfeature.COASTLINE, edgecolor='white')
    # Add longitude and latitude gridlines
    gl = ax.gridlines(draw_labels=True, linestyle='--', color='gray', alpha=0.7)
    gl.top_labels = False
    gl.right_labels = False
    # Add colorbar
    plt.colorbar(mesh, ax=ax, orientation='vertical', label='Cloud')
    plt.scatter(138.7068067, 35.3606583, c="red")
    plt.scatter(139.1999969482422, 34.72833251953125, c="blue")
    plt.ylim(34.0, 37.0)
    plt.xlim(137, 141)
    # Save and clear
    plt.savefig(f"topo_a.jpg", dpi=300)
    plt.clf()
