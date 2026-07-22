<template>
  <div class="container">
    <header v-if="company">
      <h1>{{ company.name }}</h1>
      <p class="slogan">{{ company.slogan }}</p>
    </header>

    <main v-if="company">
      <section class="about">
        <h2>회사 소개</h2>
        <p>{{ company.about }}</p>
      </section>

      <section class="services">
        <h2>주요 서비스</h2>
        <div class="service-grid">
          <div v-for="item in company.services" :key="item.id" class="card">
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
          </div>
        </div>
      </section>
    </main>

    <div v-else-if="loading" class="loading">
      데이터를 불러오는 중입니다...
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const company = ref(null)
const loading = ref(true)
const error = ref(null)

// Render 백엔드 API 주소
const API_URL = 'https://ilshin-website.onrender.com/api/company'

onMounted(async () => {
  try {
    const response = await fetch(API_URL)
    if (!response.ok) throw new Error('데이터를 불러오는데 실패했습니다.')
    company.value = await response.json()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  font-family: sans-serif;
}
header {
  text-align: center;
  border-bottom: 2px solid #eee;
  padding-bottom: 1.5rem;
  margin-bottom: 2rem;
}
.slogan {
  color: #666;
  font-size: 1.1rem;
}
.service-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}
.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1.2rem;
  background-color: #f9f9f9;
}
.loading, .error {
  text-align: center;
  padding: 3rem;
}
.error {
  color: red;
}
</style>
