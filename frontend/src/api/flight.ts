import axios from 'axios';

export const fetchFlightPath = async (flightId: string) => {
  const res = await axios.get(`http://localhost:8000/flight/${flightId}`);
    if (res.status !== 200) {
        throw new Error('Failed to fetch flight path');
    }
    if (res.data.found === false) {
        throw new Error('Flight not found');
    }
  return res.data;
};