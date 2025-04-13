import { useState } from 'react';
import Map from './components/Map';
import { fetchFlightPath } from './api/flight';

interface Point {
  lat: number;
  lon: number;
  timestamp: string;
}

function App() {
  const [flightId, setFlightId] = useState('');
  const [path, setPath] = useState<Point[]>([]);

  const handleSearch = async () => {
    const data = await fetchFlightPath(flightId);

    if (data.found) {
      const validPath = data.path.map((point: { latitude: number; longitude: number; time: string; index: number }, index: number) => ({
        lat: point.latitude,
        lon: point.longitude,
        timestamp: point.time,
        index: index, // Add index for secondary sorting
      }));

      validPath.sort((a, b) => {
        const timeComparison = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
        return timeComparison !== 0 ? timeComparison : a.index - b.index;
      });

      setPath(validPath);
    } else {
      alert('Flight not found');
      setPath([]);
    }
  };

  return (
    <div style={{ height: '100vh', width: '100vw', position: 'relative' }}>
      {/* Map fills the entire viewport */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }}>
        <Map path={path} />
      </div>
      
      <div style={{ 
        position: 'absolute', 
        top: 0, 
        left: 0, 
        width: '100%',
        padding: '1rem', 
        backgroundColor: 'rgba(240, 240, 240, 0.8)', 
        zIndex: 1000 
      }}>
        <input
          type="text"
          value={flightId}
          onChange={e => setFlightId(e.target.value)}
          placeholder="Enter Flight ID"
          style={{ marginRight: '0.5rem' }}
        />
        <button onClick={handleSearch}>Search</button>
      </div>
    </div>
  );
}

export default App;
