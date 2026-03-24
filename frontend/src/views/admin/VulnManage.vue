<template>
  <div>
    <div class="page-header">
      <div class="page-title">漏洞管理 <span>共 {{ total }} 条</span></div>
      <a :href="exportUrl" class="btn btn-ghost btn-sm">⬇ 导出CSV</a>
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
        <input v-model="keyword" class="form-control" style="width:200px" placeholder="文件路径/代码片段" @keyup.enter="loadList" />
        <button class="btn btn-ghost btn-sm" @click="loadList">搜索</button>
      </div>
      <table class="data-table">
        <thead><tr><th>ID</th><th>项目</th><th>规则</th><th>文件路径</th><th>行号</th><th>等级</th><th>状态</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="v in list" :key="v.vid">
            <td>{{ v.vid }}</td>
            <td>{{ v.pname }}</td>
            <td>{{ v.rname }}</td>
            <td><span class="file-path" :title="v.filepath">{{ shortPath(v.filepath) }}</span></td>
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
      <div class="empty-state" v-if="!list.length"><div class="icon">🐛</div><p>暂无漏洞数据</p></div>
      <div class="pagination">
        <button class="page-btn" :disabled="page<=1" @click="page--;loadList()">上一页</button>
        <span class="page-btn active">{{ page }}</span>
        <button class="page-btn" :disabled="page*size>=total" @click="page++;loadList()">下一页</button>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <div class="modal-mask" v-if="showDetail" @click.self="showDetail=false">
      <div class="modal-box" style="width:700px">
        <div class="modal-title">漏洞详情 <span style="cursor:pointer" @click="showDetail=false">✕</span></div>
        <table class="detail-table" v-if="curVuln">
          <tbody>
            <tr><td class="dl">文件路径</td><td>{{ curVuln.filepath }}</td></tr>
            <tr><td class="dl">行号</td><td>{{ curVuln.lineno }}</td></tr>
            <tr><td class="dl">规则名称</td><td>{{ curVuln.rname }}</td></tr>
            <tr><td class="dl">漏洞类别</td><td>{{ curVuln.category }}</td></tr>
            <tr><td class="dl">严重等级</td><td><span :class="sevClass(curVuln.severity)">{{ sevText(curVuln.severity) }}</span></td></tr>
            <tr><td class="dl">漏洞代码</td><td><div class="code-block">{{ curVuln.codesnip }}</div></td></tr>
            <tr><td class="dl">修复建议</td><td>{{ curVuln.suggestion }}</td></tr>
            <tr><td class="dl">备注</td><td>{{ curVuln.remark || '—' }}</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 标记弹窗 -->
    <div class="modal-mask" v-if="showMark" @click.self="showMark=false">
      <div class="modal-box">
        <div class="modal-title">标记漏洞状态 <span style="cursor:pointer" @click="showMark=false">✕</span></div>
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
import { vulnApi } from '@/api/index.js'
import { toast } from '@/utils/toast.js'

const list=ref([]),total=ref(0),page=ref(1),size=ref(20)
const filterSev=ref(''),filterState=ref(''),keyword=ref('')
const showDetail=ref(false),curVuln=ref(null)
const showMark=ref(false),markForm=ref({vid:null,vulnstate:0,remark:''})

const exportUrl=computed(()=>vulnApi.exportUrl({severity:filterSev.value,vulnstate:filterState.value}))
const sevText=s=>({1:'低危',2:'中危',3:'高危',4:'危急'}[s]??'未知')
const sevClass=s=>({1:'badge badge-low',2:'badge badge-medium',3:'badge badge-high',4:'badge badge-critical'}[s]??'badge')
const stateText=s=>({0:'未处理',1:'已确认',2:'误报',3:'已修复'}[s]??'未知')
const stateClass=s=>({0:'badge badge-default',1:'badge badge-info',2:'badge badge-medium',3:'badge badge-success'}[s]??'badge')
const shortPath=p=>p&&p.length>40?'...'+p.slice(-40):p

async function loadList(){
  const res=await vulnApi.list({page:page.value,size:size.value,severity:filterSev.value,vulnstate:filterState.value,keyword:keyword.value})
  if(res.code===200){list.value=res.data.list;total.value=res.data.total}
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
.file-path{font-family:var(--font-mono);font-size:11px;color:var(--text-secondary)}
.detail-table{width:100%;border-collapse:collapse}
.detail-table tr td{padding:8px 12px;border-bottom:1px solid var(--border-color);font-size:13px}
.detail-table td.dl{width:100px;color:var(--text-muted);font-size:12px;white-space:nowrap}
</style>

