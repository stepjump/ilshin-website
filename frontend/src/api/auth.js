// 회원가입 / 로그인 API 모듈
// FastAPI의 OAuth2 규격(x-www-form-urlencoded)에 맞게 로그인 요청 데이터를 처리해주는 모듈

import api from './index';

export const authApi = {
  // 로그인 (FastAPI OAuth2 폼 데이터 전송)
  async login(email, password) {
    const params = new URLSearchParams();
    params.append('username', email); // FastAPI OAuth2는 'username' 필드명 사용
    params.append('password', password);

    const response = await api.post('/api/members/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    // 로그인 성공 시 토큰 및 회원 정보 저장
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user_info', JSON.stringify({
        email: response.data.email,
        name: response.data.name,
        role: response.data.role,
      }));
    }

    return response.data;
  },

  // 로그아웃
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
  },

  // 회원가입
  createMember(memberData) {
    return api.post('/api/members', memberData);
  },

  // 로컬스토리지 저장 유저 정보 가져오기 헬퍼
  getCurrentUser() {
    const user = localStorage.getItem('user_info');
    return user ? JSON.parse(user) : null;
  }
};




