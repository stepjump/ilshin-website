<!-- frontend/src/views/HomeView.vue -->
<template>
  <div class="home-container">
    <h2>앞대문 내용</h2>

    <!-- 로딩 중 표시 -->
    <div v-if="loading" class="loading">
      데이터를 불러오는 중입니다...
    </div>

    <!-- 에러 발생 시 표시 -->
    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <!-- active API에서 받아온 도어 정보 표시 -->
    <div v-else-if="doorData" class="door-card">
      <!-- 정수형 ver 정보 표시 (예: 버전 v1, v2...) -->
      <div class="card-header">
        <span class="version-badge">버전 v{{ doorData.ver }}</span>
      </div>
      
      <!-- v-html을 사용하여 DB의 HTML 태그를 그대로 해석하여 출력 -->
      <div class="info-text" v-html="doorData.info"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { doorApi } from '../api/door';

const doorData = ref(null);
const loading = ref(true);
const error = ref(null);

// /api/door-info/active 호출 함수
const fetchActiveDoorInfo = async () => {
  try {
    loading.value = true;
    const response = await doorApi.getActiveDoorInfo();
    doorData.value = response.data;
  } catch (err) {
    console.error('Active door info 불러오기 실패:', err);
    error.value = '첫 화면 정보를 불러오는데 실패했습니다.';
  } finally {
    loading.value = false;
  }
};

// 컴포넌트 마운트 시 실행
onMounted(() => {
  fetchActiveDoorInfo();
});
</script>

<style scoped>
.home-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.door-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
}

.version-badge {
  font-size: 0.85rem;
  font-weight: 600;
  color: #2563eb;
  background-color: #eff6ff;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  border: 1px solid #bfdbfe;
}

.info-text {
  line-height: 1.7;
  color: #334155;
}

/* HTML 컨텐츠 내부 이미지/테이블 기본 스타일 */
.info-text :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

.info-text :deep(p) {
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