<template>
  <div>
    <div class="page-header">
      <div class="page-title">生成审计报告</div>
    </div>
    <div class="card" style="max-width:600px">
      <div class="form-group">
        <label class="form-label">选择项目 *</label>
        <select v-model="form.pid" class="form-control" @change="loadTasks">
          <option value="">请选择项目</option>
          <option v-for="p in projects" :key="p.pid" :value="p.pid">{{ p.pname }}</option>
        </select>
      </div>
      <div class="form-group" v-if="form.pid">
        <label class="form-label">选择扫描任务（仅已完成任务可生成报告）*</label>
        <select v-model="form.tid" class="form-control">
          <option value="">请选择任务</option>
          <option v-for="t in tasks" :key="t.tid" :value="t.tid" :disabled="t.status!==2">
            任务{{ t.tid }} - {{ taskText(t.status) }} - {{ t.starttime?.slice(0,16)||'—' }}
          </option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">报告名称</label>
        <input v-model="form.repname" class="form-control" placeholder="留空自动生成" />
      </div>
      <div v-if="result" class="result-box">
        <div style="color:#3fb950;font-size:16px;margin-bottom:8px">✅ 报告生成成功</div>
        <p style="font-size:13px;color:var(--text-secondary)">{{ result.summary }}</p>
        <RouterLink :to="`/auditor/reports/${result.repid}`" class="btn btn-primary" style="margin-top:12px;display:inline-flex">
          查看报告
        </RouterLink>
      </div>
      <button v-else class="btn btn-primary" @click="generate" :disabled="generating||!form.pid||!form.tid">
        {{ generating?'生成中...':'生成报告' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { projectApi, scanApi, reportApi } from '@/api/index.js'
import { useUserStore } from '@/stores/user.js'
import { toast } from '@/utils/toast.js'

const store=useUserStore()
const projects=ref([]),tasks=ref([]),result=ref(null),generating=ref(false)
const form=ref({pid:'',tid:'',repname:''})
const taskText=s=>({0:'等待',1:'进行中',2:'已完成',3:'已暂停',4:'失败'}[s]??'未知')

async function loadProjects(){
  const res=await projectApi.list({size:100,uid:store.user?.uid})
  if(res.code===200)projects.value=res.data.list.filter(p=>p.status===2)
}
async function loadTasks(){
  form.value.tid=''
  if(!form.value.pid)return
  const res=await scanApi.list({pid:form.value.pid,size:50})
  if(res.code===200)tasks.value=res.data.list
}
async function generate(){
  if(!form.value.pid||!form.value.tid){toast.error('请选择项目和扫描任务');return}
  generating.value=true
  try{
    const res=await reportApi.generate({...form.value,operuid:store.user?.uid})
    if(res.code===200)result.value=res.data
    else toast.error(res.msg)
  }finally{generating.value=false}
}
onMounted(loadProjects)
</script>

<style scoped>
.result-box{background:#0f2d12;border:1px solid var(--success-light);border-radius:8px;padding:16px;margin-top:16px}
</style>

