<template>
  <div class="login-page">
    <div class="login-box">
      <div class="login-header">
        <div class="login-icon">🔑</div>
        <h1 class="login-title">找回密码</h1>
        <p class="login-subtitle">通过安全问题验证身份</p>
      </div>

      <!-- 步骤1：输入用户名 -->
      <div v-if="step === 1">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <input v-model="uname" class="form-control" placeholder="请输入您的用户名" />
        </div>
        <div v-if="errMsg" class="error-tip">{{ errMsg }}</div>
        <button class="btn btn-primary login-btn" @click="fetchQuestion" :disabled="loading">
          下一步
        </button>
      </div>

      <!-- 步骤2：回答安全问题 -->
      <div v-if="step === 2">
        <div class="question-box">{{ question }}</div>
        <div class="form-group">
          <label class="form-label">您的答案</label>
          <input v-model="answer" class="form-control" placeholder="请输入答案" />
        </div>
        <div v-if="errMsg" class="error-tip">{{ errMsg }}</div>
        <button class="btn btn-primary login-btn" @click="verifyAnswer" :disabled="loading">
          验证答案
        </button>
      </div>

      <!-- 步骤3：设置新密码 -->
      <div v-if="step === 3">
        <div class="form-group">
          <label class="form-label">新密码</label>
          <input v-model="newpasswd" type="password" class="form-control" placeholder="请输入新密码" />
        </div>
        <div class="form-group">
          <label class="form-label">确认新密码</label>
          <input v-model="confirmPasswd" type="password" class="form-control" placeholder="再次输入新密码" />
        </div>
        <div v-if="errMsg" class="error-tip">{{ errMsg }}</div>
        <button class="btn btn-primary login-btn" @click="resetPasswd" :disabled="loading">
          重置密码
        </button>
      </div>

      <!-- 步骤4：成功 -->
      <div v-if="step === 4" class="success-box">
        <div style="font-size:40px;margin-bottom:12px;">✅</div>
        <p>密码重置成功！</p>
        <RouterLink to="/login" class="btn btn-primary login-btn" style="margin-top:16px;display:flex;">
          返回登录
        </RouterLink>
      </div>

      <div class="login-links" v-if="step < 4">
        <RouterLink to="/login">返回登录</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { authApi } from '@/api/index.js'

const step          = ref(1)
const uname         = ref('')
const question      = ref('')
const answer        = ref('')
const newpasswd     = ref('')
const confirmPasswd = ref('')
const errMsg        = ref('')
const loading       = ref(false)

async function fetchQuestion() {
  if (!uname.value.trim()) { errMsg.value = '请输入用户名'; return }
  loading.value = true; errMsg.value = ''
  try {
    const res = await authApi.getSecQuestion(uname.value.trim())
    if (res.code === 200) { question.value = res.data.question; step.value = 2 }
    else errMsg.value = res.msg
  } catch (e) { errMsg.value = e.message }
  finally { loading.value = false }
}

async function verifyAnswer() {
  if (!answer.value.trim()) { errMsg.value = '请输入答案'; return }
  loading.value = true; errMsg.value = ''
  try {
    const res = await authApi.verifyAnswer({ uname: uname.value, answer: answer.value })
    if (res.code === 200) step.value = 3
    else errMsg.value = res.msg
  } catch (e) { errMsg.value = e.message }
  finally { loading.value = false }
}

async function resetPasswd() {
  if (!newpasswd.value) { errMsg.value = '请输入新密码'; return }
  if (newpasswd.value !== confirmPasswd.value) { errMsg.value = '两次密码不一致'; return }
  loading.value = true; errMsg.value = ''
  try {
    const res = await authApi.resetPasswd({ uname: uname.value, answer: answer.value, newpasswd: newpasswd.value })
    if (res.code === 200) step.value = 4
    else errMsg.value = res.msg
  } catch (e) { errMsg.value = e.message }
  finally { loading.value = false }
}
</script>

<style scoped>
.login-page { min-height: 100vh; background: var(--bg-dark); display: flex; align-items: center; justify-content: center; }
.login-box { width: 420px; background: var(--bg-panel); border: 1px solid var(--border-color); border-radius: 12px; padding: 40px 36px; }
.login-header { text-align: center; margin-bottom: 28px; }
.login-icon { font-size: 40px; margin-bottom: 10px; }
.login-title { font-size: 18px; font-weight: 700; }
.login-subtitle { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.login-btn { width: 100%; justify-content: center; padding: 10px; font-size: 14px; margin-top: 4px; }
.error-tip { background: #3d0c0c; border: 1px solid var(--danger); border-radius: 6px; padding: 8px 12px; color: #f85149; font-size: 13px; margin-bottom: 12px; }
.question-box { background: #0d2840; border: 1px solid var(--accent); border-radius: 6px; padding: 12px 16px; color: #58a6ff; font-size: 14px; margin-bottom: 16px; }
.success-box { text-align: center; padding: 20px 0; color: #3fb950; }
.login-links { text-align: center; margin-top: 16px; font-size: 13px; }
</style>

