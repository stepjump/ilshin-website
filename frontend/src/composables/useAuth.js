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

  // 백엔드 단일 회원 상세조회 GET API (/api/members/{email})
  const fetchMemberDetail = async (email) => {
    try {
      if (!email) return null;
      const encodedEmail = encodeURIComponent(email);
      const response = await axios.get(`${API_BASE_URL}/members/${encodedEmail}`);
      return response.data;
    } catch (error) {
      console.error('회원 상세 정보 조회 실패:', error);
      return null;
    }
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

      // 상태 및 로컬 스토리지에 이메일/이름/전화번호 필드를 명확하게 매핑
      currentUser.value = {
        ...currentUser.value,
        name: updatedMember.name,
        phone: updatedMember.phone || '',
        email: updatedMember.email
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
    fetchMemberDetail,
    updateUserInfo,
  };
}