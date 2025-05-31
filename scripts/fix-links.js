const axios = require('axios');

async function fixLinks() {
  try {
    const response = await axios.post('http://localhost:3000/api/events/fix-links');
    console.log('Success:', response.data);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

fixLinks(); 