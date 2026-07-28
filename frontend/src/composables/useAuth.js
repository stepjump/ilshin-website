// frontend/src/composables/useAuth.js
import { ref, computed } from 'vue';
import axios from 'axios';
import { authApi } from '../api/auth';

const API_BASE_URL = 'https://ilshin-website.onrender.com/api';
const currentUser = ref(authApi.getCurrentUser());

export function useAuth() {
  const isLoggedIn = computed(() => !!currentUser.value);

  const login = async (email, password) => {
    const data = await authApi.login(email, password);
    // 로그인 시 반환된 전체 유저 정보를 currentUser에 반영
    currentUser.value = authApi.getCurrentUser();
    return data;
  };

  const logout = () => {
    authApi.logout();
    currentUser.value = null;
  };

  const updateUserInfo = async (updatedData) => {
    try {
      const email = currentUser.value?.email || updatedData.email;
      if (!email) {
        throw new Error('이메일 정보가 존재하지 않습니다.');
      }

      let updatedMember = null;

      if (authApi && typeof authApi.updateMemberByEmail === 'function') {
        updatedMember = await authApi.updateMemberByEmail(email, updatedData);
      } else {
        const encodedEmail = encodeURIComponent(email);
        const response = await axios.put(`${API_BASE_URL}/members/${encodedEmail}`, updatedData);
        updatedMember = response.data;
      }

      // 수정 후 기존 토큰 정보 등은 유지하면서 수정한 프로필 데이터 갱신
      currentUser.value = {
        ...currentUser.value,
        ...updatedMember
      };
      localStorage.setItem('user', JSON.stringify(currentUser.value));

      return { success: true, data: updatedMember };
    } catch (error) {
      console.error('회원정보 변경 실패:', error);
      return { 
        success: false, 
        message: error.response?.data?.detail || error.message 
      };
    }
  };

  return {
    currentUser,
    isLoggedIn,
    login,
    logout,
    updateUserInfo,
  };
}