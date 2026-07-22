<template>
  <div style="font-family: sans-serif; padding: 2rem; max-width: 800px; margin: 0 auto;">
    <h1>일신 웹사이트</h1>
    <hr />
    <h2>백엔드 연결 상태</h2>
    <p v-if="loading">백엔드 서버(Render)에서 데이터를 가져오는 중입니다...</p>
    <p v-else-if="error" style="color: red;">연결 에러: {{ error }}</p>
    <div v-else style="background: #f4f4f4; padding: 1rem; border-radius: 8px;">
      <pre>{{ apiData }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const apiData = ref(null)
const loading = ref(true)
const error = ref(null)

// Render 백엔드 API 호출
onMounted(async () => {
  try {
    const response = await fetch('https://ilshin-website.onrender.com/')
    if (!response.ok) throw new Error('네트워크 응답이 정상이 아닙니다.')
    const data = await response.json()
    apiData.value = data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>
