<!-- src/views/HomeView.vue -->
<template>
  <div class="home-container">
    <section class="hero-section">
      <h1>일신 소개</h1>
      <p>엄격한 품질 관리로 제작된 일신의 주요 도어 제품을 소개합니다.</p>
    </section>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading-box">
      제품 정보를 불러오는 중입니다...
    </div>

    <!-- 도어 정보 카드 목록 -->
    <div v-else-if="doors.length > 0" class="door-grid">
      <div v-for="door in doors" :key="door.id" class="door-card">
        <div class="door-image-placeholder" v-if="!door.image_url">
          🚪
        </div>
        <img v-else :src="door.image_url" :alt="door.title || door.name" class="door-img" />

        <div class="door-info">
          <h3>{{ door.title || door.name || '도어 제품' }}</h3>
          <p class="door-desc">{{ door.description || door.content || '제품 상세 설명이 없습니다.' }}</p>
          <div class="door-spec" v-if="door.spec">
            <span>스펙: {{ door.spec }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 데이터 없음 -->
    <div v-else class="empty-box">
      현재 게시 중인 도어 제품 정보가 없습니다.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { doorApi } from '../api/door';

const doors = ref([]);
const loading = ref(true);

const fetchActiveDoors = async () => {
  loading.value = true;
  try {
    // 1. API 호출
    const response = await doorApi.getDoorInfos();
    const data = response.data || [];

    // 2. useyn이 'Y'인 레코드만 프론트엔드에서 필터링 (대소문자 구별 방지)
    doors.value = data.filter(item => item.useyn && item.useyn.toUpperCase() === 'Y');

    /* 만약 백엔드에 /api/door-info/active API를 만드셨다면 아래처럼 직접 사용 가능합니다:
       const response = await doorApi.getActiveDoorInfos();
       doors.value = response.data;
    */
  } catch (error) {
    console.error('도어 정보 불러오기 실패:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchActiveDoors();
});
</script>

<style scoped>
.home-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 20px;
}

.hero-section {
  text-align: center;
  margin-bottom: 40px;
}

.hero-section h1 {
  font-size: 2.2rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.hero-section p {
  color: #666;
  font-size: 1.1rem;
}

.door-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

.door-card {
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
  background: #fff;
}

.door-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.door-image-placeholder {
  height: 180px;
  background-color: #f5f6f8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
}

.door-img {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.door-info {
  padding: 20px;
}

.door-info h3 {
  margin: 0 0 10px 0;
  font-size: 1.25rem;
  color: #333;
}

.door-desc {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.5;
  margin-bottom: 15px;
}

.door-spec {
  font-size: 0.85rem;
  color: #42b983;
  font-weight: bold;
}

.loading-box, .empty-box {
  text-align: center;
  padding: 60px 0;
  color: #888;
  font-size: 1.1rem;
}
</style>