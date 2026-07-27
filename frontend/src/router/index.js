import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue';
import BoardView from '../views/BoardView.vue';
import AboutView from '../views/AboutView.vue'; // ★ 회사소개 뷰 임포트

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/about',
    name: 'About',
    component: AboutView // ★ 자유게시판 왼쪽 회사소개 페이지
  },
  {
    path: '/board',
    name: 'Board',
    component: BoardView
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

export default router;