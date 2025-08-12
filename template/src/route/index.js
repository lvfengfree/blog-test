import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import Article from '../components/Article.vue'
import Login from '../components/Login.vue'
import Dash from '../components/Dash.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/article/:slug', component: Article },
  { path: '/login', component: Login },
  { path: '/dash', component: Dash, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  if (!to.meta.requiresAuth) {
    return next()
  }

  try {
    const res = await fetch('http://localhost:5000/api/check_login', {
      credentials: 'include', // 重要：带上 cookie
    })
    const data = await res.json()
    if (data.logged_in) {
      next()
    } else {
      next('/login')
    }
  } catch (error) {
    next('/login')
  }
})

export default router
