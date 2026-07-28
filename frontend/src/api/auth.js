// frontend/src/api/auth.js
import axios from 'axios';

const API_BASE_URL = 'https://ilshin-website.onrender.com/api';

export const authApi = {
  getCurrentUser() {
    const keys = ['user', 'userInfo', 'auth'];
    for (const key of keys) {
      const item = localStorage.getItem(key);
      if (item) {
        try {
          return JSON.parse(item);
        } catch {
          return { username: item, email: item };
        }
      }
    }
    return null;
  },

  async login(email, password) {
    const response = await axios.post(`${API_BASE_URL}/login`, { email, password });
    if (response.data) {
      localStorage.setItem('user', JSON.stringify(response.data));
    }
    return response.data;
  },

  logout() {
    localStorage.removeItem('user');
    localStorage.removeItem('userInfo');
    localStorage.removeItem('auth');
    localStorage.removeItem('token');
  },

  // ★ member 테이블의 email 컬럼을 Key로 수정 API 호출
  async updateMemberByEmail(email, updateData) {
    if (!email) {
      throw new Error('수정할 회원의 이메일 정보가 없습니다.');
    }

    const encodedEmail = encodeURIComponent(email);

    try {
      // /api/members/{email} 엔드포인트 호출
      const response = await axios.put(`${API_BASE_URL}/members/${encodedEmail}`, updateData);
      return response.data;
    } catch (err) {
      console.warn('/api/members/{email} PUT 실패, /api/users/{email} 경로로 재시도합니다:', err);
      // 폴백 경로 시도
      const response = await axios.put(`${API_BASE_URL}/users/${encodedEmail}`, updateData);
      return response.data;
    }
  }
};