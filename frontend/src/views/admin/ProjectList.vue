<template>
  <div>
    <div class="page-header">
      <div class="page-title">项目管理 <span>共 {{ total }} 个</span></div>
    </div>
    <div class="card">
      <div class="toolbar">
        <input v-model="keyword" class="form-control" style="width:220px" placeholder="搜索项目名称" @keyup.enter="loadList" />
        <button class="btn btn-ghost btn-sm" @click="loadList">搜索</button>
      </div>
      <table class="data-table">
        <thead>
          <tr><th>ID</th><th>项目名称</th><th>语言</th><th>负责人</th><th>状态</th><th>创建时间</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in list" :key="p.pid">
            <td>{{ p.pid }}</td>
            <td>{{ p.pname }}</td>
            <td><span class="badge badge-info">{{ p.language }}</span></td>
            <td>{{ p.ownername }}</td>
            <td><span :class="statusClass(p.status)">{{ statusText(p.status) }}</span></td>
            <td>{{ p.createtime?.slice(0,10) }}</td>
            <td>
              <RouterLink :to="`/admin/projects/${p.pid}/vulns`" class="btn btn-ghost btn-sm">查看漏洞</RouterLink>
              <button class="btn btn-ghost btn-sm" style="margin-left:4px" @click="openEdit(p)">编辑</button>
              <button class="btn btn-danger btn-sm" style="margin-left:4px" @click="delProj(p)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="empty-state" v-if="!list.length"><div class="icon">📁</div><p>暂无项目</p></div>
      <div class="pagination">
        <button class="page-btn" :disabled="page<=1" @click="page--;loadList()">上一页</button>
        <span class="page-btn active">{{ page }}</span>
        <button class="page-btn" :disabled="page*size>=total" @click="page++;loadList()">下一页</button>
      </div>
    </div>

    <div class="modal-mask" v-if="showModal" @click.self="showModal=false">
      <div class="modal-box">
        <div class="modal-title">编辑项目 <span style="cursor:pointer" @click="showModal=false">✕</span></div>
        <div class="form-group"><label class="form-label">项目名称 *</label>
          <input v-model="form.pname" class="form-control" /></div>
        <div class="form-group"><label class="form-label">项目描述</label>
          <textarea v-model="form.pdesc" class="form-control"></textarea></div>
        <div class="form-group"><label class="form-label">目标语言 *</label>
          <select v-model="form.language" class="form-control">
            <option value="python">Python</option>
            <option value="java">Java</option>
            <option value="php">PHP</option>
            <option value="js">JavaScript/TypeScript</option>
          </select></div>
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
import { RouterLink } from 'vue-router'
import { projectApi } from '@/api/index.js'
import { toast } from '@/utils/toast.js'

const list = ref([]), total = ref(0), page = ref(1), size = ref(10), keyword = ref('')
const showModal = ref(false), editMode = ref(false)
const form = ref({ pname:'', pdesc:'', language:'python' })

const statusText = s => ({ 0:'待扫描', 1:'扫描中', 2:'已完成', 3:'已暂停' }[s] ?? '未知')
const statusClass = s => ({ 0:'badge badge-default', 1:'badge badge-info', 2:'badge badge-success', 3:'badge badge-medium' }[s] ?? 'badge')

async function loadList() {
  const res = await projectApi.list({ page: page.value, size: size.value, keyword: keyword.value })
  if (res.code === 200) { list.value = res.data.list; total.value = res.data.total }
}

function openEdit(p) { editMode.value=true; form.value={...p}; showModal.value=true }

async function submit() {
  try {
    const res = await projectApi.update(form.value)
    if (res.code === 200) { toast.success(res.msg); showModal.value=false; loadList() }
    else toast.error(res.msg)
  } catch(e) { toast.error(e.message) }
}

async function delProj(p) {
  if (!confirm(`确认删除项目 "${p.pname}"？此操作将同时删除相关任务、漏洞和报告！`)) return
  const res = await projectApi.del(p.pid)
  if (res.code === 200) { toast.success('删除成功'); loadList() }
  else toast.error(res.msg)
}

onMounted(loadList)
</script>

