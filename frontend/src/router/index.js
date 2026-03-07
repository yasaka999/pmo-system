import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
    { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
    {
        path: '/',
        component: () => import('@/layouts/MainLayout.vue'),
        children: [
            { path: '', redirect: '/dashboard' },
            { path: 'dashboard', component: () => import('@/views/DashboardView.vue'), meta: { title: '项目总览' } },
            { path: 'projects', component: () => import('@/views/ProjectListView.vue'), meta: { title: '项目列表' } },
            { path: 'projects/:id', component: () => import('@/views/ProjectDetailView.vue'), meta: { title: '项目详情' } },
            { path: 'projects/:id/milestones', component: () => import('@/views/MilestoneView.vue'), meta: { title: '里程碑与进度' } },
            { path: 'projects/:id/issues', component: () => import('@/views/IssueView.vue'), meta: { title: '问题台账' } },
            { path: 'projects/:id/risks', component: () => import('@/views/RiskView.vue'), meta: { title: '风险台账' } },
            { path: 'projects/:id/mandays', component: () => import('@/views/ManDayView.vue'), meta: { title: '人天管理' } },
            { path: 'projects/:id/weekly-progress', component: () => import('@/views/WeeklyProgressView.vue'), meta: { title: '周报进展' } },
            { path: 'projects/:id/reports', component: () => import('@/views/ReportView.vue'), meta: { title: '报告生成' } },
            { path: 'system/users', component: () => import('@/views/UserListView.vue'), meta: { title: '用户管理', adminOnly: true } },
            { path: 'system/config', component: () => import('@/views/SystemConfigView.vue'), meta: { title: '系统配置', adminOnly: true } },
            { path: 'portfolio-report', component: () => import('@/views/PortfolioReportView.vue'), meta: { title: '整体报告' } },
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

router.beforeEach((to) => {
    const auth = useAuthStore()
    if (!to.meta.public && !auth.isLoggedIn) {
        return '/login'
    }
})

export default router
