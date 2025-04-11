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
    const map = L.map('map').setView([0, 0], 2);

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    // Add markers for each point in the path
    const markers: L.Marker[] = [];
    path.forEach(point => {
      const marker = L.marker([point.lat, point.lon]).addTo(map);
      markers.push(marker);
    });

    // Adjust map bounds to fit all points
    if (path.length > 0) {
      const bounds = L.latLngBounds(path.map(point => [point.lat, point.lon]));
      map.fitBounds(bounds);
    }

    // Cleanup on component unmount
    return () => {
      map.remove();
    };
  }, [path]);

  return <div id="map" style={{ width: '100%', height: '100%' }} />;
};

export default Map;
