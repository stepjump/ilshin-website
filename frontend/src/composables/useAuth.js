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

  // ★ member.py API 연동 계정 정보 수정
  const updateUserInfo = async (updatedData) => {
    try {
      // 로그인된 사용자 ID 추출 (id 또는 member_id)
      const memberId = currentUser.value?.id || currentUser.value?.member_id || currentUser.value?.username || 1;

      // API 호출
      const updatedMember = await authApi.updateMember(memberId, updatedData);

      // 반환된 MemberResponse 데이터로 currentUser 갱신
      currentUser.value = {
        ...currentUser.value,
        ...updatedMember
      };

      // localStorage 데이터 동기화
      localStorage.setItem('user', JSON.stringify(currentUser.value));

      return { success: true, data: updatedMember };
    } catch (error) {
      console.error('회원정보 수정 실패:', error);
      
      // API 통신 에러 시 클라이언트 가상 반영 (서버 연결 불가 시 대처)
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