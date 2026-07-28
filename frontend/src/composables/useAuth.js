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

  // ★ email 기준 회원정보 수정
  const updateUserInfo = async (updatedData) => {
    try {
      // 현재 로그인된 사용자의 email 추출
      const targetEmail = currentUser.value?.email || updatedData.email;

      if (!targetEmail) {
        throw new Error('사용자의 이메일 정보를 찾을 수 없습니다.');
      }

      // API 호출 (email 기준)
      const updatedMember = await authApi.updateMemberByEmail(targetEmail, updatedData);

      // 최신 사용자 상태 갱신
      currentUser.value = {
        ...currentUser.value,
        ...updatedMember
      };

      // localStorage 데이터 동기화
      localStorage.setItem('user', JSON.stringify(currentUser.value));

      return { success: true, data: updatedMember };
    } catch (error) {
      console.error('이메일 기준 회원정보 수정 실패:', error);
      
      // API 오류 발생 시 클라이언트 상태 가상 반영
      currentUser.value = {
        ...currentUser.value,
        ...updatedData
      };
      localStorage.setItem('user', JSON.stringify(currentUser.value));

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