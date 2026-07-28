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

  return {
    currentUser,
    isLoggedIn,
    login,
    logout,
  };
}