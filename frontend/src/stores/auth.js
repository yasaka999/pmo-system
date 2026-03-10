import { defineStore } from 'pinia'
import { authApi } from '@/api'
import router from '@/router'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('pmo_token') || '',
        user: null,
    }),
    getters: {
        isLoggedIn: state => !!state.token,
    },
    actions: {
        async init() {
            const userStr = localStorage.getItem('pmo_user')
            if (userStr) {
                try {
                    this.user = JSON.parse(userStr)
                } catch (e) {
                    console.error('Failed to parse user from localStorage', e)
                    this.user = null
                }
            }
        },
        async login(username, password) {
            try {
                const form = new URLSearchParams({ username, password })
                const res = await authApi.login(form)
                
                this.token = res.access_token
                this.user = res.user
                
                localStorage.setItem('pmo_token', res.access_token)
                localStorage.setItem('pmo_user', JSON.stringify(res.user))
                
                await new Promise(resolve => setTimeout(resolve, 100))
                
                window.location.href = '/'
            } catch (error) {
                console.error('Login failed:', error)
                throw error
            }
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
