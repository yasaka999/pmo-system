import { defineStore } from 'pinia'
import { authApi } from '@/api'
import router from '@/router'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('pmo_token') || '',
        user: JSON.parse(localStorage.getItem('pmo_user') || 'null'),
    }),
    getters: {
        isLoggedIn: s => !!s.token,
    },
    actions: {
        async login(username, password) {
            const form = new URLSearchParams({ username, password })
            const res = await authApi.login(form)
            this.token = res.access_token
            this.user = res.user
            localStorage.setItem('pmo_token', res.access_token)
            localStorage.setItem('pmo_user', JSON.stringify(res.user))
            router.push('/')
        },
        logout() {
            this.token = ''
            this.user = null
            localStorage.removeItem('pmo_token')
            localStorage.removeItem('pmo_user')
            router.push('/login')
        }
    }
})
