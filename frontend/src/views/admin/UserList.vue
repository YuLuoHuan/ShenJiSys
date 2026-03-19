<template>
  <div>
    <div class="page-header">
      <div class="page-title">用户管理 <span>共 {{ total }} 人</span></div>
      <button class="btn btn-primary btn-sm" @click="openAdd">+ 新增用户</button>
    </div>
    <div class="card">
      <div class="toolbar">
        <input v-model="keyword" class="form-control" style="width:220px" placeholder="搜索用户名/姓名" @keyup.enter="loadList" />
        <button class="btn btn-ghost btn-sm" @click="loadList">搜索</button>
      </div>
      <table class="data-table">
        <thead>
          <tr><th>ID</th><th>用户名</th><th>姓名</th><th>邮箱</th><th>角色</th><th>状态</th><th>创建时间</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="u in list" :key="u.uid">
            <td>{{ u.uid }}</td>
            <td><code>{{ u.uname }}</code></td>
            <td>{{ u.realname }}</td>
            <td>{{ u.email }}</td>
            <td><span :class="u.rolecode===1?'badge badge-info':'badge badge-default'">{{ u.rolecode===1?'管理员':'审计员' }}</span></td>
            <td><span :class="u.status===1?'badge badge-success':'badge badge-high'">{{ u.status===1?'启用':'禁用' }}</span></td>
            <td>{{ u.createtime }}</td>
            <td>
              <button class="btn btn-ghost btn-sm" @click="openEdit(u)">编辑</button>
              <button class="btn btn-danger btn-sm" style="margin-left:4px" @click="delUser(u)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="empty-state" v-if="!list.length"><div class="icon">👥</div><p>暂无用户数据</p></div>
      <div class="pagination">
        <button class="page-btn" :disabled="page<=1" @click="page--;loadList()">上一页</button>
        <span class="page-btn active">{{ page }}</span>
        <button class="page-btn" :disabled="page*size>=total" @click="page++;loadList()">下一页</button>
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <div class="modal-mask" v-if="showModal" @click.self="showModal=false">
      <div class="modal-box">
        <div class="modal-title">{{ editMode?'编辑用户':'新增用户' }} <span style="cursor:pointer" @click="showModal=false">✕</span></div>
        <div class="form-group"><label class="form-label">用户名</label>
          <input v-model="form.uname" class="form-control" :disabled="editMode" placeholder="登录用户名" /></div>
        <div class="form-group" v-if="!editMode"><label class="form-label">初始密码</label>
          <input v-model="form.passwd" class="form-control" placeholder="默认123456" /></div>
        <div class="form-group"><label class="form-label">真实姓名</label>
          <input v-model="form.realname" class="form-control" /></div>
        <div class="form-group"><label class="form-label">邮箱</label>
          <input v-model="form.email" class="form-control" /></div>
        <div class="form-group"><label class="form-label">角色</label>
          <select v-model="form.rolecode" class="form-control">
            <option :value="1">管理员</option><option :value="2">审计员</option>
          </select></div>
        <div class="form-group" v-if="editMode"><label class="form-label">状态</label>
          <select v-model="form.status" class="form-control">
            <option :value="1">启用</option><option :value="0">禁用</option>
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
import { userApi } from '@/api/index.js'
import { toast } from '@/utils/toast.js'

const list = ref([]), total = ref(0), page = ref(1), size = ref(10), keyword = ref('')
const showModal = ref(false), editMode = ref(false)
const form = ref({ uname:'', passwd:'123456', realname:'', email:'', rolecode:2, status:1 })

async function loadList() {
  const res = await userApi.list({ page: page.value, size: size.value, keyword: keyword.value })
  if (res.code === 200) { list.value = res.data.list; total.value = res.data.total }
}

function openAdd() { editMode.value=false; form.value={uname:'',passwd:'123456',realname:'',email:'',rolecode:2,status:1}; showModal.value=true }
function openEdit(u) { editMode.value=true; form.value={...u}; showModal.value=true }

async function submit() {
  try {
    let res
    if (editMode.value) res = await userApi.update(form.value)
    else res = await userApi.add(form.value)
    if (res.code === 200) { toast.success(res.msg); showModal.value=false; loadList() }
    else toast.error(res.msg)
  } catch(e) { toast.error(e.message) }
}

async function delUser(u) {
  if (!confirm(`确认删除用户 "${u.uname}" ？`)) return
  const res = await userApi.del(u.uid)
  if (res.code === 200) { toast.success('删除成功'); loadList() }
  else toast.error(res.msg)
}

onMounted(loadList)
</script>

