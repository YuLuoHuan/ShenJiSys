<template>
  <div>
    <div class="page-header">
      <div class="page-title">个人中心</div>
    </div>
    <div class="profile-grid">
      <!-- 基本信息 -->
      <div class="card">
        <div class="section-title">👤 基本信息</div>
        <div class="form-group"><label class="form-label">用户名（不可修改）</label>
          <input class="form-control" :value="store.user?.uname" disabled /></div>
        <div class="form-group"><label class="form-label">真实姓名</label>
          <input v-model="profileForm.realname" class="form-control" /></div>
        <div class="form-group"><label class="form-label">邮箱</label>
          <input v-model="profileForm.email" class="form-control" /></div>
        <div class="form-group"><label class="form-label">角色</label>
          <input class="form-control" :value="store.user?.rolecode===1?'管理员':'审计员'" disabled /></div>
        <button class="btn btn-primary" @click="saveProfile">保存基本信息</button>
      </div>

      <!-- 修改密码 -->
      <div class="card">
        <div class="section-title">🔑 修改密码</div>
        <div class="form-group"><label class="form-label">原密码</label>
          <input v-model="pwdForm.oldpasswd" type="password" class="form-control" /></div>
        <div class="form-group"><label class="form-label">新密码</label>
          <input v-model="pwdForm.newpasswd" type="password" class="form-control" /></div>
        <div class="form-group"><label class="form-label">确认新密码</label>
          <input v-model="pwdForm.confirm" type="password" class="form-control" /></div>
        <button class="btn btn-primary" @click="changePasswd">修改密码</button>
      </div>

      <!-- 安全问题 -->
      <div class="card">
        <div class="section-title">🛡 安全问题（用于找回密码）</div>
        <div class="form-group"><label class="form-label">安全问题</label>
          <input v-model="sqForm.question" class="form-control" placeholder="输入您的安全问题" /></div>
        <div class="form-group"><label class="form-label">答案</label>
          <input v-model="sqForm.answer" class="form-control" placeholder="输入安全问题答案" /></div>
        <button class="btn btn-primary" @click="saveSecQuestion">保存安全问题</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authApi, userApi } from '@/api/index.js'
import { useUserStore } from '@/stores/user.js'
import { toast } from '@/utils/toast.js'

const store=useUserStore()
const profileForm=ref({realname:store.user?.realname||'',email:store.user?.email||''})
const pwdForm=ref({oldpasswd:'',newpasswd:'',confirm:''})
const sqForm=ref({question:'',answer:''})

async function loadSecQuestion(){
  const res=await userApi.detail(store.user?.uid)
  if(res.code===200&&res.data.secquestion) sqForm.value.question=res.data.secquestion
}

async function saveProfile(){
  const res=await userApi.updateProfile({uid:store.user?.uid,...profileForm.value})
  if(res.code===200){
    store.setUser({...store.user,...profileForm.value})
    toast.success('个人信息更新成功')
  }else toast.error(res.msg)
}

async function changePasswd(){
  if(!pwdForm.value.oldpasswd||!pwdForm.value.newpasswd){toast.error('请填写完整');return}
  if(pwdForm.value.newpasswd!==pwdForm.value.confirm){toast.error('两次密码不一致');return}
  const res=await authApi.changePasswd({uid:store.user?.uid,oldpasswd:pwdForm.value.oldpasswd,newpasswd:pwdForm.value.newpasswd})
  if(res.code===200){toast.success('密码修改成功');pwdForm.value={oldpasswd:'',newpasswd:'',confirm:''}}
  else toast.error(res.msg)
}

async function saveSecQuestion(){
  if(!sqForm.value.question||!sqForm.value.answer){toast.error('请填写安全问题和答案');return}
  const res=await authApi.setSecQuestion({uid:store.user?.uid,...sqForm.value})
  if(res.code===200)toast.success('安全问题保存成功')
  else toast.error(res.msg)
}

onMounted(loadSecQuestion)
</script>

<style scoped>
.profile-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.profile-grid .card:last-child{grid-column:1/-1}
.section-title{font-size:14px;font-weight:600;margin-bottom:16px;color:var(--text-primary)}
@media(max-width:700px){.profile-grid{grid-template-columns:1fr}}
</style>

