<template>
  <div class="board-container">
    <h2>자유 게시판</h2>

    <!-- 새 글 작성 폼 -->
    <div class="write-box">
      <h3>새 글 작성</h3>
      <form @submit.prevent="handleCreate">
        <input 
          v-model="title" 
          placeholder="제목을 입력하세요" 
          required 
          class="input-field" 
        />
        <textarea 
          v-model="content" 
          placeholder="내용을 입력하세요" 
          required 
          class="textarea-field"
        ></textarea>
        
        <!-- 비회원 작성 시에만 작성자명/비밀번호 입력 -->
        <div v-if="!isLoggedIn" class="guest-info">
          <input v-model="authorName" placeholder="작성자 이름" required />
          <input v-model="guestPassword" type="password" placeholder="비회원 비밀번호" required />
        </div>

        <button type="submit" :disabled="submitting">
          {{ submitting ? '등록 중...' : '글등록' }}
        </button>
      </form>
    </div>

    <hr />

    <!-- 게시글 목록 -->
    <div v-if="loading" class="loading-text">게시글을 불러오는 중입니다...</div>
    <ul v-else-if="posts.length > 0" class="post-list">
      <li v-for="post in posts" :key="post.id" class="post-item">
        <h4>{{ post.title }}</h4>
        <p class="post-content">{{ post.content }}</p>
        <div class="meta">
          <!-- author_name 또는 author 중 존재하는 값 표시 -->
          <span>작성자: {{ post.author_name || post.author || '익명' }}</span>
          <span> | {{ post.created_at ? new Date(post.created_at).toLocaleDateString() : '' }}</span>
        </div>
        <button @click="handleDelete(post.id)" class="del-btn">삭제</button>
      </li>
    </ul>
    <div v-else class="empty-text">등록된 게시글이 없습니다.</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { boardApi } from '../api/board';
import { useAuth } from '../composables/useAuth';

const { isLoggedIn, currentUser } = useAuth();

const posts = ref([]);
const loading = ref(true);
const submitting = ref(false);

const title = ref('');
const content = ref('');
const authorName = ref('');
const guestPassword = ref('');

// 게시글 목록 가져오기
const fetchPosts = async () => {
  loading.value = true;
  try {
    const res = await boardApi.getBoards('free');
    posts.value = res.data;
  } catch (err) {
    console.error('게시글 조회 오류:', err);
    alert('게시글 목록을 가져오지 못했습니다.');
  } finally {
    loading.value = false;
  }
};

// 게시글 등록
const handleCreate = async () => {
  submitting.value = true;
  try {
    let finalAuthorName = '';

    if (isLoggedIn.value) {
      const userObj = currentUser.value || currentUser || {};
      finalAuthorName = userObj.name 
                     || userObj.user_name 
                     || userObj.username 
                     || (userObj.email ? userObj.email.split('@')[0] : '회원');
    } else {
      finalAuthorName = authorName.value;
    }

    const payload = {
      title: title.value,
      content: content.value,
      author_name: finalAuthorName || '익명',
      password: isLoggedIn.value ? undefined : guestPassword.value
    };

    await boardApi.createBoard('free', payload);
    alert('게시글이 성공적으로 등록되었습니다.');
    
    // 입력 폼 초기화 및 목록 새로고침
    title.value = '';
    content.value = '';
    authorName.value = '';
    guestPassword.value = '';
    await fetchPosts();
  } catch (err) {
    console.error('글 작성 오류:', err);
    alert('글 작성 실패: ' + (err.response?.data?.detail || err.message));
  } finally {
    submitting.value = false;
  }
};

// 게시글 삭제
const handleDelete = async (boardId) => {
  let password = null;
  if (!isLoggedIn.value) {
    password = prompt('비회원글 삭제를 위해 설정한 비밀번호를 입력하세요:');
    if (!password) return;
  } else {
    if (!confirm('정말 삭제하시겠습니까?')) return;
  }

  try {
    await boardApi.deleteBoard('free', boardId, password);
    alert('삭제되었습니다.');
    await fetchPosts();
  } catch (err) {
    console.error('글 삭제 오류:', err);
    alert('삭제 실패: ' + (err.response?.data?.detail || '권한이 없거나 비밀번호가 틀렸습니다.'));
  }
};

onMounted(() => {
  fetchPosts();
});
</script>

<style scoped>
.board-container { max-width: 800px; margin: 30px auto; padding: 20px; }
.write-box { background: #f9f9f9; padding: 20px; border-radius: 8px; margin-bottom: 25px; border: 1px solid #eee; }
.input-field, .textarea-field { width: 100%; margin-bottom: 12px; padding: 10px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
.textarea-field { height: 100px; resize: vertical; }
.guest-info { display: flex; gap: 10px; margin-bottom: 12px; }
.guest-info input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
button { padding: 10px 20px; background-color: #42b983; color: white; border: none; border-radius: 4px; cursor: pointer; }
button:disabled { background-color: #a8d8c0; }
.post-list { list-style: none; padding: 0; margin-top: 20px; }
.post-item { border-bottom: 1px solid #eee; padding: 15px 0; position: relative; }
.post-content { color: #444; margin: 8px 0; white-space: pre-line; }
.meta { font-size: 0.85rem; color: #888; }
.del-btn { position: absolute; right: 0; top: 15px; background: #ff4d4f; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.85rem; }
.loading-text, .empty-text { text-align: center; color: #777; padding: 30px 0; }
</style>