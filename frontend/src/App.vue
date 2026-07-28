<template>
  <div id="app">
    <!-- 상단 네비게이션 바 -->
    <header class="navbar">
      <h1 class="logo">
        <router-link to="/">일신 홈페이지9</router-link>
      </h1>
      <nav class="nav-links">
        <router-link to="/about">회사소개</router-link>
        <router-link to="/board">자유게시판</router-link>
        
        <!-- 로그인 상태 표시 -->
        <span v-if="isLoggedIn" class="user-area">
          <span 
            class="user-name clickable" 
            @click="openProfileModal" 
            title="계정정보 변경"
          >
            👤 {{ currentUser?.name || currentUser?.email || '회원' }}님
          </span>
          <button @click="handleLogout" class="logout-btn">로그아웃</button>
        </span>
        <router-link v-else to="/login" class="login-link">로그인</router-link>
      </nav>
    </header>

    <!-- 라우터 화면 영역 -->
    <main class="content">
      <router-view :key="$route.fullPath" />
    </main>

    <!-- 👤 계정 정보 변경 모달 창 -->
    <div v-if="showProfileModal" class="modal-overlay" @click.self="closeProfileModal">
      <div class="modal-content">
        <h3>👤 계정 정보 변경</h3>
        
        <form @submit.prevent="handleSaveProfile">
          <div class="form-group">
            <label>이메일 (계정 Key / 변경 불가)</label>
            <input 
              type="text" 
              :value="profileForm.email" 
              disabled 
              class="disabled-input"
            />
          </div>

          <div class="form-group">
            <label>이름</label>
            <input 
              type="text" 
              v-model="profileForm.name" 
              placeholder="이름을 입력하세요"
              required 
            />
          </div>

          <div class="form-group">
            <label>전화번호</label>
            <input 
              type="text" 
              v-model="profileForm.phone" 
              placeholder="010-0000-0000"
            />
          </div>

          <div class="form-group">
            <label>새 비밀번호 (변경할 경우만 입력)</label>
            <input 
              type="password" 
              v-model="profileForm.password" 
              placeholder="변경할 새 비밀번호" 
            />
          </div>

          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="closeProfileModal">취소</button>
            <button type="submit" class="save-btn" :disabled="saving">
              {{ saving ? '저장 중...' : '저장하기' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from './composables/useAuth';

const router = useRouter();
const { currentUser, isLoggedIn, logout, updateUserInfo, fetchMemberDetail } = useAuth();

const showProfileModal = ref(false);
const saving = ref(false);

const profileForm = ref({
  email: '',
  name: '',
  phone: '',
  password: ''
});

// 모달 오픈 시 백엔드 DB에서 직접 최신 회원 데이터 로드
const openProfileModal = async () => {
  const email = currentUser.value?.email;
  
  profileForm.value = {
    email: email || '',
    name: '',
    phone: '',
    password: ''
  };

  showProfileModal.value = true;

  if (email) {
    // DB에서 이메일 기준으로 회원 정보를 직접 조회해 폼을 깔끔하게 채움
    const detail = await fetchMemberDetail(email);
    if (detail) {
      profileForm.value.name = detail.name || '';
      profileForm.value.phone = detail.phone || '';
    } else {
      profileForm.value.name = currentUser.value?.name || '';
    }
  }
};

const closeProfileModal = () => {
  showProfileModal.value = false;
};

const handleLogout = () => {
  logout();
  alert('로그아웃 되었습니다.');
  router.push('/login');
};

const handleSaveProfile = async () => {
  try {
    saving.value = true;

    const payload = {
      name: profileForm.value.name,
      phone: profileForm.value.phone
    };

    if (profileForm.value.password && profileForm.value.password.trim() !== '') {
      payload.password = profileForm.value.password;
    }

    const res = await updateUserInfo(payload);

    if (res.success) {
      alert('계정 정보가 성공적으로 변경되었습니다.');
      closeProfileModal();
    } else {
      alert(`저장 실패: ${res.message}`);
    }
  } catch (err) {
    console.error('계정 정보 변경 처리 중 예외 발생:', err);
    alert('저장 도중 오류가 발생했습니다.');
  } finally {
    saving.value = false;
  }
};
</script>

<style scoped>
#app {
  font-family: Arial, sans-serif;
  color: #2c3e50;
}
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background-color: #35495e;
  color: white;
}
.logo a {
  color: white;
  text-decoration: none;
  font-size: 1.2rem;
  font-weight: bold;
}
.nav-links {
  display: flex;
  align-items: center;
  gap: 20px;
}
.nav-links a {
  color: #ffffff;
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
}
.nav-links a.router-link-active {
  color: #42b983;
  font-weight: bold;
}
.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name.clickable {
  font-size: 0.95rem;
  color: #e2e8f0;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s, color 0.2s;
  text-decoration: underline;
  text-underline-offset: 4px;
}
.user-name.clickable:hover {
  background-color: rgba(255, 255, 255, 0.15);
  color: #ffffff;
}

.logout-btn {
  background: #e74c3c;
  border: none;
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}
.content {
  padding: 20px;
  min-height: 80vh;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  color: #1e293b;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #0f172a;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.4rem;
  color: #334155;
  font-size: 0.9rem;
}

.form-group input {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  box-sizing: border-box;
  font-size: 0.95rem;
}

.disabled-input {
  background-color: #f1f5f9;
  color: #64748b;
  cursor: not-allowed;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.cancel-btn {
  padding: 0.5rem 1rem;
  background: #e2e8f0;
  color: #475569;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.save-btn {
  padding: 0.5rem 1rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.save-btn:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}
</style>