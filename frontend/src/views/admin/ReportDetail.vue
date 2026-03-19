<template>
  <div>
    <div class="page-header">
      <div class="page-title">
        <RouterLink to="/admin/reports" style="color:var(--text-secondary);font-size:14px">← 报告列表</RouterLink>
        <span style="margin:0 8px;color:var(--text-muted)">/</span>
        报告详情
      </div>
      <a v-if="rep" :href="downloadUrl(rep.repid)" class="btn btn-primary btn-sm">⬇ 下载PDF</a>
    </div>
    <div v-if="rep">
      <div class="card" style="margin-bottom:16px">
        <div class="detail-row"><span class="dl">报告名称</span><span>{{ rep.repname }}</span></div>
        <div class="detail-row"><span class="dl">所属项目</span><span>{{ rep.pname }}</span></div>
        <div class="detail-row"><span class="dl">生成时间</span><span>{{ rep.createtime }}</span></div>
        <div class="detail-row"><span class="dl">报告摘要</span><span>{{ rep.summary }}</span></div>
      </div>
      <div class="card">
        <div class="section-title">漏洞清单（共 {{ rep.vulns?.length || 0 }} 条）</div>
        <table class="data-table">
          <thead><tr><th>ID</th><th>规则</th><th>类别</th><th>文件路径</th><th>行号</th><th>等级</th><th>代码片段</th></tr></thead>
          <tbody>
            <tr v-for="v in rep.vulns" :key="v.vid">
              <td>{{ v.vid }}</td>
              <td>{{ v.rname }}</td>
              <td>{{ v.category }}</td>
              <td><span style="font-family:var(--font-mono);font-size:11px">{{ v.filepath }}</span></td>
              <td>{{ v.lineno }}</td>
              <td><span :class="sevClass(v.severity)">{{ sevText(v.severity) }}</span></td>
              <td><code style="font-size:11px;color:var(--text-secondary)">{{ (v.codesnip||'').slice(0,60) }}</code></td>
            </tr>
          </tbody>
        </table>
        <div class="empty-state" v-if="!rep.vulns?.length"><div class="icon">✅</div><p>该报告无漏洞记录</p></div>
      </div>
    </div>
    <div class="empty-state" v-else><div class="icon">⏳</div><p>加载中...</p></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { reportApi } from '@/api/index.js'

const route=useRoute()
const rep=ref(null)
const downloadUrl=repid=>reportApi.download(repid)
const sevText=s=>({1:'低危',2:'中危',3:'高危',4:'危急'}[s]??'未知')
const sevClass=s=>({1:'badge badge-low',2:'badge badge-medium',3:'badge badge-high',4:'badge badge-critical'}[s]??'badge')

async function load(){
  const res=await reportApi.detail(route.params.repid)
  if(res.code===200)rep.value=res.data
}
onMounted(load)
</script>

<style scoped>
.detail-row{display:flex;gap:16px;padding:8px 0;border-bottom:1px solid var(--border-color);font-size:13px}
.dl{width:80px;color:var(--text-muted);flex-shrink:0}
.section-title{font-size:14px;font-weight:600;margin-bottom:14px}
</style>

