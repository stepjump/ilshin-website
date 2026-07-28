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
    const response = await axios.post(`${API_BASE_URL}/members/login`, { email, password });
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

  // ★ member.py의 PUT /api/members/{email} 직접 호출
  async updateMemberByEmail(email, updateData) {
    if (!email) {
      throw new Error('이메일 정보가 없습니다.');
    }
    const encodedEmail = encodeURIComponent(email);
    const response = await axios.put(`${API_BASE_URL}/members/${encodedEmail}`, updateData);
    return response.data;
  }
};