import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import AboutView from '../views/AboutView.vue';
import BoardView from '../views/BoardView.vue';
import BoardWriteView from '../views/BoardWriteView.vue';
import BoardDetailView from '../views/BoardDetailView.vue'; // ★ 상세화면 컴포넌트 임포트
import LoginView from '../views/LoginView.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/about',
    name: 'about',
    component: AboutView,
  },
  {
    path: '/board',
    name: 'board',
    component: BoardView,
  },
  {
    path: '/board/write',
    name: 'board-write',
    component: BoardWriteView,
  },
  {
    // ★ 게시글 상세페이지 동적 경로 연결 (/board/1, /board/2 ...)
    path: '/board/:id',
    name: 'board-detail',
    component: BoardDetailView,
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;