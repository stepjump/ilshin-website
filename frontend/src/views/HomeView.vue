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
      <div class="card-header">
        <!-- ★ 버전 뱃지 클릭 시 관리자라면 바로 수정 모달 오픈 -->
        <span 
          class="version-badge" 
          :class="{ 'clickable': isAdmin }"
          @click="isAdmin && openEditModal()"
          :title="isAdmin ? '클릭하여 내용 수정' : ''"
        >
          버전 v{{ doorData.ver }} {{ isAdmin ? '✏️' : '' }}
        </span>
      </div>
      
      <!-- v-html을 사용하여 DB의 HTML 태그를 그대로 해석하여 출력 -->
      <div class="info-text" v-html="doorData.info"></div>
    </div>

    <!-- ★ 대문 내용 수정 모달 (Admin 전용) -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h3>앞대문 내용 수정 (새 버전 생성)</h3>
        <p class="modal-desc">
          내용을 수정하고 저장하면 <strong>버전 v{{ nextVersion }}</strong>로 자동 생성 및 적용됩니다. HTML 태그 작성이 가능합니다.
        </p>

        <textarea 
          v-model="editInfo" 
          rows="10" 
          class="info-textarea" 
          placeholder="HTML 태그 또는 문구를 입력하세요..."
        ></textarea>

        <div class="modal-actions">
          <button class="cancel-btn" @click="closeModal" :disabled="saving">취소</button>
          <button class="save-btn" @click="saveNewDoorInfo" :disabled="saving">
            {{ saving ? '저장 중...' : '저장하기' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { doorApi } from '../api/door';

const doorData = ref(null);
const loading = ref(true);
const error = ref(null);

// 관리자 모달 및 저장 관련 상태
const showModal = ref(false);
const editInfo = ref('');
const saving = ref(false);

// 다음 예상 버전 계산
const nextVersion = computed(() => {
  if (!doorData.value || doorData.value.ver === undefined) return 1;
  const currentVer = parseInt(doorData.value.ver, 10);
  return isNaN(currentVer) ? 1 : currentVer + 1;
});

// admin 로그인 상태 체크 (localStorage 기반)
const isAdmin = computed(() => {
  const userJson = localStorage.getItem('user');
  if (!userJson) return false;
  try {
    const user = JSON.parse(userJson);
    return user.role === 'admin' || user.username === 'admin';
  } catch (e) {
    return false;
  }
});

// /api/door-info/active 호출 함수
const fetchActiveDoorInfo = async () => {
  try {
    loading.value = true;
    error.value = null;
    const response = await doorApi.getActiveDoorInfo();
    doorData.value = response.data;
  } catch (err) {
    console.error('Active door info 불러오기 실패:', err);
    error.value = '첫 화면 정보를 불러오는데 실패했습니다.';
  } finally {
    loading.value = false;
  }
};

// 모달 열기
const openEditModal = () => {
  if (doorData.value) {
    editInfo.value = doorData.value.info;
  }
  showModal.value = true;
};

// 모달 닫기
const closeModal = () => {
  if (saving.value) return;
  showModal.value = false;
};

// 신규 버전 대문 저장
const saveNewDoorInfo = async () => {
  if (!editInfo.value.trim()) {
    alert('내용을 입력해주세요.');
    return;
  }

  try {
    saving.value = true;
    await doorApi.createDoorInfo({
      info: editInfo.value,
      useyn: 'Y'
    });
    alert('새로운 대문 내용이 정상적으로 적용되었습니다.');
    showModal.value = false;
    await fetchActiveDoorInfo();
  } catch (err) {
    console.error('대문 수정 실패:', err);
    alert('대문 내용 저장 중 오류가 발생했습니다.');
  } finally {
    saving.value = false;
  }
};

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
  align-items: center;
  margin-bottom: 1rem;
}

/* ★ 버전 뱃지 스타일 */
.version-badge {
  font-size: 0.85rem;
  font-weight: 600;
  color: #2563eb;
  background-color: #eff6ff;
  padding: 0.3rem 0.75rem;
  border-radius: 20px;
  border: 1px solid #bfdbfe;
  user-select: none;
  transition: all 0.2s ease;
}

/* ★ 클릭 가능한 관리자 전용 버전 뱃지 hover 효과 */
.version-badge.clickable {
  cursor: pointer;
}

.version-badge.clickable:hover {
  background-color: #dbeafe;
  border-color: #3b82f6;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.15);
}

.info-text {
  line-height: 1.7;
  color: #334155;
}

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

/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #ffffff;
  padding: 2rem;
  border-radius: 12px;
  width: 90%;
  max-width: 650px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.modal-content h3 {
  margin-top: 0;
  color: #1e293b;
}

.modal-desc {
  font-size: 0.9rem;
  color: #64748b;
  margin-bottom: 1rem;
}

.info-textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.95rem;
  resize: vertical;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.25rem;
}

.cancel-btn {
  padding: 0.5rem 1rem;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  cursor: pointer;
}

.save-btn {
  padding: 0.5rem 1rem;
  background: #2563eb;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.save-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.save-btn:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}
</style>