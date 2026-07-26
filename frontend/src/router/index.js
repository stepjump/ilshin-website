
import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';
import BoardView from '../views/BoardView.vue';

const routes = [
  {
    path: '/',
    redirect: '/board',
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