// frontend/src/composables/useAuth.js
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

  // ★ 이메일 기반 회원정보 수정 함수
  const updateUserInfo = async (updatedData) => {
    try {
      const email = currentUser.value?.email || updatedData.email;
      if (!email) {
        throw new Error('이메일 정보가 존재하지 않습니다.');
      }

      // API 호출
      const updatedMember = await authApi.updateMemberByEmail(email, updatedData);

      // 반환 데이터로 상태 갱신
      currentUser.value = {
        ...currentUser.value,
        ...updatedMember
      };

      // localStorage 업데이트
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