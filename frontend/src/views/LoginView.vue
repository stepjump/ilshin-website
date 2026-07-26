<template>
  <div class="login-container">
    <h2>로그인</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label>이메일</label>
        <input 
          v-model="email" 
          type="email" 
          required 
          placeholder="email@example.com" 
        />
      </div>
      <div class="form-group">
        <label>비밀번호</label>
        <input 
          v-model="password" 
          type="password" 
          required 
          placeholder="비밀번호 입력" 
        />
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? '로그인 중...' : '로그인' }}
      </button>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../composables/useAuth';

const email = ref('');
const password = ref('');
const loading = ref(false);
const errorMessage = ref('');

const router = useRouter();
const { login } = useAuth();

const handleLogin = async () => {
  loading.value = true;
  errorMessage.value = '';

  try {
    await login(email.value, password.value);
    alert('로그인 성공!');
    router.push('/board'); // 로그인 성공 후 게시판 페이지로 이동
  } catch (error) {
    console.error('로그인 에러:', error);
    errorMessage.value = error.response?.data?.detail || '로그인에 실패했습니다.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}
.form-group {
  margin-bottom: 15px;
}
.form-group label {
  display: block;
  margin-bottom: 5px;
}
.form-group input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
button {
  width: 100%;
  padding: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:disabled {
  background-color: #a8d8c0;
}
.error {
  color: red;
  margin-top: 10px;
}
</style>
