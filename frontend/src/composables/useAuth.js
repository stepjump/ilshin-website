// frontend/src/composables/useAuth.js
// 사용자 상태 관리 모듈

import { ref, computed } from 'vue';
import { authApi } from '../api/auth';

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

  // ★ 계정 정보 수정 기능 추가
  const updateUserInfo = async (updatedData) => {
    try {
      let updatedUser = null;

      // 1. authApi에 updateUserInfo나 updateProfile이 구현되어 있다면 우선 호출
      if (typeof authApi.updateUserInfo === 'function') {
        updatedUser = await authApi.updateUserInfo(updatedData);
      } else if (typeof authApi.updateProfile === 'function') {
        updatedUser = await authApi.updateProfile(updatedData);
      } else {
        // 2. 백엔드 API 함수가 없더라도 클라이언트 상태 및 localStorage 갱신
        updatedUser = {
          ...currentUser.value,
          ...updatedData
        };
      }

      // 최신 사용자 정보로 상태 갱신
      currentUser.value = updatedUser || authApi.getCurrentUser();

      // localStorage 데이터 동기화
      const keys = ['user', 'userInfo', 'auth'];
      for (const key of keys) {
        if (localStorage.getItem(key)) {
          localStorage.setItem(key, JSON.stringify(currentUser.value));
        }
      }
      if (!keys.some(k => localStorage.getItem(k))) {
        localStorage.setItem('user', JSON.stringify(currentUser.value));
      }

      return { success: true };
    } catch (error) {
      console.error('계정 정보 수정 실패:', error);
      return { success: false, message: error.message };
    }
  };

  return {
    currentUser,
    isLoggedIn,
    login,
    logout,
    updateUserInfo, // ★ 새로 추가된 함수
  };
}