import axios from 'axios';

interface UserParams {
    year: number;
    month: number;
    day: number;
    hour: number;
  }
  
  export const generateTmpModelData = async (params: UserParams) => {
    try {
      const res = await axios.post('http://localhost:8000/generate-tmp-model-data', params);
      if (res.status !== 200) {
        throw new Error('Failed to generate temporary model data');
      }
      return res.data;
    } catch (error) {
      console.error('Error generating temporary model data:', error);
      throw error;
    }
  };