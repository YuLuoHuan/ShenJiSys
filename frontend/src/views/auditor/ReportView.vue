<template>
  <div>
    <div class="page-header">
      <div class="page-title">
        <button class="btn btn-ghost btn-sm" @click="$router.back()">← 返回</button>
        <span style="margin-left:8px">报告详情</span>
      </div>
      <a v-if="rep" :href="downloadUrl(rep.repid)" class="btn btn-primary btn-sm">⬇ 下载PDF</a>
    </div>
    <div v-if="rep">
      <div class="card" style="margin-bottom:14px">
        <h2 style="font-size:17px;font-weight:700;margin-bottom:12px;color:var(--text-primary)">{{ rep.repname }}</h2>
        <div class="info-row"><span class="info-label">所属项目</span>{{ rep.pname }}</div>
        <div class="info-row"><span class="info-label">生成时间</span>{{ rep.createtime }}</div>
        <div class="info-row"><span class="info-label">报告摘要</span>{{ rep.summary }}</div>
      </div>
      <!-- 漏洞统计 -->
      <div class="sev-summary">
        <div v-for="s in sevList" :key="s.val" class="sev-item">
          <span :class="s.cls" style="font-size:14px;padding:3px 12px">{{ s.label }}</span>
          <span class="sev-num">{{ getSevCnt(s.val) }}</span>
        </div>
      </div>
      <div class="card" style="margin-top:14px">
        <div class="section-title">漏洞清单（{{ rep.vulns?.length || 0 }} 条）</div>
        <table class="data-table">
          <thead><tr><th>ID</th><th>规则</th><th>文件</th><th>行</th><th>等级</th><th>代码片段</th></tr></thead>
          <tbody>
            <tr v-for="v in rep.vulns" :key="v.vid">
              <td>{{ v.vid }}</td>
              <td>{{ v.rname }}</td>
              <td><span style="font-family:var(--font-mono);font-size:11px">{{ v.filepath?.split('/').slice(-2).join('/') }}</span></td>
              <td>{{ v.lineno }}</td>
              <td><span :class="sevClass(v.severity)">{{ sevText(v.severity) }}</span></td>
              <td><code style="font-size:11px;color:var(--text-secondary)">{{ (v.codesnip||'').slice(0,50) }}</code></td>
            </tr>
          </tbody>
        </table>
        <div class="empty-state" v-if="!rep.vulns?.length"><div class="icon">✅</div><p>无漏洞记录</p></div>
      </div>
    </div>
    <div class="empty-state" v-else><div class="icon">⏳</div><p>加载中...</p></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { reportApi } from '@/api/index.js'

const route=useRoute()
const rep=ref(null)
const downloadUrl=repid=>reportApi.download(repid)
const sevText=s=>({1:'低危',2:'中危',3:'高危',4:'危急'}[s]??'未知')
const sevClass=s=>({1:'badge badge-low',2:'badge badge-medium',3:'badge badge-high',4:'badge badge-critical'}[s]??'badge')
const sevList=[{val:4,label:'危急',cls:'badge badge-critical'},{val:3,label:'高危',cls:'badge badge-high'},{val:2,label:'中危',cls:'badge badge-medium'},{val:1,label:'低危',cls:'badge badge-low'}]
const getSevCnt=val=>rep.value?.vulns?.filter(v=>v.severity===val).length||0

async function load(){
  const res=await reportApi.detail(route.params.repid)
  if(res.code===200)rep.value=res.data
}
onMounted(load)
</script>

<style scoped>
.info-row{display:flex;gap:12px;padding:7px 0;border-bottom:1px solid var(--border-color);font-size:13px}
.info-label{width:80px;color:var(--text-muted);font-size:12px;flex-shrink:0}
.sev-summary{display:flex;gap:16px;margin-bottom:4px}
.sev-item{display:flex;align-items:center;gap:8px}
.sev-num{font-size:22px;font-weight:700;color:var(--text-primary)}
.section-title{font-size:14px;font-weight:600;margin-bottom:12px}
</style>

