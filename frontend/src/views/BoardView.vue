<template>
  <div class="board-container">
    <div class="board-header">
      <h2>자유게시판</h2>
      <div class="header-actions">
        <!-- admin 회원 등급 전용: 전체글 삭제 버튼 -->
        <button 
          v-if="currentUser?.role === 'admin'" 
          @click="handleDeleteAll" 
          class="delete-all-btn"
          :disabled="deleting"
        >
          🚨 {{ deleting ? '삭제 중...' : '전체글 삭제' }}
        </button>

        <router-link v-if="isLoggedIn" to="/board/write" class="write-btn">
          글쓰기
        </router-link>
      </div>
    </div>

    <!-- 게시글 목록 -->
    <div v-if="loading" class="loading">게시글을 불러오는 중...</div>
    
    <div v-else-if="posts.length === 0" class="empty-list">
      작성된 게시글이 없습니다.
    </div>

    <table v-else class="board-table">
      <thead>
        <tr>
          <th class="col-id">번호</th>
          <th class="col-title">제목</th>
          <th class="col-author">작성자</th>
          <th class="col-date">작성일</th>
          <th class="col-action">관리</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(post, index) in posts" :key="post.id">
          <td class="col-id">{{ posts.length - index }}</td>
          <td class="col-title">
            <router-link :to="`/board/${post.id}`">{{ post.title }}</router-link>
          </td>
          <td class="col-author">{{ post.author_name }}</td>
          <td class="col-date">{{ formatDate(post.created_at) }}</td>
          <td class="col-action">
            <!-- ★ 자신의 글이거나 admin 등급인 경우에만 삭제 버튼 노출 -->
            <button 
              v-if="canDeletePost(post)" 
              @click="handleDeleteOne(post.id)" 
              class="small-delete-btn"
            >
              삭제
            </button>
            <span v-else class="no-perm">-</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuth } from '../composables/useAuth';

const API_BASE_URL = 'https://ilshin-website.onrender.com/api';
const { currentUser, isLoggedIn } = useAuth();

const posts = ref([]);
const loading = ref(true);
const deleting = ref(false);

const fetchPosts = async () => {
  try {
    loading.value = true;
    const response = await axios.get(`${API_BASE_URL}/board`);
    posts.value = response.data;
  } catch (err) {
    console.error('게시글 목록 불러오기 실패:', err);
  } finally {
    loading.value = false;
  }
};

// ★ 삭제 권한 판별: 자신의 게시물이거나 admin 계정인 경우 true
const canDeletePost = (post) => {
  if (!currentUser.value) return false;
  const isOwner = currentUser.value.email === post.author_email;
  const isAdmin = currentUser.value.role === 'admin';
  return isOwner || isAdmin;
};

// admin 전용: 전체글 삭제
const handleDeleteAll = async () => {
  if (posts.value.length === 0) {
    alert('삭제할 게시글이 없습니다.');
    return;
  }

  if (!confirm(`정말로 모든 게시글(${posts.value.length}개)을 삭제하시겠습니까?`)) return;

  try {
    deleting.value = true;
    const token = currentUser.value?.access_token || localStorage.getItem('token');
    
    const response = await axios.delete(`${API_BASE_URL}/board/all`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    alert(response.data.message || '모든 게시글이 삭제되었습니다.');
    await fetchPosts();
  } catch (err) {
    alert(err.response?.data?.detail || '전체 게시글 삭제 중 오류가 발생했습니다.');
  } finally {
    deleting.value = false;
  }
};

// 개별글 삭제
const handleDeleteOne = async (postId) => {
  if (!confirm('이 게시글을 삭제하시겠습니까?')) return;

  try {
    const token = currentUser.value?.access_token || localStorage.getItem('token');
    await axios.delete(`${API_BASE_URL}/board/${postId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    alert('삭제되었습니다.');
    await fetchPosts();
  } catch (err) {
    alert(err.response?.data?.detail || '본인의 게시글만 삭제할 수 있습니다.');
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

onMounted(() => {
  fetchPosts();
});
</script>

<style scoped>
.board-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.board-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.write-btn {
  background-color: #2563eb;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 600;
}

.delete-all-btn {
  background-color: #dc2626;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.delete-all-btn:hover {
  background-color: #b91c1c;
}

.delete-all-btn:disabled {
  background-color: #fca5a5;
  cursor: not-allowed;
}

.board-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.board-table th, .board-table td {
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
  text-align: center;
}

.board-table th {
  background-color: #f8fafc;
  color: #475569;
  font-weight: 600;
}

.col-title {
  text-align: left !important;
}

.col-title a {
  color: #1e293b;
  text-decoration: none;
  font-weight: 500;
}

.col-title a:hover {
  color: #2563eb;
  text-decoration: underline;
}

.small-delete-btn {
  background-color: #ef4444;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
}

.no-perm {
  color: #cbd5e1;
  font-size: 0.9rem;
}

.empty-list, .loading {
  text-align: center;
  padding: 40px;
  color: #64748b;
}
</style>