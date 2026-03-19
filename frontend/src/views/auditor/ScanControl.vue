<template>
  <div>
    <div class="page-header">
      <div class="page-title">
        <RouterLink to="/auditor/projects" style="color:var(--text-secondary);font-size:14px">← 项目列表</RouterLink>
        <span style="margin:0 8px;color:var(--text-muted)">/</span>
        扫描控制台
      </div>
    </div>

    <div class="card" v-if="proj">
      <div class="proj-info">
        <div><span class="label">项目名称</span>{{ proj.pname }}</div>
        <div><span class="label">目标语言</span>{{ proj.language }}</div>
        <div><span class="label">源码路径</span><code>{{ proj.sourcepath }}</code></div>
        <div><span class="label">当前状态</span><span :class="statusClass(proj.status)">{{ statusText(proj.status) }}</span></div>
      </div>
    </div>

    <!-- 上传源码 -->
    <div class="card" style="margin-top:16px">
      <div class="section-title">📦 上传源码</div>
      <div style="font-size:12px;color:var(--text-muted);margin-bottom:10px">
        支持 ZIP、TAR.GZ、RAR 压缩包，或直接上传单个源码文件（.py .java .php .js .ts 等）
      </div>
      <div class="upload-area" @dragover.prevent @drop.prevent="onDrop">
        <input ref="fileInput" type="file"
          accept=".zip,.tar,.gz,.tgz,.tar.gz,.rar,.py,.java,.php,.js,.ts,.jsx,.tsx"
          style="display:none" @change="onFileChange" />
        <button class="btn btn-ghost" @click="fileInput.click()">选择文件</button>
        <span style="margin-left:10px;color:var(--text-secondary);font-size:13px">{{ uploadFile?.name || '或拖拽文件到此处' }}</span>
        <button v-if="uploadFile" class="btn btn-success" style="margin-left:10px" @click="doUpload" :disabled="uploading">
          {{ uploading?'上传中...':'上传' }}
        </button>
      </div>
    </div>

    <!-- 扫描控制 -->
    <div class="card" style="margin-top:16px">
      <div class="section-title">🚀 扫描控制</div>
      <div class="scan-controls">
        <button class="btn btn-primary" @click="startScan" :disabled="scanning||proj?.status===1">
          ▶ 开始扫描
        </button>
        <button class="btn btn-warning" @click="pauseScan" :disabled="!scanning&&proj?.status!==1" style="margin-left:10px">
          ⏸ 暂停扫描
        </button>
        <button class="btn btn-success" @click="resumeScan" :disabled="proj?.status!==3" style="margin-left:10px">
          ▶▶ 继续扫描
        </button>
        <RouterLink v-if="proj?.status===2" :to="`/auditor/projects/${pid}/vulns`" class="btn btn-ghost" style="margin-left:10px">
          🐛 查看漏洞
        </RouterLink>
      </div>

      <!-- 当前任务进度 -->
      <div v-if="curTask" style="margin-top:20px">
        <div style="display:flex;justify-content:space-between;margin-bottom:6px;font-size:13px">
          <span>扫描进度</span>
          <span>{{ curTask.scannedfiles }}/{{ curTask.totalfiles }} 文件 · {{ curTask.progress }}%</span>
        </div>
        <div class="progress-bar-wrap">
          <div class="progress-bar-fill" :style="{width:curTask.progress+'%'}"></div>
        </div>
        <div style="margin-top:10px;font-size:12px;color:var(--text-muted)">
          任务ID: {{ curTask.tid }} · 开始: {{ curTask.starttime || '—' }} · 结束: {{ curTask.endtime || '进行中' }}
        </div>
      </div>
    </div>

    <!-- 历史任务 -->
    <div class="card" style="margin-top:16px">
      <div class="section-title">📜 历史任务</div>
      <table class="data-table">
        <thead><tr><th>任务ID</th><th>状态</th><th>进度</th><th>文件数</th><th>开始时间</th><th>结束时间</th></tr></thead>
        <tbody>
          <tr v-for="t in tasks" :key="t.tid">
            <td>{{ t.tid }}</td>
            <td><span :class="taskClass(t.status)">{{ taskText(t.status) }}</span></td>
            <td>
              <div class="progress-bar-wrap" style="width:80px;display:inline-block">
                <div class="progress-bar-fill" :style="{width:t.progress+'%'}"></div>
              </div> {{ t.progress }}%
            </td>
            <td>{{ t.scannedfiles }}/{{ t.totalfiles }}</td>
            <td>{{ t.starttime?.slice(0,16)||'—' }}</td>
            <td>{{ t.endtime?.slice(0,16)||'—' }}</td>
          </tr>
        </tbody>
      </table>
      <div class="empty-state" v-if="!tasks.length"><div class="icon">🔍</div><p>暂无扫描记录</p></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { projectApi, scanApi } from '@/api/index.js'
import { useUserStore } from '@/stores/user.js'
import { toast } from '@/utils/toast.js'

const route=useRoute(),store=useUserStore()
const pid=route.params.pid
const proj=ref(null),tasks=ref([]),curTask=ref(null)
const scanning=ref(false),uploading=ref(false)
const fileInput=ref(null),uploadFile=ref(null)
let pollTimer=null

const statusText=s=>({0:'待扫描',1:'扫描中',2:'已完成',3:'已暂停'}[s]??'未知')
const statusClass=s=>({0:'badge badge-default',1:'badge badge-info',2:'badge badge-success',3:'badge badge-medium'}[s]??'badge')
const taskText=s=>({0:'等待',1:'进行中',2:'已完成',3:'已暂停',4:'失败'}[s]??'未知')
const taskClass=s=>({0:'badge badge-default',1:'badge badge-info',2:'badge badge-success',3:'badge badge-medium',4:'badge badge-high'}[s]??'badge')

async function loadData(){
  const r=await projectApi.detail(pid)
  if(r.code===200)proj.value=r.data
  const t=await scanApi.list({pid,size:10})
  if(t.code===200)tasks.value=t.data.list
  if(tasks.value.length){
    const latest=tasks.value[0]
    if(latest.status===1){scanning.value=true;curTask.value=latest;startPoll(latest.tid)}
    else curTask.value=latest
  }
}

async function startScan(){
  const res=await scanApi.start({pid,operuid:store.user.uid})
  if(res.code===200){toast.success('扫描已启动');scanning.value=true;loadData();startPoll(res.data.tid)}
  else toast.error(res.msg)
}
async function pauseScan(){
  if(!curTask.value)return
  const res=await scanApi.pause({tid:curTask.value.tid,pid})
  if(res.code===200){toast.success('已暂停');scanning.value=false;stopPoll();loadData()}
  else toast.error(res.msg)
}
async function resumeScan(){
  const res=await scanApi.resume({pid,operuid:store.user.uid})
  if(res.code===200){toast.success('继续扫描');scanning.value=true;loadData();startPoll(res.data.tid)}
  else toast.error(res.msg)
}

function startPoll(tid){
  stopPoll()
  pollTimer=setInterval(async()=>{
    const r=await scanApi.progress(tid)
    if(r.code===200){
      curTask.value=r.data
      if(r.data.status===2||r.data.status===4){stopPoll();scanning.value=false;loadData();toast.success('扫描完成！')}
    }
  },2000)
}
function stopPoll(){ if(pollTimer){clearInterval(pollTimer);pollTimer=null} }

function onFileChange(e){ uploadFile.value=e.target.files[0] }
function onDrop(e){ uploadFile.value=e.dataTransfer.files[0] }
async function doUpload(){
  if(!uploadFile.value)return
  uploading.value=true
  try{
    const res=await scanApi.upload(pid,uploadFile.value)
    if(res.code===200){toast.success('上传成功');uploadFile.value=null;loadData()}
    else toast.error(res.msg)
  }finally{uploading.value=false}
}

onMounted(loadData)
onUnmounted(stopPoll)
</script>

<style scoped>
.proj-info{display:grid;grid-template-columns:1fr 1fr;gap:10px;font-size:13px}
.proj-info .label{color:var(--text-muted);margin-right:8px;font-size:12px}
.section-title{font-size:14px;font-weight:600;margin-bottom:14px}
.scan-controls{display:flex;align-items:center;flex-wrap:wrap;gap:4px}
.upload-area{display:flex;align-items:center;padding:12px;border:1px dashed var(--border-color);border-radius:8px;flex-wrap:wrap;gap:8px}
</style>

