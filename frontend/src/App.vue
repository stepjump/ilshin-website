<template>
  <div style="font-family: 'Noto Sans KR', sans-serif; padding: 2.5rem; max-width: 800px; margin: 0 auto; color: #333;">
    <header style="border-bottom: 2px solid #2b6cb0; padding-bottom: 1rem; margin-bottom: 2rem;">
      <h1 style="margin: 0; color: #2b6cb0; font-size: 2rem;">🏢 일신 웹사이트</h1>
      <p style="margin-top: 0.5rem; color: #666;">FastAPI (Render) & Vue 3 (Vercel) 연동 완료</p>
    </header>

    <!-- 로딩 상태 -->
    <div v-if="loading" style="text-align: center; padding: 3rem; font-size: 1.1rem; color: #4a5568;">
      ⏳ 백엔드 서버에서 회사 정보를 가져오는 중입니다...
    </div>

    <!-- 에러 발생 시 -->
    <div v-else-if="error" style="background: #fff5f5; border: 1px solid #feb2b2; padding: 1.5rem; border-radius: 8px; color: #c53030;">
      <strong>⚠️ 연결 에러:</strong> {{ error }}
    </div>

    <!-- 성공적으로 데이터를 받아왔을 때 -->
    <main v-else style="background: #f7fafc; border: 1px solid #e2e8f0; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
      <h2 style="margin-top: 0; color: #2d3748; font-size: 1.5rem; border-bottom: 1px solid #cbd5e0; padding-bottom: 0.5rem;">
        회사 정보
      </h2>
      
      <div style="background: #1a202c; color: #68d391; padding: 1.2rem; border-radius: 8px; overflow-x: auto; font-family: monospace; font-size: 0.95rem; line-height: 1.5;">
        <pre style="margin: 0;">{{ JSON.stringify(companyData, null, 2) }}</pre>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const companyData = ref(null)
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    // /api/company 엔드포인트 호출
    const response = await fetch('https://ilshin-website.onrender.com/api/company')
    if (!response.ok) {
      throw new Error(`서버 응답 에러 (${response.status})`)
    }
    const data = await response.json()
    companyData.value = data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>
