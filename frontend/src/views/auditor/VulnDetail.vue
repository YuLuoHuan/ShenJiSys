<template>
  <div>
    <div class="page-header">
      <div class="page-title">
        <button class="btn btn-ghost btn-sm" @click="$router.back()">← 返回</button>
        <span style="margin-left:8px">漏洞详情</span>
      </div>
      <button class="btn btn-primary btn-sm" @click="showMark=true">标记状态</button>
    </div>

    <div v-if="vuln">
      <!-- 漏洞头信息 -->
      <div class="card vuln-header-card">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
          <span :class="sevClass(vuln.severity)" style="font-size:14px;padding:4px 12px">{{ sevText(vuln.severity) }}</span>
          <span :class="stateClass(vuln.vulnstate)">{{ stateText(vuln.vulnstate) }}</span>
          <span class="badge badge-info">{{ vuln.category }}</span>
        </div>
        <h2 style="font-size:16px;margin-bottom:4px">{{ vuln.rname }}</h2>
        <p style="font-size:13px;color:var(--text-muted)">{{ vuln.pname }}</p>
      </div>

      <!-- 漏洞位置 -->
      <div class="card" style="margin-top:14px">
        <div class="section-title">📍 漏洞位置</div>
        <div class="info-row"><span class="info-label">文件路径</span><code>{{ vuln.filepath }}</code></div>
        <div class="info-row"><span class="info-label">行号</span>{{ vuln.lineno }}</div>
      </div>

      <!-- 漏洞代码 -->
      <div class="card" style="margin-top:14px">
        <div class="section-title">💻 漏洞代码片段</div>
        <div class="code-block">{{ vuln.codesnip }}</div>
      </div>

      <!-- 修复建议 -->
      <div class="card" style="margin-top:14px">
        <div class="section-title">🔧 修复建议</div>
        <p style="font-size:13px;color:var(--text-secondary);line-height:1.8">{{ vuln.suggestion || '暂无修复建议' }}</p>
      </div>

      <!-- 备注 -->
      <div class="card" style="margin-top:14px" v-if="vuln.remark">
        <div class="section-title">📝 备注</div>
        <p style="font-size:13px;color:var(--text-secondary)">{{ vuln.remark }}</p>
      </div>
    </div>

    <div class="empty-state" v-else><div class="icon">⏳</div><p>加载中...</p></div>

    <!-- 标记弹窗 -->
    <div class="modal-mask" v-if="showMark" @click.self="showMark=false">
      <div class="modal-box">
        <div class="modal-title">标记漏洞状态 <span style="cursor:pointer" @click="showMark=false">✕</span></div>
        <div class="form-group"><label class="form-label">处理状态</label>
          <select v-model="markForm.vulnstate" class="form-control">
            <option :value="0">未处理</option><option :value="1">已确认</option>
            <option :value="2">误报</option><option :value="3">已修复</option>
          </select></div>
        <div class="form-group"><label class="form-label">备注说明</label>
          <textarea v-model="markForm.remark" class="form-control" rows="3"></textarea></div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showMark=false">取消</button>
          <button class="btn btn-primary" @click="submitMark">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { vulnApi } from '@/api/index.js'
import { toast } from '@/utils/toast.js'

const route=useRoute()
const vid=route.params.vid
const vuln=ref(null),showMark=ref(false)
const markForm=ref({vid:null,vulnstate:0,remark:''})

const sevText=s=>({1:'低危',2:'中危',3:'高危',4:'危急'}[s]??'未知')
const sevClass=s=>({1:'badge badge-low',2:'badge badge-medium',3:'badge badge-high',4:'badge badge-critical'}[s]??'badge')
const stateText=s=>({0:'未处理',1:'已确认',2:'误报',3:'已修复'}[s]??'未知')
const stateClass=s=>({0:'badge badge-default',1:'badge badge-info',2:'badge badge-medium',3:'badge badge-success'}[s]??'badge')

async function load(){
  const res=await vulnApi.detail(vid)
  if(res.code===200){
    vuln.value=res.data
    markForm.value={vid:res.data.vid,vulnstate:res.data.vulnstate,remark:res.data.remark||''}
  }
}
async function submitMark(){
  const res=await vulnApi.updateState(markForm.value)
  if(res.code===200){toast.success(res.msg);showMark.value=false;load()}
  else toast.error(res.msg)
}
onMounted(load)
</script>

<style scoped>
.vuln-header-card{border-left:3px solid var(--accent)}
.section-title{font-size:13px;font-weight:600;margin-bottom:10px;color:var(--text-secondary);text-transform:uppercase;letter-spacing:0.5px}
.info-row{display:flex;gap:12px;padding:6px 0;border-bottom:1px solid var(--border-color);font-size:13px}
.info-label{width:80px;color:var(--text-muted);font-size:12px;flex-shrink:0}
</style>

