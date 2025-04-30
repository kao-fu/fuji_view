import React, { useEffect, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';

interface Point {
  lat: number;
  lon: number;
  timestamp: string;
  height?: number;
  index?: number;
  id?: string;
}

interface Props {
  path: Point[];
}

const Map: React.FC<Props> = ({ path }) => {
  const [figureUrl, setFigureUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Initialize map
    const map = L.map('map', { zoomControl: false }).setView([0, 0], 2);
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    // Add markers for each point in the path
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
      marker.on('click', async () => {
      const point = path[index];
      const popupContent = `
        <div>
        <p><strong>Latitude:</strong> ${point.lat}</p>
        <p><strong>Longitude:</strong> ${point.lon}</p>
        <p><strong>Height:</strong> ${point.height} m </p>
        <p><strong>Time:</strong> ${point.timestamp}</p>
        <p><strong>Flight idx:</strong> ${point.index}</p>
        <button id="generate-figure-btn-${index}">Generate Figure</button>
        </div>
      `;
      marker.bindPopup(popupContent).openPopup();

      // Add event listener for the "Generate Figure" button
      setTimeout(() => {
        const button = document.getElementById(`generate-figure-btn-${index}`);
        if (button) {
        button.onclick = async () => {
          setLoading(true);
          try {
          // Post to generate-figure endpoint
          await axios.post('http://localhost:8000/generate-figure', {
            start_point_longitude: point.lon,
            start_point_latitude: point.lat,
            start_point_altitude: point.height,
            start_point_index: point.index,
            start_point_flight_id: point.id
          });

          // Call the generated-figure endpoint
          const response = await axios.get('http://localhost:8000/generated-figure', {
            params: {
            flight_id: point.id,
            index: point.index,
            },
            responseType: 'blob', // Ensure the response is treated as a binary file
          });

          // Create a URL for the blob and set it as the figure URL
          const blob = new Blob([response.data], { type: 'image/png' });
          const figurePath = URL.createObjectURL(blob);
          setFigureUrl(figurePath);
          } catch (error) {
          console.error('Error generating or fetching figure:', error);
          } finally {
          setLoading(false);
          }
        };
        }
      }, 0);
      });
    });

    // Cleanup on component unmount
    return () => {
      map.remove();
    };
  }, [path]);

  return (
    <>
      <div id="map" style={{ width: '100%', height: '100%' }} />
      {loading && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000,
          }}
        >
          <div style={{ color: 'white', fontSize: '1.5rem' }}>Loading...</div>
        </div>
      )}
      {figureUrl && (
        <div
          style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000,
          }}
          onClick={() => setFigureUrl(null)}
        >
          <img
        src={figureUrl.startsWith('http') ? figureUrl : `${figureUrl}`}
        alt="Generated Figure"
        style={{ maxWidth: '90%', maxHeight: '90%' }}
          />
        </div>
      )}
    </>
  );
};

export default Map;
