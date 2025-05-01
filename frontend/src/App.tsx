import { useState, useEffect } from 'react';
import Map from './components/Map';
import { fetchFlightPath } from './api/flight';
import axios from 'axios';

interface Point {
  lat: number;
  lon: number;
  timestamp: string;
}

function App() {
  const [flightId, setFlightId] = useState('');
  const [date, setDate] = useState('2025-04-09'); // Default date
  const [path, setPath] = useState<Point[]>([]);
  const [flightIds, setFlightIds] = useState<string[]>([]);

  useEffect(() => {
    const fetchFlightIds = async () => {
      try {
        const res = await axios.get(`http://localhost:8000/flight-ids/${date}`);
        setFlightIds(res.data.flight_ids);
        setFlightId(''); // Reset flight ID when date changes
      } catch (error) {
        console.error('Error fetching flight IDs:', error);
        setFlightIds([]);
      }
    };

    fetchFlightIds();
  }, [date]);

  const handleSearch = async () => {
    const data = await fetchFlightPath(flightId, date);
    console.log(data);
    if (data.found) {
      const validPath = data.path.map((point: { latitude: number; longitude: number; height: number; time: string; index: number; id: string; date: string }, index: number) => ({
        lat:       point.latitude,
        lon:       point.longitude,
        timestamp: point.time,
        height:    point.height, // Uncomment if height is needed
        index:     index,        // Add index for secondary sorting
        id:        point.id,
        date:      point.date
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
        <select
          value={date}
          onChange={e => setDate(e.target.value)}
          style={{ marginRight: '0.5rem' }}
        >
          <option value="2025-04-01">2025-04-01</option>
          <option value="2025-04-02">2025-04-02</option>
          <option value="2025-04-03">2025-04-03</option>
          <option value="2025-04-09">2025-04-09</option>
          <option value="2025-04-10">2025-04-10</option>
          <option value="2025-04-11">2025-04-11</option>
          <option value="2025-12-31">2025-12-31</option>
        </select>
        <select
          value={flightId}
          onChange={e => setFlightId(e.target.value)}
          style={{ marginRight: '0.5rem' }}
        >
          <option value="" disabled>Select Flight ID</option>
          {flightIds.map(id => (
            <option key={id} value={id}>{id}</option>
          ))}
        </select>
        <button onClick={handleSearch} disabled={!flightId}>Search</button>
      </div>
    </div>
  );
}

export default App;
