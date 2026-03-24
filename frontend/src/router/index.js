import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user.js'

const routes = [
  { path: '/',        redirect: '/login' },
  { path: '/login',   component: () => import('@/views/auth/LoginPage.vue'),    meta: { guest: true } },
  { path: '/register',component: () => import('@/views/auth/RegisterPage.vue'), meta: { guest: true } },
  { path: '/forgot',  component: () => import('@/views/auth/ForgotPasswd.vue'), meta: { guest: true } },

  // 管理员布局
  {
    path: '/admin',
    component: () => import('@/components/AdminLayout.vue'),
    meta: { requireAuth: true, role: 1 },
    children: [
      { path: '',          redirect: '/admin/dashboard' },
      { path: 'dashboard', component: () => import('@/views/admin/Dashboard.vue') },
      { path: 'users',     component: () => import('@/views/admin/UserList.vue') },
      { path: 'projects',  component: () => import('@/views/admin/ProjectList.vue') },
      { path: 'projects/:pid/vulns', component: () => import('@/views/admin/ProjectVulns.vue') },
      { path: 'rules',     component: () => import('@/views/admin/RuleList.vue') },
      { path: 'vulns',     component: () => import('@/views/admin/VulnManage.vue') },
      { path: 'reports',   component: () => import('@/views/admin/ReportList.vue') },
      { path: 'reports/:repid', component: () => import('@/views/admin/ReportDetail.vue') },
      { path: 'settings',  component: () => import('@/views/admin/SystemSettings.vue') },
      { path: 'backup',    component: () => import('@/views/admin/BackupManage.vue') },
      { path: 'profile',   component: () => import('@/views/common/ProfilePage.vue') },
    ]
  },

  // 审计员布局
  {
    path: '/auditor',
    component: () => import('@/components/AuditorLayout.vue'),
    meta: { requireAuth: true, role: 2 },
    children: [
      { path: '',           redirect: '/auditor/workbench' },
      { path: 'workbench',  component: () => import('@/views/auditor/Workbench.vue') },
      { path: 'projects',   component: () => import('@/views/auditor/ProjectSelect.vue') },
      { path: 'projects/:pid/scan', component: () => import('@/views/auditor/ScanControl.vue') },
      { path: 'projects/:pid/vulns', component: () => import('@/views/auditor/VulnList.vue') },
      { path: 'vulns/:vid', component: () => import('@/views/auditor/VulnDetail.vue') },
      { path: 'reports',    component: () => import('@/views/auditor/ReportHistory.vue') },
      { path: 'reports/generate', component: () => import('@/views/auditor/ReportGenerate.vue') },
      { path: 'reports/:repid',   component: () => import('@/views/auditor/ReportView.vue') },
      { path: 'profile',    component: () => import('@/views/common/ProfilePage.vue') },
    ]
  },

  { path: '/:pathMatch(.*)*', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to) => {
  const store = useUserStore()
  // 未登录且需要认证 → 去登录
  if (to.meta.requireAuth && !store.isLoggedIn) return '/login'
  // 已登录访问游客页 → 去首页
  if (to.meta.guest && store.isLoggedIn) {
    return store.isAdmin ? '/admin/dashboard' : '/auditor/workbench'
  }
  // 仅对顶层路由做角色检查（matched[0] 是最外层路由）
  if (store.isLoggedIn && to.matched.length > 0) {
    const topMeta = to.matched[0].meta
    if (topMeta.role && store.user?.rolecode !== topMeta.role) {
      return store.isAdmin ? '/admin/dashboard' : '/auditor/workbench'
    }
  }
})

export default router

