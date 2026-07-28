<template>
  <div class="detail-container">
    <div v-if="loading" class="loading">게시글을 불러오는 중...</div>
    
    <div v-else-if="!post" class="error-msg">
      게시글이 존재하지 않거나 삭제되었습니다.
      <br />
      <router-link to="/board" class="back-link">목록으로 돌아가기</router-link>
    </div>

    <div v-else class="post-card">
      <div class="post-header">
        <h2>{{ post.title }}</h2>
        <div class="post-meta">
          <span>✍️ {{ post.author_name }} ({{ post.author_email }})</span>
          <span>📅 {{ formatDate(post.created_at) }}</span>
        </div>
      </div>

      <div class="post-body">
        <p>{{ post.content }}</p>
      </div>

      <div class="post-actions">
        <router-link to="/board" class="list-btn">목록</router-link>
        
        <!-- ★ 작성자 본인이거나 admin 회원 등급인 경우 삭제 버튼 표시 -->
        <button 
          v-if="canDelete" 
          @click="handleDelete" 
          class="delete-btn"
          :disabled="deleting"
        >
          {{ deleting ? '삭제 중...' : '삭제하기' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { useAuth } from '../composables/useAuth';

const route = useRoute();
const router = useRouter();
const API_BASE_URL = 'https://ilshin-website.onrender.com/api';

const { currentUser } = useAuth();

const post = ref(null);
const loading = ref(true);
const deleting = ref(false);

const postId = route.params.id;

// ★ 삭제 권한 계산 (작성자 본인 OR admin)
const canDelete = computed(() => {
  if (!currentUser.value || !post.value) return false;
  
  const isAuthor = currentUser.value.email === post.value.author_email;
  const isAdmin = currentUser.value.role === 'admin';

  return isAuthor || isAdmin;
});

const fetchPostDetail = async () => {
  try {
    loading.value = true;
    const response = await axios.get(`${API_BASE_URL}/board/${postId}`);
    post.value = response.data;
  } catch (err) {
    console.error('게시글 상세조회 실패:', err);
  } finally {
    loading.value = false;
  }
};

const handleDelete = async () => {
  if (!confirm('정말로 이 게시글을 삭제하시겠습니까?')) return;

  try {
    deleting.value = true;
    const token = currentUser.value?.access_token || localStorage.getItem('token');

    await axios.delete(`${API_BASE_URL}/board/${postId}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    alert('게시글이 삭제되었습니다.');
    router.push('/board');
  } catch (err) {
    console.error('게시글 삭제 실패:', err);
    alert(err.response?.data?.detail || '게시글 삭제 중 오류가 발생했습니다.');
  } finally {
    deleting.value = false;
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

onMounted(() => {
  fetchPostDetail();
});
</script>

<style scoped>
.detail-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.post-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
  padding: 24px;
  border: 1px solid #e2e8f0;
}

.post-header {
  border-bottom: 2px solid #f1f5f9;
  padding-bottom: 16px;
  margin-bottom: 20px;
}

.post-header h2 {
  margin: 0 0 10px 0;
  color: #0f172a;
  font-size: 1.5rem;
}

.post-meta {
  display: flex;
  gap: 20px;
  color: #64748b;
  font-size: 0.9rem;
}

.post-body {
  min-height: 150px;
  line-height: 1.6;
  color: #334155;
  white-space: pre-wrap;
  margin-bottom: 30px;
}

.post-actions {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid #f1f5f9;
  padding-top: 16px;
}

.list-btn {
  padding: 8px 16px;
  background-color: #64748b;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 500;
}

.delete-btn {
  padding: 8px 16px;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
}

.delete-btn:hover {
  background-color: #dc2626;
}

.delete-btn:disabled {
  background-color: #fca5a5;
  cursor: not-allowed;
}

.loading, .error-msg {
  text-align: center;
  padding: 40px;
  color: #64748b;
}

.back-link {
  color: #2563eb;
  text-decoration: underline;
  margin-top: 10px;
  display: inline-block;
}
</style>