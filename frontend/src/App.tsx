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
    console.log(data);

    if (data.found) {
      const validPath = data.path.filter(
        (point: Point) => point.lat !== undefined && point.lon !== undefined
      );
      setPath(validPath);
    } else {
      alert('Flight not found');
      setPath([]);
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '1rem', backgroundColor: '#f0f0f0' }}>
        <input
          type="text"
          value={flightId}
          onChange={e => setFlightId(e.target.value)}
          placeholder="Enter Flight ID"
          style={{ marginRight: '0.5rem' }}
        />
        <button onClick={handleSearch}>Search</button>
      </div>
      <div style={{ flex: 1 }}>
        <Map path={path} />
      </div>
    </div>
  );
}

export default App;
