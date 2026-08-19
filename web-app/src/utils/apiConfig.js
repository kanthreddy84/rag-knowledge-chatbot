// Auto-detect backend API URL based on hostname
export const getApiUrl = () => {
  const hostname = window.location.hostname;

  // If on localhost, use local backend
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }

  // For all other domains (Vercel, etc), use production backend
  return 'https://rag-knowledge-chatbot.onrender.com';
};
