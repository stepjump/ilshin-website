<!-- frontend/src/views/AboutView.vue -->
<template>
  <div class="about-container">
    <h2>회사소개</h2>

    <!-- 1. 로딩 중 표시 -->
    <div v-if="loading" class="loading">
      회사소개 정보를 불러오는 중입니다...
    </div>

    <!-- 2. 에러 발생 시 표시 -->
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="fetchCompanyInfo">다시 시도</button>
    </div>

    <!-- 3. 데이터 수신 성공시 표시 -->
    <div v-else-if="companyData" class="about-card">
      <!-- 제목이 있는 경우 출력 -->
      <h3 v-if="computedTitle" class="company-title">
        {{ computedTitle }}
      </h3>

      <!-- 본문 내용 출력 (v-html 사용) -->
      <div 
        v-if="computedContent" 
        class="company-content" 
        v-html="computedContent"
      ></div>

      <!-- 만약 필드명이 안 맞아서 본문 출력이 안 되면, 아래 원본 데이터가 표시됩니다 -->
      <div v-else class="debug-box">
        <p>⚠️ <strong>데이터는 응답받았으나 출력할 필드를 찾지 못했습니다.</strong></p>
        <p>백엔드에서 들어온 실제 JSON 데이터:</p>
        <pre>{{ JSON.stringify(companyData, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

const API_URL = 'https://ilshin-website.onrender.com/api/company/1';

const companyData = ref(null);
const loading = ref(true);
const error = ref(null);

// 백엔드가 배열([ { ... } ])로 넘겨주든 객체({ ... })로 넘겨주든 단일 객체로 정제
const targetObject = computed(() => {
  if (!companyData.value) return null;
  if (Array.isArray(companyData.value)) {
    return companyData.value[0] || null; // 배열인 경우 첫 번째 아이템 추출
  }
  return companyData.value;
});

// 제목 필드 탐색 (title, name, company_name 등)
const computedTitle = computed(() => {
  const obj = targetObject.value;
  if (!obj) return '';
  if (typeof obj === 'string') return '';
  return obj.title || obj.name || obj.company_name || obj.subject || '';
});

// 본문 필드 탐색 (content, info, description, details, body 등)
const computedContent = computed(() => {
  const obj = targetObject.value;
  if (!obj) return '';
  // 단순 문자열로 넘어왔을 경우
  if (typeof obj === 'string') return obj;

  return obj.content || 
         obj.info || 
         obj.description || 
         obj.details || 
         obj.body || 
         obj.company_info || 
         obj.detail || '';
});

const fetchCompanyInfo = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    const response = await axios.get(API_URL);
    console.log('API Response Data:', response.data);
    
    companyData.value = response.data;
  } catch (err) {
    console.error('회사소개 불러오기 실패:', err);
    if (err.response) {
      error.value = `회사소개 정보를 불러오지 못했습니다. (응답 상태 코드: ${err.response.status})`;
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

.debug-box {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 6px;
  font-size: 0.9rem;
}

.debug-box pre {
  background: #1e293b;
  color: #f8fafc;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}

.error {
  color: #dc2626;
}

.retry-btn {
  margin-top: 0.75rem;
  padding: 0.4rem 0.8rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>