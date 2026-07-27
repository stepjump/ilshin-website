<!-- frontend/src/views/AboutView.vue -->
<template>
  <div class="about-container">
    <!-- 로딩 중 표시 -->
    <div v-if="loading" class="loading">
      회사소개 정보를 불러오는 중입니다...
    </div>

    <!-- 에러 발생 시 표시 -->
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="fetchCompanyInfo">다시 시도</button>
    </div>

    <!-- 백엔드 데이터를 활용한 회사소개 카드 -->
    <div v-else-if="companyData" class="about-card">
      <!-- 1. 회사명 & 슬로건 -->
      <div class="header-section">
        <h2 class="company-name">{{ companyData.name || '(주)일신' }}</h2>
        <p v-if="companyData.slogan" class="slogan">
          "{{ companyData.slogan }}"
        </p>
      </div>

      <hr class="divider" />

      <!-- 2. 회사 소개 본문 -->
      <div class="content-section">
        <h3>기업 소개</h3>
        <p class="about-text">{{ companyData.about }}</p>
      </div>

      <!-- 3. 주소 및 연락처 정보 -->
      <div class="info-section">
        <div v-if="companyData.address" class="info-item">
          <span class="info-label">📍 주소</span>
          <span class="info-value">{{ companyData.address }}</span>
        </div>
        <div v-if="companyData.phone" class="info-item">
          <span class="info-label">📞 전화</span>
          <span class="info-value">{{ companyData.phone }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

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
    if (err.response) {
      error.value = `회사소개 정보를 불러오지 못했습니다. (상태 코드: ${err.response.status})`;
    } else {
      error.value = `서버 연결에 실패했습니다. (${err.message})`;
    }
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
  border-radius: 12px;
  padding: 2.5rem;
  background-color: #ffffff;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.header-section {
  text-align: center;
  margin-bottom: 1.5rem;
}

.company-name {
  font-size: 2rem;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
  font-weight: 700;
}

.slogan {
  font-size: 1.1rem;
  color: #3b82f6;
  font-weight: 600;
  margin: 0;
}

.divider {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 1.5rem 0;
}

.content-section {
  margin-bottom: 2rem;
}

.content-section h3 {
  font-size: 1.25rem;
  color: #334155;
  margin-bottom: 0.75rem;
  border-left: 4px solid #3b82f6;
  padding-left: 0.5rem;
}

.about-text {
  line-height: 1.8;
  color: #475569;
  font-size: 1.05rem;
  white-space: pre-line; /* 줄바꿈 유지 */
}

.info-section {
  background-color: #f8fafc;
  border-radius: 8px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.info-label {
  font-weight: 600;
  color: #64748b;
  min-width: 70px;
}

.info-value {
  color: #1e293b;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
  color: #64748b;
}

.error {
  color: #dc2626;
}

.retry-btn {
  margin-top: 0.75rem;
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
</style>