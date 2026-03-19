<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <span class="logo-icon">🛡</span>
        <span class="logo-text">代码审计平台</span>
      </div>
      <nav class="sidebar-nav">
        <div class="nav-section-title">总览</div>
        <RouterLink to="/admin/dashboard" class="nav-item">
          <span class="nav-icon">📊</span> 系统仪表盘
        </RouterLink>
        <div class="nav-section-title">管理</div>
        <RouterLink to="/admin/users" class="nav-item">
          <span class="nav-icon">👥</span> 用户管理
        </RouterLink>
        <RouterLink to="/admin/projects" class="nav-item">
          <span class="nav-icon">📁</span> 项目管理
        </RouterLink>
        <RouterLink to="/admin/rules" class="nav-item">
          <span class="nav-icon">📋</span> 规则管理
        </RouterLink>
        <RouterLink to="/admin/vulns" class="nav-item">
          <span class="nav-icon">🐛</span> 漏洞管理
        </RouterLink>
        <RouterLink to="/admin/reports" class="nav-item">
          <span class="nav-icon">📄</span> 审计报告
        </RouterLink>
        <div class="nav-section-title">系统</div>
        <RouterLink to="/admin/settings" class="nav-item">
          <span class="nav-icon">⚙️</span> 系统设置
        </RouterLink>
        <RouterLink to="/admin/backup" class="nav-item">
          <span class="nav-icon">💾</span> 数据备份
        </RouterLink>
      </nav>
      <div class="sidebar-footer">
        <RouterLink to="/admin/profile" class="nav-item">
          <span class="nav-icon">👤</span> {{ store.user?.realname }}
        </RouterLink>
        <button class="nav-item logout-btn" @click="logout">
          <span class="nav-icon">🚪</span> 退出登录
        </button>
      </div>
    </aside>
    <!-- 主内容区 -->
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user.js'

const store  = useUserStore()
const router = useRouter()
function logout() {
  store.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout { display: flex; height: 100vh; overflow: hidden; }

.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: var(--bg-panel);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 16px;
  border-bottom: 1px solid var(--border-color);
  font-weight: 700;
  font-size: 14px;
  color: var(--text-primary);
}
.logo-icon { font-size: 20px; }

.sidebar-nav { flex: 1; padding: 12px 0; }
.nav-section-title {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-muted);
  padding: 12px 16px 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  color: var(--text-secondary);
  font-size: 13px;
  text-decoration: none;
  border-radius: 0;
  transition: color 0.15s, background 0.15s;
  cursor: pointer;
  width: 100%;
  text-align: left;
  border: none;
  background: transparent;
  font-family: inherit;
}
.nav-item:hover { background: var(--bg-hover); color: var(--text-primary); }
.nav-item.router-link-active { color: var(--accent-light); background: #1b2a3e; }
.nav-icon { font-size: 15px; width: 18px; text-align: center; }

.sidebar-footer {
  border-top: 1px solid var(--border-color);
  padding: 8px 0;
}
.logout-btn { color: var(--danger-light); }

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: var(--bg-dark);
}
</style>

