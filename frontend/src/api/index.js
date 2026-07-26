// Axios 공통 클라이언트
import axios from 'axios';

// 1. Axios 인스턴스 생성
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 2. Request Interceptor: 요청 시 토큰 자동 첨부
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 3. Response Interceptor: 401(토큰 만료) 시 자동 로그아웃 처리
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      
      // 로그인 화면이 아닐 때만 이동
      if (window.location.pathname !== '/login') {
        alert('세션이 만료되었습니다. 다시 로그인해 주세요.');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
