// frontend/src/api/auth.js
import axios from 'axios';

// Render에 배포된 백엔드 API URL
const API_BASE_URL = 'https://ilshin-website.onrender.com/api';

export const authApi = {
  // 현재 로그인된 유저 가져오기
  getCurrentUser() {
    const keys = ['user', 'userInfo', 'auth'];
    for (const key of keys) {
      const item = localStorage.getItem(key);
      if (item) {
        try {
          return JSON.parse(item);
        } catch {
          return { username: item, name: item };
        }
      }
    }
    return null;
  },

  // 로그인 API
  async login(email, password) {
    const response = await axios.post(`${API_BASE_URL}/login`, { email, password });
    if (response.data) {
      localStorage.setItem('user', JSON.stringify(response.data));
    }
    return response.data;
  },

  // 로그아웃
  logout() {
    localStorage.removeItem('user');
    localStorage.removeItem('userInfo');
    localStorage.removeItem('auth');
    localStorage.removeItem('token');
  },

  // ★ member.py의 @router.put("/{member_id}") 호출
  async updateMember(memberId, updateData) {
    // member_id가 없거나 'admin' 등 스트링인 경우 기본 ID 처리
    const id = memberId || 1;
    
    // endpoint 경로 시도 (/api/members/{id} 또는 /api/users/{id})
    try {
      const response = await axios.put(`${API_BASE_URL}/members/${id}`, updateData);
      return response.data;
    } catch (err) {
      // /api/members/ 경로가 실패할 경우 /api/users/ 로 폴백 시도
      console.warn('/api/members PUT 실패, /api/users 경로 시도:', err);
      const response = await axios.put(`${API_BASE_URL}/users/${id}`, updateData);
      return response.data;
    }
  }
};