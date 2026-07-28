import axios from 'axios';

const API_BASE_URL = 'https://ilshin-website.onrender.com/api';

export const authApi = {
  getCurrentUser() {
    const keys = ['user', 'userInfo', 'auth'];
    for (const key of keys) {
      const item = localStorage.getItem(key);
      if (item) {
        try {
          const parsed = JSON.parse(item);
          if (parsed && typeof parsed === 'object') {
            return parsed;
          }
        } catch {
          // JSON 파싱에 실패한 문자열일 경우 기본 객체 생성
          return { name: item, email: item };
        }
      }
    }
    return null;
  },

  async login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await axios.post(`${API_BASE_URL}/members/login`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });

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

  async updateMemberByEmail(email, updateData) {
    if (!email) {
      throw new Error('이메일 정보가 없습니다.');
    }
    const encodedEmail = encodeURIComponent(email);
    const response = await axios.put(`${API_BASE_URL}/members/${encodedEmail}`, updateData);
    return response.data;
  }
};