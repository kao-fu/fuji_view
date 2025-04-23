import React, { useEffect } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface Point {
  lat: number;
  lon: number;
  timestamp: string;
}

interface Props {
  path: Point[];
}

const Map: React.FC<Props> = ({ path }) => {
  useEffect(() => {
    // Initialize map
    const map = L.map('map', { zoomControl: false }).setView([0, 0], 2);
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    // Add markers for each point in the path
    console.log('Path:', path);
    const markers: L.Marker[] = [];
    const bounds = L.latLngBounds([]);
    path.forEach(point => {
      const marker = L.marker([point.lat, point.lon]).addTo(map);
      markers.push(marker);
      bounds.extend(marker.getLatLng());
    });
    // Add a red line connecting points
    if (path.length > 1) {
      const latLngs = path.map(point => [point.lat, point.lon] as [number, number]);
      L.polyline(latLngs, { color: 'red' }).addTo(map);
    }

    // Adjust map bounds to fit all points
    if (path.length > 0) {
      map.fitBounds(bounds, { padding: [20, 20] });
    }

    // Add click event to markers to display information
    markers.forEach((marker, index) => {
      marker.on('click', () => {
      const point = path[index];
      console.log(point);
      const popupContent = `
        <div>
        <p><strong>Latitude:</strong> ${point.lat}</p>
        <p><strong>Longitude:</strong> ${point.lon}</p>
        <p><strong>Height:</strong> ${point.height} m </p>
        <p><strong>Time:</strong> ${point.timestamp}</p>
        <button id="generate-figure-btn">Generate Figure</button>
        </div>
      `;
      marker.bindPopup(popupContent).openPopup();
      });
    });

    // Cleanup on component unmount
    return () => {
      map.remove();
    };
  }, [path]);

  return <div id="map" style={{ width: '100%', height: '100%' }} />;
};

export default Map;
