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
      <!-- 관리자 전용 수정 버튼 -->
      <div v-if="isAdmin" class="admin-bar">
        <button class="edit-btn" @click="openEditModal">✏️ 회사소개 수정 (관리자)</button>
      </div>

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

    <!-- ✏️ 관리자 수정 모달 창 -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-content">
        <h3>회사소개 정보 수정</h3>
        
        <form @submit.prevent="handleUpdate">
          <div class="form-group">
            <label>회사명</label>
            <input type="text" v-model="editForm.name" required />
          </div>

          <div class="form-group">
            <label>슬로건</label>
            <input type="text" v-model="editForm.slogan" placeholder="예: 신뢰와 기술로 미래를 열어가는 기업" />
          </div>

          <div class="form-group">
            <label>기업 소개 (본문)</label>
            <textarea v-model="editForm.about" rows="5" required></textarea>
          </div>

          <div class="form-group">
            <label>주소</label>
            <input type="text" v-model="editForm.address" />
          </div>

          <div class="form-group">
            <label>전화번호</label>
            <input type="text" v-model="editForm.phone" />
          </div>

          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="closeEditModal">취소</button>
            <button type="submit" class="save-btn" :disabled="saving">
              {{ saving ? '저장 중...' : '저장하기' }}
            </button>
          </div>
        </form>
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

// 관리자 수정 관련 상태
const showEditModal = ref(false);
const saving = ref(false);
const editForm = ref({
  name: '',
  slogan: '',
  about: '',
  address: '',
  phone: ''
});

// 관리자 로그인 권한 체크 (localStorage 내부 여러 키 탐색)
const isAdmin = computed(() => {
  try {
    const keys = ['user', 'userInfo', 'auth', 'token'];
    for (const key of keys) {
      const item = localStorage.getItem(key);
      if (!item) continue;
      
      try {
        const parsed = JSON.parse(item);
        if (parsed.role === 'admin' || parsed.username === 'admin' || parsed.isAdmin === true) {
          return true;
        }
      } catch {
        if (item === 'admin' || item.includes('admin')) return true;
      }
    }
  } catch (e) {
    console.error('관리자 권한 확인 중 오류:', e);
  }
  return false;
});

// 회사 정보 조회 (GET)
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

// 수정 모달 열기
const openEditModal = () => {
  if (companyData.value) {
    editForm.value = {
      name: companyData.value.name || '',
      slogan: companyData.value.slogan || '',
      about: companyData.value.about || '',
      address: companyData.value.address || '',
      phone: companyData.value.phone || ''
    };
  }
  showEditModal.value = true;
};

// 수정 모달 닫기
const closeEditModal = () => {
  showEditModal.value = false;
};

// 수정 요청 전송 (PUT / PATCH)
const handleUpdate = async () => {
  try {
    saving.value = true;
    
    // PUT 요청 시도
    const response = await axios.put(API_URL, editForm.value);
    companyData.value = response.data;
    alert('회사소개가 성공적으로 수정되었습니다.');
    closeEditModal();
  } catch (err) {
    console.warn('PUT 수정 실패, PATCH로 재시도합니다:', err);
    try {
      // PUT에 실패할 경우 PATCH로 자동 재시도
      const patchResponse = await axios.patch(API_URL, editForm.value);
      companyData.value = patchResponse.data;
      alert('회사소개가 성공적으로 수정되었습니다.');
      closeEditModal();
    } catch (patchErr) {
      console.error('회사소개 수정 실패:', patchErr);
      alert('수정에 실패했습니다. 서버 상태 또는 API 권한을 확인해 주세요.');
    }
  } finally {
    saving.value = false;
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
  position: relative;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 2.5rem;
  background-color: #ffffff;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.admin-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
}

.edit-btn {
  background-color: #059669;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.edit-btn:hover {
  background-color: #047857;
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
  white-space: pre-line;
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

/* 모달 레이아웃 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 90%;
  max-width: 550px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #0f172a;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.4rem;
  color: #334155;
  font-size: 0.9rem;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  box-sizing: border-box;
  font-size: 0.95rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.cancel-btn {
  padding: 0.5rem 1rem;
  background: #e2e8f0;
  color: #475569;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.save-btn {
  padding: 0.5rem 1rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.save-btn:disabled {
  background: #93c5fd;
  cursor: not-allowed;
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