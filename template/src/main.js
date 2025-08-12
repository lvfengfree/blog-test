import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './route'  // 注意你之前写的是 './route'，确认目录名是 router

createApp(App)
  .use(router)    // 挂载路由插件
  .mount('#app')
