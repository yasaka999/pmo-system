import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './style.css'

async function initApp() {
    const app = createApp(App)
    const pinia = createPinia()

    app.use(pinia)
    app.use(router)
    app.use(ElementPlus, { locale: zhCn })

    // 注册所有图标
    for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
        app.component(key, component)
    }

    // 初始化 auth store（从 localStorage 恢复用户信息）
    const auth = useAuthStore()
    await auth.init()

    app.mount('#app')
}

initApp()
