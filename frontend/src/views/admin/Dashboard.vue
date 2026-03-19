<template>
  <div>
    <div class="page-header">
      <div class="page-title">系统仪表盘 <span>数据总览</span></div>
      <button class="btn btn-ghost btn-sm" @click="loadData">🔄 刷新</button>
    </div>

    <!-- 统计卡片 -->
    <div class="stat-grid">
      <div class="stat-card"><div class="stat-num">{{ d.usertotal }}</div><div class="stat-label">注册用户</div></div>
      <div class="stat-card"><div class="stat-num" style="color:#3fb950">{{ d.projdone }}</div><div class="stat-label">已完成项目</div></div>
      <div class="stat-card"><div class="stat-num" style="color:#f85149">{{ d.vulncritical }}</div><div class="stat-label">危急漏洞</div></div>
      <div class="stat-card"><div class="stat-num" style="color:#e3b341">{{ d.vulnhigh }}</div><div class="stat-label">高危漏洞</div></div>
      <div class="stat-card"><div class="stat-num">{{ d.vulntotal }}</div><div class="stat-label">漏洞总数</div></div>
      <div class="stat-card"><div class="stat-num" style="color:#3fb950">{{ d.vulnfixed }}</div><div class="stat-label">已修复漏洞</div></div>
      <div class="stat-card"><div class="stat-num">{{ d.reporttotal }}</div><div class="stat-label">审计报告</div></div>
      <div class="stat-card"><div class="stat-num">{{ d.ruletotal }}</div><div class="stat-label">启用规则</div></div>
    </div>

    <!-- 漏洞分布 -->
    <div class="card" style="margin-top:24px;">
      <div class="section-title">各项目漏洞 TOP5</div>
      <div v-if="d.trend && d.trend.length" class="trend-list">
        <div v-for="item in d.trend" :key="item.pname" class="trend-item">
          <span class="trend-name">{{ item.pname }}</span>
          <div class="trend-bar-wrap">
            <div class="trend-bar" :style="{width: Math.min(100, item.cnt / maxCnt * 100) + '%'}"></div>
          </div>
          <span class="trend-cnt">{{ item.cnt }}</span>
        </div>
      </div>
      <div v-else class="empty-state"><p>暂无数据</p></div>
    </div>

    <!-- 快捷入口 -->
    <div class="card" style="margin-top:16px;">
      <div class="section-title">快捷操作</div>
      <div class="quick-links">
        <RouterLink to="/admin/users" class="quick-btn">👥 用户管理</RouterLink>
        <RouterLink to="/admin/projects" class="quick-btn">📁 项目管理</RouterLink>
        <RouterLink to="/admin/rules" class="quick-btn">📋 规则管理</RouterLink>
        <RouterLink to="/admin/vulns" class="quick-btn">🐛 漏洞管理</RouterLink>
        <RouterLink to="/admin/reports" class="quick-btn">📄 审计报告</RouterLink>
        <RouterLink to="/admin/settings" class="quick-btn">⚙️ 系统设置</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { systemApi } from '@/api/index.js'

const d = ref({
  usertotal:0, projtotal:0, projdone:0, vulntotal:0,
  vulncritical:0, vulnhigh:0, vulnfixed:0, reporttotal:0, ruletotal:0, trend:[]
})

const maxCnt = computed(() => Math.max(...(d.value.trend?.map(i=>i.cnt) || [1]), 1))

async function loadData() {
  const res = await systemApi.dashboard()
  if (res.code === 200) d.value = res.data
}
onMounted(loadData)
</script>

<style scoped>
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.section-title { font-size: 14px; font-weight: 600; margin-bottom: 16px; color: var(--text-primary); }
.trend-list { display: flex; flex-direction: column; gap: 12px; }
.trend-item { display: flex; align-items: center; gap: 12px; }
.trend-name { width: 160px; font-size: 13px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.trend-bar-wrap { flex: 1; background: var(--bg-hover); border-radius: 4px; height: 8px; overflow: hidden; }
.trend-bar { height: 100%; background: var(--accent); border-radius: 4px; transition: width 0.5s ease; }
.trend-cnt { width: 30px; text-align: right; font-size: 13px; color: var(--text-secondary); }
.quick-links { display: flex; gap: 10px; flex-wrap: wrap; }
.quick-btn {
  padding: 10px 18px; background: var(--bg-hover); border: 1px solid var(--border-color);
  border-radius: 8px; color: var(--text-primary); text-decoration: none; font-size: 13px;
  transition: border-color 0.15s;
}
.quick-btn:hover { border-color: var(--accent-light); color: var(--accent-light); text-decoration: none; }
</style>

