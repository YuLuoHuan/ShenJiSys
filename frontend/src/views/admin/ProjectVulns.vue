<template>
  <div>
    <div class="page-header">
      <div class="page-title">
        <RouterLink to="/admin/projects" style="color:var(--text-secondary);font-size:14px">← 项目列表</RouterLink>
        <span style="margin:0 8px;color:var(--text-muted)">/</span>
        漏洞列表 <span>项目ID: {{ pid }}</span>
      </div>
      <a :href="exportUrl" class="btn btn-ghost btn-sm">⬇ 导出</a>
    </div>

    <!-- 统计 -->
    <div class="stat-grid" style="margin-bottom:20px">
      <div class="stat-card"><div class="stat-num" style="color:#f85149">{{ stats.critical }}</div><div class="stat-label">危急</div></div>
      <div class="stat-card"><div class="stat-num" style="color:#e3b341">{{ stats.high }}</div><div class="stat-label">高危</div></div>
      <div class="stat-card"><div class="stat-num" style="color:#58a6ff">{{ stats.medium }}</div><div class="stat-label">中危</div></div>
      <div class="stat-card"><div class="stat-num">{{ stats.low }}</div><div class="stat-label">低危</div></div>
    </div>

    <div class="card">
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
      </div>
      <table class="data-table">
        <thead><tr><th>ID</th><th>规则</th><th>文件路径</th><th>行号</th><th>等级</th><th>状态</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="v in list" :key="v.vid">
            <td>{{ v.vid }}</td>
            <td>{{ v.rname }}</td>
            <td><span class="file-path">{{ v.filepath }}</span></td>
            <td>{{ v.lineno }}</td>
            <td><span :class="sevClass(v.severity)">{{ sevText(v.severity) }}</span></td>
            <td><span :class="stateClass(v.vulnstate)">{{ stateText(v.vulnstate) }}</span></td>
            <td>
              <button class="btn btn-ghost btn-sm" @click="openDetail(v)">详情</button>
              <button class="btn btn-ghost btn-sm" style="margin-left:4px" @click="openMark(v)">标记</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="empty-state" v-if="!list.length"><div class="icon">✅</div><p>该项目暂无漏洞</p></div>
    </div>

    <!-- 详情弹窗 -->
    <div class="modal-mask" v-if="showDetail" @click.self="showDetail=false">
      <div class="modal-box" style="width:680px">
        <div class="modal-title">漏洞详情 <span style="cursor:pointer" @click="showDetail=false">✕</span></div>
        <div v-if="curVuln">
          <div style="margin-bottom:8px"><span :class="sevClass(curVuln.severity)">{{ sevText(curVuln.severity) }}</span></div>
          <p style="font-size:13px;color:var(--text-secondary);margin-bottom:8px">{{ curVuln.filepath }}:{{ curVuln.lineno }}</p>
          <div class="code-block">{{ curVuln.codesnip }}</div>
          <p style="margin-top:12px;font-size:13px"><strong>修复建议：</strong>{{ curVuln.suggestion }}</p>
        </div>
      </div>
    </div>

    <!-- 标记弹窗 -->
    <div class="modal-mask" v-if="showMark" @click.self="showMark=false">
      <div class="modal-box">
        <div class="modal-title">标记状态 <span style="cursor:pointer" @click="showMark=false">✕</span></div>
        <div class="form-group"><label class="form-label">状态</label>
          <select v-model="markForm.vulnstate" class="form-control">
            <option :value="0">未处理</option><option :value="1">已确认</option>
            <option :value="2">误报</option><option :value="3">已修复</option>
          </select></div>
        <div class="form-group"><label class="form-label">备注</label>
          <textarea v-model="markForm.remark" class="form-control"></textarea></div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showMark=false">取消</button>
          <button class="btn btn-primary" @click="submitMark">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { vulnApi } from '@/api/index.js'
import { toast } from '@/utils/toast.js'

const route=useRoute()
const pid=route.params.pid
const list=ref([]),filterSev=ref(''),filterState=ref('')
const showDetail=ref(false),curVuln=ref(null)
const showMark=ref(false),markForm=ref({vid:null,vulnstate:0,remark:''})
const stats=ref({critical:0,high:0,medium:0,low:0})

const exportUrl=computed(()=>vulnApi.exportUrl({pid}))
const sevText=s=>({1:'低危',2:'中危',3:'高危',4:'危急'}[s]??'未知')
const sevClass=s=>({1:'badge badge-low',2:'badge badge-medium',3:'badge badge-high',4:'badge badge-critical'}[s]??'badge')
const stateText=s=>({0:'未处理',1:'已确认',2:'误报',3:'已修复'}[s]??'未知')
const stateClass=s=>({0:'badge badge-default',1:'badge badge-info',2:'badge badge-medium',3:'badge badge-success'}[s]??'badge')

async function loadList(){
  const res=await vulnApi.list({pid,severity:filterSev.value,vulnstate:filterState.value,size:200})
  if(res.code===200){
    list.value=res.data.list
    const sres=await vulnApi.stats({pid})
    if(sres.code===200){
      const m={critical:0,high:0,medium:0,low:0}
      sres.data.byseverity.forEach(s=>{if(s.severity===4)m.critical=s.cnt;else if(s.severity===3)m.high=s.cnt;else if(s.severity===2)m.medium=s.cnt;else m.low=s.cnt})
      stats.value=m
    }
  }
}
function openDetail(v){curVuln.value=v;showDetail.value=true}
function openMark(v){markForm.value={vid:v.vid,vulnstate:v.vulnstate,remark:v.remark||''};showMark.value=true}
async function submitMark(){
  const res=await vulnApi.updateState(markForm.value)
  if(res.code===200){toast.success(res.msg);showMark.value=false;loadList()}else toast.error(res.msg)
}
onMounted(loadList)
</script>

<style scoped>
.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.file-path{font-family:var(--font-mono);font-size:11px;color:var(--text-secondary)}
</style>

