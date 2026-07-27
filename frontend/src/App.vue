<!-- frontend/src/App.vue -->
<template>
  <div id="app">
    <!-- 상단 네비게이션 바 -->
    <header class="navbar">
      <h1 class="logo">
        <router-link to="/">일신 홈페이지</router-link>
      </h1>
      <nav class="nav-links">
        <!-- 회사소개 링크 -->
        <router-link to="/about">회사소개</router-link>
        
        <!-- 자유게시판 -->
        <router-link to="/board">자유게시판</router-link>
        
        <!-- 로그인 상태 표시 -->
        <span v-if="isLoggedIn" class="user-area">
          <span class="user-name">{{ currentUser?.name || currentUser?.email || '회원' }}님</span>
          <button @click="handleLogout" class="logout-btn">로그아웃</button>
        </span>
        <router-link v-else to="/login" class="login-link">로그인</router-link>
      </nav>
    </header>

    <!-- 라우터에 따라 실제 화면이 렌더링되는 영역 -->
    <main class="content">
      <!-- key를 $route.fullPath로 지정하면 경로 이동 시 확실하게 강제 새로고침(재렌더링) 됩니다 -->
      <router-view :key="$route.fullPath" />
    </main>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router';
import { useAuth } from './composables/useAuth';

const router = useRouter();
const route = useRoute();
const { currentUser, isLoggedIn, logout } = useAuth();

const handleLogout = () => {
  logout();
  alert('로그아웃 되었습니다.');
  router.push('/login');
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
  gap: 10px;
}
.user-name {
  font-size: 0.9rem;
  color: #ddd;
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
</style>