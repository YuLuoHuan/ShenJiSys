<template>
  <div>
    <div class="page-header">
      <div class="page-title">选择项目 <span>点击项目进入扫描控制台</span></div>
    </div>
    <div class="toolbar">
      <input v-model="keyword" class="form-control" style="width:240px" placeholder="搜索项目名称" @keyup.enter="loadList" />
      <select v-model="filterStatus" class="form-control" style="width:140px" @change="loadList">
        <option value="">全部状态</option>
        <option value="0">待扫描</option><option value="1">扫描中</option>
        <option value="2">已完成</option><option value="3">已暂停</option>
      </select>
      <button class="btn btn-ghost btn-sm" @click="loadList">刷新</button>
    </div>
    <div class="project-grid">
      <div v-for="p in list" :key="p.pid" class="project-card" @click="gotoScan(p.pid)">
        <div class="proj-header">
          <span class="proj-lang">{{ p.language.toUpperCase() }}</span>
          <span :class="statusClass(p.status)">{{ statusText(p.status) }}</span>
        </div>
        <div class="proj-name">{{ p.pname }}</div>
        <div class="proj-desc">{{ p.pdesc || '暂无描述' }}</div>
        <div class="proj-meta">
          <span>负责人：{{ p.ownername }}</span>
          <span>{{ p.createtime?.slice(0,10) }}</span>
        </div>
      </div>
    </div>
    <div class="empty-state" v-if="!list.length"><div class="icon">📁</div><p>暂无可用项目</p></div>
    <div class="pagination">
      <button class="page-btn" :disabled="page<=1" @click="page--;loadList()">上一页</button>
      <span class="page-btn active">{{ page }}</span>
      <button class="page-btn" :disabled="page*size>=total" @click="page++;loadList()">下一页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { projectApi } from '@/api/index.js'

const router=useRouter()
const list=ref([]),total=ref(0),page=ref(1),size=ref(12)
const keyword=ref(''),filterStatus=ref('')

const statusText=s=>({0:'待扫描',1:'扫描中',2:'已完成',3:'已暂停'}[s]??'未知')
const statusClass=s=>({0:'badge badge-default',1:'badge badge-info',2:'badge badge-success',3:'badge badge-medium'}[s]??'badge')

async function loadList(){
  const res=await projectApi.list({page:page.value,size:size.value,keyword:keyword.value})
  if(res.code===200){list.value=res.data.list;total.value=res.data.total}
}
function gotoScan(pid){ router.push(`/auditor/projects/${pid}/scan`) }
onMounted(loadList)
</script>

<style scoped>
.project-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px;margin-bottom:16px}
.project-card{
  background:var(--bg-card);border:1px solid var(--border-color);border-radius:10px;
  padding:18px;cursor:pointer;transition:border-color 0.15s,transform 0.15s;
}
.project-card:hover{border-color:var(--accent-light);transform:translateY(-2px)}
.proj-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.proj-lang{background:#1b2a3e;color:var(--accent-light);padding:2px 8px;border-radius:4px;font-size:12px;font-weight:700}
.proj-name{font-size:15px;font-weight:600;margin-bottom:6px;color:var(--text-primary)}
.proj-desc{font-size:12px;color:var(--text-muted);margin-bottom:12px;line-height:1.5;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.proj-meta{display:flex;justify-content:space-between;font-size:11px;color:var(--text-muted)}
</style>

