<template>
  <div>
    <div class="page-header">
      <div class="page-title">
        👋 欢迎，{{ store.user?.realname }}
        <span>个人工作台</span>
      </div>
    </div>

    <!-- 统计卡 -->
    <div class="stat-grid" style="margin-bottom:24px">
      <div class="stat-card">
        <div class="stat-num">{{ wb.scancnt }}</div>
        <div class="stat-label">扫描任务</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color:#f85149">{{ wb.vulnfound }}</div>
        <div class="stat-label">发现漏洞</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color:#3fb950">{{ wb.reportcnt }}</div>
        <div class="stat-label">生成报告</div>
      </div>
    </div>

    <!-- 最近扫描任务 -->
    <div class="card">
      <div class="section-title">📋 最近扫描任务</div>
      <table class="data-table" v-if="wb.recenttasks?.length">
        <thead><tr><th>任务ID</th><th>项目名称</th><th>状态</th><th>进度</th><th>开始时间</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="t in wb.recenttasks" :key="t.tid">
            <td>{{ t.tid }}</td>
            <td>{{ t.pname }}</td>
            <td><span :class="taskClass(t.status)">{{ taskText(t.status) }}</span></td>
            <td>
              <div class="progress-bar-wrap" style="width:100px;display:inline-block">
                <div class="progress-bar-fill" :style="{width:t.progress+'%'}"></div>
              </div>
              <span style="font-size:12px;margin-left:6px;color:var(--text-secondary)">{{ t.progress }}%</span>
            </td>
            <td>{{ t.starttime?.slice(0,16) || '—' }}</td>
            <td>
              <RouterLink :to="`/auditor/projects/${t.pid}/scan`" class="btn btn-ghost btn-sm">查看</RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="empty-state" v-else><div class="icon">📭</div><p>暂无扫描记录</p></div>
    </div>

    <!-- 快捷入口 -->
    <div class="card" style="margin-top:16px">
      <div class="section-title">⚡ 快捷操作</div>
      <div class="quick-links">
        <RouterLink to="/auditor/projects" class="quick-btn">📁 选择项目扫描</RouterLink>
        <RouterLink to="/auditor/reports/generate" class="quick-btn">✏️ 生成审计报告</RouterLink>
        <RouterLink to="/auditor/reports" class="quick-btn">📄 查看历史报告</RouterLink>
        <RouterLink to="/auditor/profile" class="quick-btn">⚙️ 个人设置</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { systemApi } from '@/api/index.js'
import { useUserStore } from '@/stores/user.js'

const store=useUserStore()
const wb=ref({scancnt:0,vulnfound:0,reportcnt:0,recenttasks:[]})

const taskText=s=>({0:'等待',1:'进行中',2:'已完成',3:'已暂停',4:'失败'}[s]??'未知')
const taskClass=s=>({0:'badge badge-default',1:'badge badge-info',2:'badge badge-success',3:'badge badge-medium',4:'badge badge-high'}[s]??'badge')

async function loadData(){
  const res=await systemApi.workbench(store.user?.uid)
  if(res.code===200)wb.value=res.data
}
onMounted(loadData)
</script>

<style scoped>
.stat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.section-title{font-size:14px;font-weight:600;margin-bottom:14px}
.quick-links{display:flex;gap:10px;flex-wrap:wrap}
.quick-btn{padding:10px 18px;background:var(--bg-hover);border:1px solid var(--border-color);border-radius:8px;color:var(--text-primary);text-decoration:none;font-size:13px;transition:border-color 0.15s}
.quick-btn:hover{border-color:var(--accent-light);color:var(--accent-light);text-decoration:none}
</style>

