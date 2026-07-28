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
    currentUser.value = authApi.getCurrentUser();
    return data;
  };

  const logout = () => {
    authApi.logout();
    currentUser.value = null;
  };

  // ★ 회원정보 변경 기능
  const updateUserInfo = async (updatedData) => {
    try {
      const email = currentUser.value?.email || updatedData.email;
      if (!email) {
        throw new Error('이메일 정보가 존재하지 않습니다.');
      }

      let updatedMember = null;

      // 1. authApi 객체의 updateMemberByEmail 호출 시도
      if (authApi && typeof authApi.updateMemberByEmail === 'function') {
        updatedMember = await authApi.updateMemberByEmail(email, updatedData);
      } else {
        // 2. 메서드가 없을 경우 직접 axios로 /api/members/{email} PUT 호출
        const encodedEmail = encodeURIComponent(email);
        const response = await axios.put(`${API_BASE_URL}/members/${encodedEmail}`, updatedData);
        updatedMember = response.data;
      }

      // 상태 및 LocalStorage 업데이트
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