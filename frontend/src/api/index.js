import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const api = axios.create({
    baseURL: '/api/v1',
    timeout: 30000,
})

// 请求拦截：自动附加Token
api.interceptors.request.use(config => {
    const auth = useAuthStore()
    if (auth.token) {
        config.headers.Authorization = `Bearer ${auth.token}`
    }
    return config
})

// 响应拦截：统一错误处理
api.interceptors.response.use(
    res => res.data,
    err => {
        const msg = err.response?.data?.detail || err.message || '请求失败'
        if (err.response?.status === 401) {
            useAuthStore().logout()
        } else {
            ElMessage.error(msg)
        }
        return Promise.reject(err)
    }
)

// ─── 认证 ─────────────────────────────────────
export const authApi = {
    login: (data) => api.post('/auth/login', data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }),
    me: () => api.get('/auth/me'),
    register: (data) => api.post('/auth/register', data),
}
// ─── 用户管理 ──────────────────────────────────
export const userApi = {
    list: (params) => api.get('/users/', { params }),
    create: (data) => api.post('/users/', data),
    update: (id, data) => api.put(`/users/${id}`, data),
    updateStatus: (id, isActive) => api.put(`/users/${id}/status`, { is_active: isActive }),
    remove: (id) => api.delete(`/users/${id}`),
    changePassword: (data) => api.put('/users/me/password', data),
}

// ─── 数据字典 ──────────────────────────────────
export const dictApi = {
    list: (params) => api.get('/sys-dicts/', { params }),
    create: (data) => api.post('/sys-dicts/', data),
    update: (id, data) => api.put(`/sys-dicts/${id}`, data),
    remove: (id) => api.delete(`/sys-dicts/${id}`),
    batchSave: (items) => api.post('/sys-dicts/batch-save', { items }),
}

// ─── 项目 ─────────────────────────────────────
export const projectApi = {
    list: (params) => api.get('/projects/', { params }),
    listWithStats: () => api.get('/projects/all-with-stats'),  // 聚合 API（含统计数据）
    get: (id) => api.get(`/projects/${id}`),
    create: (data) => api.post('/projects/', data),
    update: (id, data) => api.put(`/projects/${id}`, data),
    remove: (id) => api.delete(`/projects/${id}`),
}

// ─── 里程碑 ───────────────────────────────────
export const milestoneApi = {
    list: (pid) => api.get(`/projects/${pid}/milestones`),
    create: (pid, data) => api.post(`/projects/${pid}/milestones`, data),
    update: (id, data) => api.put(`/milestones/${id}`, data),
    remove: (id) => api.delete(`/milestones/${id}`),
}

// ─── 任务 ─────────────────────────────────────
export const taskApi = {
    list: (pid) => api.get(`/projects/${pid}/tasks`),
    create: (pid, data) => api.post(`/projects/${pid}/tasks`, data),
    update: (id, data) => api.put(`/tasks/${id}`, data),
    remove: (id) => api.delete(`/tasks/${id}`),
}

// ─── 问题 ─────────────────────────────────────
export const issueApi = {
    list: (pid, params) => api.get(`/projects/${pid}/issues`, { params }),
    create: (pid, data) => api.post(`/projects/${pid}/issues`, data),
    update: (id, data) => api.put(`/issues/${id}`, data),
    remove: (id) => api.delete(`/issues/${id}`),
}

// ─── 风险 ─────────────────────────────────────
export const riskApi = {
    list: (pid, params) => api.get(`/projects/${pid}/risks`, { params }),
    create: (pid, data) => api.post(`/projects/${pid}/risks`, data),
    update: (id, data) => api.put(`/risks/${id}`, data),
    remove: (id) => api.delete(`/risks/${id}`),
}

// ─── 人天 ─────────────────────────────────────
export const mandayApi = {
    list: (pid, params) => api.get(`/projects/${pid}/mandays`, { params }),
    create: (pid, data) => api.post(`/projects/${pid}/mandays`, data),
    update: (id, data) => api.put(`/mandays/${id}`, data),
    remove: (id) => api.delete(`/mandays/${id}`),
    stats: (pid) => api.get(`/projects/${pid}/mandays/stats`),
}

// ─── 周报进展 ──────────────────────────────────
export const weeklyProgressApi = {
    list: (pid) => api.get(`/projects/${pid}/weekly-progress`),
    create: (pid, data) => api.post(`/projects/${pid}/weekly-progress`, data),
    update: (id, data) => api.put(`/weekly-progress/${id}`, data),
    remove: (id) => api.delete(`/weekly-progress/${id}`),
}

// ─── 报告 ─────────────────────────────────────
export const reportApi = {
    weekly: (pid, date) => {
        const params = date ? { report_date: date } : {}
        return axios.get(`/api/v1/projects/${pid}/reports/weekly`, {
            params,
            responseType: 'blob',
            headers: { Authorization: `Bearer ${useAuthStore().token}` }
        })
    },
    monthly: (pid, year, month) => axios.get(`/api/v1/projects/${pid}/reports/monthly`, {
        params: { year, month },
        responseType: 'blob',
        headers: { Authorization: `Bearer ${useAuthStore().token}` }
    }),
    issueRisk: (pid) => axios.get(`/api/v1/projects/${pid}/reports/issues-risks`, {
        responseType: 'blob',
        headers: { Authorization: `Bearer ${useAuthStore().token}` }
    }),
    mandays: (pid) => axios.get(`/api/v1/projects/${pid}/reports/mandays`, {
        responseType: 'blob',
        headers: { Authorization: `Bearer ${useAuthStore().token}` }
    }),
    statusOverview: () => axios.get(`/api/v1/reports/status-overview`, {
        responseType: 'blob',
        headers: { Authorization: `Bearer ${useAuthStore().token}` }
    }),
    portfolioWord: (params) => axios.get(`/api/v1/reports/portfolio/word`, {
        responseType: 'blob',
        headers: { Authorization: `Bearer ${useAuthStore().token}` },
        params
    }),
    portfolioExcel: (params) => axios.get(`/api/v1/reports/portfolio/excel`, {
        responseType: 'blob',
        headers: { Authorization: `Bearer ${useAuthStore().token}` },
        params
    }),
    weeklySummary: (params) => api.get('/reports/weekly-summary', { params }),
    weeklySummaryExcel: (params) => axios.get(`/api/v1/reports/weekly-summary/excel`, {
        responseType: 'blob',
        headers: { Authorization: `Bearer ${useAuthStore().token}` },
        params
    }),
}

// 通用下载函数
export function downloadBlob(response, filename) {
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    window.URL.revokeObjectURL(url)
}

export default api
