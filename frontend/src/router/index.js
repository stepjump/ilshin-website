
import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';
import BoardView from '../views/BoardView.vue';
import HomeView from '../views/HomeView.vue' // ★ 이 줄이 누락되어 발생한 오류입니다!

const routes = [
  {
    path: '/',
    redirect: HomeView // 홈페이지 처음 방문 시 로드됨
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
  },
  {
    path: '/board',
    name: 'Board',
    component: BoardView,
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;