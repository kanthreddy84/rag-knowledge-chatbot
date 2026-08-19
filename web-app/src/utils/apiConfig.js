// Auto-detect backend API URL based on environment
export const getApiUrl = () => {
  // If on localhost, use local backend
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }

  // If on Vercel or any other hostname, use production Render backend
  return 'https://rag-knowledge-chatbot.onrender.com';
};
