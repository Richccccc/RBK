import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../pages/HomePage.vue'),
    },
    {
      path: '/diary',
      name: 'diary',
      component: () => import('../pages/HomePage.vue'),
      meta: { postType: 'diary' },
    },
    {
      path: '/templates',
      name: 'templates',
      component: () => import('../pages/HomePage.vue'),
    },
    {
      path: '/guestbook',
      name: 'guestbook',
      component: () => import('../pages/HomePage.vue'),
    },
    {
      path: '/sheets',
      redirect: '/templates',
    },
    {
      path: '/post/:id',
      name: 'post',
      component: () => import('../pages/BlogDetailPage.vue'),
    },
    {
      path: '/new',
      name: 'new',
      component: () => import('../pages/NewBlogPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/edit/:id',
      name: 'edit',
      component: () => import('../pages/NewBlogPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../pages/LoginPage.vue'),
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  // 登录页：已登录则直接回首页
  if (to.name === 'login') {
    return auth.isLogin ? { name: 'home' } : true
  }
  // 其余页面一律需要登录，未登录进入即跳登录页
  if (!auth.isLogin) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  return true
})

export default router