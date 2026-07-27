<!-- frontend/src/views/AboutView.vue -->
<template>
  <div class="about-container">
    <h2>회사소개</h2>

    <!-- 로딩 중 표시 -->
    <div v-if="loading" class="loading">
      회사소개 정보를 불러오는 중입니다...
    </div>

    <!-- 에러 발생 시 표시 -->
    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <!-- API에서 받아온 단일 회사소개 정보 표시 -->
    <div v-else-if="companyData" class="about-card">
      <h3 v-if="companyData.title" class="company-title">
        {{ companyData.title }}
      </h3>

      <!-- v-html을 이용하여 DB에 저장된 HTML 태그/문구 출력 -->
      <div 
        class="company-content" 
        v-html="companyData.content || companyData.info || companyData.description"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

// ★ ID 1번 단일 데이터 조회 API 엔드포인트
const API_URL = 'https://ilshin-website.onrender.com/api/company/1';

const companyData = ref(null);
const loading = ref(true);
const error = ref(null);

const fetchCompanyInfo = async () => {
  try {
    loading.value = true;
    error.value = null;
    const response = await axios.get(API_URL);
    companyData.value = response.data;
  } catch (err) {
    console.error('회사소개 불러오기 실패:', err);
    error.value = '회사소개 정보를 불러오는데 실패했습니다.';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchCompanyInfo();
});
</script>

<style scoped>
.about-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.about-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 2rem;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.company-title {
  margin-top: 0;
  color: #1e293b;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  border-bottom: 2px solid #3b82f6;
  padding-bottom: 0.5rem;
}

.company-content {
  line-height: 1.7;
  color: #334155;
}

.company-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

.company-content :deep(p) {
  margin-bottom: 0.75rem;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}

.error {
  color: #dc2626;
}
</style>