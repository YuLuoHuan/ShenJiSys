<template>
  <div>
    <div class="page-header">
      <div class="page-title">
        <RouterLink to="/auditor/projects" style="color:var(--text-secondary);font-size:14px">← 项目列表</RouterLink>
        <span style="margin:0 8px;color:var(--text-muted)">/</span>
        扫描结果 <span>共 {{ total }} 条漏洞</span>
      </div>
      <a :href="exportUrl" class="btn btn-ghost btn-sm">⬇ 导出CSV</a>
    </div>

    <!-- 漏洞分布统计 -->
    <div class="sev-bar-row" v-if="stats.byseverity?.length">
      <div v-for="s in sevList" :key="s.val" class="sev-bar-item">
        <span :class="s.cls">{{ s.label }}</span>
        <span class="sev-cnt">{{ getSevCnt(s.val) }}</span>
      </div>
    </div>

    <div class="card" style="margin-top:16px">
      <div class="toolbar">
        <select v-model="filterSev" class="form-control" style="width:130px" @change="loadList">
          <option value="">全部等级</option>
          <option value="4">危急</option><option value="3">高危</option>
          <option value="2">中危</option><option value="1">低危</option>
        </select>
        <select v-model="filterState" class="form-control" style="width:130px" @change="loadList">
          <option value="">全部状态</option>
          <option value="0">未处理</option><option value="1">已确认</option>
          <option value="2">误报</option><option value="3">已修复</option>
        </select>
        <input v-model="keyword" class="form-control" style="width:200px" placeholder="文件路径搜索" @keyup.enter="loadList" />
      </div>
      <table class="data-table">
        <thead><tr><th>ID</th><th>规则</th><th>类别</th><th>文件</th><th>行号</th><th>等级</th><th>状态</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="v in list" :key="v.vid">
            <td>{{ v.vid }}</td>
            <td>{{ v.rname }}</td>
            <td>{{ v.category }}</td>
            <td><span class="file-path">{{ shortPath(v.filepath) }}</span></td>
            <td>{{ v.lineno }}</td>
            <td><span :class="sevClass(v.severity)">{{ sevText(v.severity) }}</span></td>
            <td><span :class="stateClass(v.vulnstate)">{{ stateText(v.vulnstate) }}</span></td>
            <td>
              <RouterLink :to="`/auditor/vulns/${v.vid}`" class="btn btn-ghost btn-sm">详情</RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="empty-state" v-if="!list.length"><div class="icon">🎉</div><p>未发现任何漏洞</p></div>
      <div class="pagination">
        <button class="page-btn" :disabled="page<=1" @click="page--;loadList()">上一页</button>
        <span class="page-btn active">{{ page }}</span>
        <button class="page-btn" :disabled="page*size>=total" @click="page++;loadList()">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { vulnApi } from '@/api/index.js'

const route=useRoute()
const pid=route.params.pid
const list=ref([]),total=ref(0),page=ref(1),size=ref(20)
const filterSev=ref(''),filterState=ref(''),keyword=ref('')
const stats=ref({byseverity:[]})

const exportUrl=computed(()=>vulnApi.exportUrl({pid}))
const sevText=s=>({1:'低危',2:'中危',3:'高危',4:'危急'}[s]??'未知')
const sevClass=s=>({1:'badge badge-low',2:'badge badge-medium',3:'badge badge-high',4:'badge badge-critical'}[s]??'badge')
const stateText=s=>({0:'未处理',1:'已确认',2:'误报',3:'已修复'}[s]??'未知')
const stateClass=s=>({0:'badge badge-default',1:'badge badge-info',2:'badge badge-medium',3:'badge badge-success'}[s]??'badge')
const shortPath=p=>p&&p.length>40?'...'+p.slice(-40):p
const sevList=[{val:4,label:'危急',cls:'badge badge-critical'},{val:3,label:'高危',cls:'badge badge-high'},{val:2,label:'中危',cls:'badge badge-medium'},{val:1,label:'低危',cls:'badge badge-low'}]
const getSevCnt=val=>{const f=stats.value.byseverity?.find(s=>s.severity===val);return f?.cnt||0}

async function loadList(){
  const res=await vulnApi.list({pid,page:page.value,size:size.value,severity:filterSev.value,vulnstate:filterState.value,keyword:keyword.value})
  if(res.code===200){list.value=res.data.list;total.value=res.data.total}
}
async function loadStats(){
  const res=await vulnApi.stats({pid})
  if(res.code===200)stats.value=res.data
}
onMounted(()=>{loadList();loadStats()})
</script>

<style scoped>
.sev-bar-row{display:flex;gap:12px;margin-bottom:4px}
.sev-bar-item{display:flex;align-items:center;gap:6px;font-size:13px}
.sev-cnt{font-weight:700;color:var(--text-primary)}
.file-path{font-family:var(--font-mono);font-size:11px;color:var(--text-secondary)}
</style>

