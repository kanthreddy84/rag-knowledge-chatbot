// Auto-detect backend API URL based on hostname
export const getApiUrl = () => {
  const hostname = window.location.hostname;
  const apiUrl = (hostname === 'localhost' || hostname === '127.0.0.1')
    ? 'http://localhost:8000'
    : 'https://rag-knowledge-chatbot.onrender.com';

  console.log(`[API Config] Hostname: ${hostname}, API URL: ${apiUrl}`);
  return apiUrl;
};
