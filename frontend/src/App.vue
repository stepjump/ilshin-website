<template>
  <div id="app">
    <header class="navbar">
      <h1 class="logo">일신 홈페이지</h1>
      <nav>
        <router-link to="/board">게시판</router-link>
        <span v-if="isLoggedIn" class="user-area">
          <span class="user-name">{{ currentUser?.name || currentUser?.email }}님</span>
          <button @click="handleLogout" class="logout-btn">로그아웃</button>
        </span>
        <router-link v-else to="/login" class="login-link">로그인</router-link>
      </nav>
    </header>

    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAuth } from './composables/useAuth';

const router = useRouter();
const { currentUser, isLoggedIn, logout } = useAuth();

const handleLogout = () => {
  logout();
  alert('로그아웃 되었습니다.');
  router.push('/login');
};
</script>

<style>
#app { font-family: Avenir, Helvetica, Arial, sans-serif; color: #2c3e50; }
.navbar { display: flex; justify-content: space-between; align-items: center; padding: 15px 30px; background-color: #35495e; color: white; }
.logo { font-size: 1.2rem; margin: 0; }
nav { display: flex; align-items: center; gap: 20px; }
nav a { color: #fff; text-decoration: none; }
nav a.router-link-active { font-weight: bold; color: #42b983; }
.user-area { display: flex; align-items: center; gap: 10px; }
.user-name { font-size: 0.9rem; color: #ddd; }
.logout-btn { background: #e74c3c; border: none; color: white; padding: 5px 10px; border-radius: 4px; cursor: pointer; }
.content { min-height: 80vh; }
</style>