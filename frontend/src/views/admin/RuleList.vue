<template>
  <div>
    <div class="page-header">
      <div class="page-title">规则管理 <span>共 {{ total }} 条</span></div>
      <button class="btn btn-primary btn-sm" @click="openAdd">+ 新增规则</button>
    </div>
    <div class="card">
      <div class="toolbar">
        <select v-model="filterLang" class="form-control" style="width:140px" @change="loadList">
          <option value="">全部语言</option>
          <option value="python">Python</option><option value="java">Java</option>
          <option value="php">PHP</option><option value="js">JavaScript</option><option value="all">通用</option>
        </select>
        <select v-model="filterCat" class="form-control" style="width:140px" @change="loadList">
          <option value="">全部类别</option>
          <option value="sqli">SQL注入</option><option value="xss">XSS</option>
          <option value="rce">命令执行</option><option value="path">路径穿越</option>
          <option value="sensitive">敏感信息</option><option value="other">其他</option>
        </select>
        <select v-model="filterEnabled" class="form-control" style="width:120px" @change="loadList">
          <option value="">全部状态</option><option value="1">已启用</option><option value="0">已禁用</option>
        </select>
        <input v-model="keyword" class="form-control" style="width:180px" placeholder="搜索规则名" @keyup.enter="loadList" />
        <button class="btn btn-ghost btn-sm" @click="loadList">搜索</button>
      </div>
      <table class="data-table">
        <thead><tr><th>ID</th><th>规则名称</th><th>漏洞类别</th><th>语言</th><th>等级</th><th>状态</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="r in list" :key="r.rid">
            <td>{{ r.rid }}</td>
            <td>{{ r.rname }}</td>
            <td><span class="badge badge-info">{{ r.category }}</span></td>
            <td><span class="badge badge-default">{{ r.language }}</span></td>
            <td><span :class="sevClass(r.severity)">{{ sevText(r.severity) }}</span></td>
            <td><span :class="r.enabled?'badge badge-success':'badge badge-high'">{{ r.enabled?'启用':'禁用' }}</span></td>
            <td>
              <button class="btn btn-ghost btn-sm" @click="openEdit(r)">编辑</button>
              <button class="btn btn-sm" :class="r.enabled?'btn-warning':'btn-success'" style="margin-left:4px" @click="toggle(r)">
                {{ r.enabled?'禁用':'启用' }}
              </button>
              <button class="btn btn-danger btn-sm" style="margin-left:4px" @click="delRule(r)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="empty-state" v-if="!list.length"><div class="icon">📋</div><p>暂无规则</p></div>
      <div class="pagination">
        <button class="page-btn" :disabled="page<=1" @click="page--;loadList()">上一页</button>
        <span class="page-btn active">{{ page }}</span>
        <button class="page-btn" :disabled="page*size>=total" @click="page++;loadList()">下一页</button>
      </div>
    </div>

    <div class="modal-mask" v-if="showModal" @click.self="showModal=false">
      <div class="modal-box" style="width:600px">
        <div class="modal-title">{{ editMode?'编辑规则':'新增规则' }} <span style="cursor:pointer" @click="showModal=false">✕</span></div>
        <div class="form-group"><label class="form-label">规则名称 *</label><input v-model="form.rname" class="form-control" /></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
          <div class="form-group"><label class="form-label">漏洞类别 *</label>
            <select v-model="form.category" class="form-control">
              <option value="sqli">SQL注入</option><option value="xss">XSS</option><option value="rce">命令执行</option>
              <option value="path">路径穿越</option><option value="sensitive">敏感信息</option><option value="other">其他</option>
            </select></div>
          <div class="form-group"><label class="form-label">适用语言 *</label>
            <select v-model="form.language" class="form-control">
              <option value="python">Python</option><option value="java">Java</option>
              <option value="php">PHP</option><option value="js">JavaScript</option><option value="all">通用</option>
            </select></div>
        </div>
        <div class="form-group"><label class="form-label">匹配正则 *</label>
          <input v-model="form.pattern" class="form-control" style="font-family:var(--font-mono);font-size:12px" placeholder="正则表达式" /></div>
        <div class="form-group"><label class="form-label">严重等级</label>
          <select v-model="form.severity" class="form-control">
            <option :value="1">1 - 低危</option><option :value="2">2 - 中危</option>
            <option :value="3">3 - 高危</option><option :value="4">4 - 危急</option>
          </select></div>
        <div class="form-group"><label class="form-label">修复建议</label>
          <textarea v-model="form.suggestion" class="form-control"></textarea></div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showModal=false">取消</button>
          <button class="btn btn-primary" @click="submit">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ruleApi } from '@/api/index.js'
import { toast } from '@/utils/toast.js'

const list=ref([]),total=ref(0),page=ref(1),size=ref(20)
const keyword=ref(''),filterLang=ref(''),filterCat=ref(''),filterEnabled=ref('')
const showModal=ref(false),editMode=ref(false)
const form=ref({rname:'',category:'sqli',language:'python',pattern:'',severity:2,suggestion:''})

const sevText = s=>({1:'低危',2:'中危',3:'高危',4:'危急'}[s]??'未知')
const sevClass = s=>({1:'badge badge-low',2:'badge badge-medium',3:'badge badge-high',4:'badge badge-critical'}[s]??'badge')

async function loadList(){
  const res=await ruleApi.list({page:page.value,size:size.value,language:filterLang.value,category:filterCat.value,enabled:filterEnabled.value,keyword:keyword.value})
  if(res.code===200){list.value=res.data.list;total.value=res.data.total}
}
function openAdd(){editMode.value=false;form.value={rname:'',category:'sqli',language:'python',pattern:'',severity:2,suggestion:''};showModal.value=true}
function openEdit(r){editMode.value=true;form.value={...r};showModal.value=true}
async function submit(){
  try{
    const res=editMode.value?await ruleApi.update(form.value):await ruleApi.add(form.value)
    if(res.code===200){toast.success(res.msg);showModal.value=false;loadList()}else toast.error(res.msg)
  }catch(e){toast.error(e.message)}
}
async function toggle(r){
  const res=await ruleApi.toggle({rid:r.rid,enabled:r.enabled?0:1})
  if(res.code===200){toast.success(res.msg);loadList()}else toast.error(res.msg)
}
async function delRule(r){
  if(!confirm(`确认删除规则 "${r.rname}"？`))return
  const res=await ruleApi.del(r.rid)
  if(res.code===200){toast.success('删除成功');loadList()}else toast.error(res.msg)
}
onMounted(loadList)
</script>

