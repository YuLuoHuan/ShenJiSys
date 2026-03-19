<template>
  <div class="login-page">
    <div class="login-box">
      <div class="login-header">
        <div class="login-icon">🛡</div>
        <h1 class="login-title">代码审计安全检测平台</h1>
        <p class="login-subtitle">Lightweight Code Audit Security Platform</p>
      </div>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <input v-model="form.uname" class="form-control" placeholder="请输入用户名" autocomplete="username" required />
        </div>
        <div class="form-group">
          <label class="form-label">密码</label>
          <input v-model="form.passwd" type="password" class="form-control" placeholder="请输入密码" autocomplete="current-password" required />
        </div>
        <div v-if="errMsg" class="error-tip">{{ errMsg }}</div>
        <button type="submit" class="btn btn-primary login-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </form>
      <div class="login-links">
        <RouterLink to="/forgot">忘记密码？</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { authApi } from '@/api/index.js'
import { useUserStore } from '@/stores/user.js'

const router  = useRouter()
const store   = useUserStore()
const loading = ref(false)
const errMsg  = ref('')
const form    = ref({ uname: '', passwd: '' })

async function handleLogin() {
  errMsg.value  = ''
  loading.value = true
  try {
    const res = await authApi.login(form.value)
    if (res.code === 200) {
      store.setUser(res.data)
      router.push(res.data.rolecode === 1 ? '/admin/dashboard' : '/auditor/workbench')
    } else {
      errMsg.value = res.msg
    }
  } catch (e) {
    errMsg.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: var(--bg-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.login-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 50%, #1f6feb18 0, transparent 50%),
    radial-gradient(circle at 80% 20%, #8957e518 0, transparent 40%);
  pointer-events: none;
}
.login-box {
  width: 400px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 40px 36px;
  position: relative;
  z-index: 1;
}
.login-header { text-align: center; margin-bottom: 32px; }
.login-icon { font-size: 48px; margin-bottom: 12px; }
.login-title { font-size: 18px; font-weight: 700; color: var(--text-primary); }
.login-subtitle { font-size: 12px; color: var(--text-muted); margin-top: 4px; letter-spacing: 0.5px; }
.login-btn { width: 100%; justify-content: center; padding: 10px; font-size: 14px; margin-top: 4px; }
.error-tip {
  background: #3d0c0c; border: 1px solid var(--danger);
  border-radius: 6px; padding: 8px 12px; color: #f85149;
  font-size: 13px; margin-bottom: 12px;
}
.login-links { text-align: center; margin-top: 16px; font-size: 13px; }
</style>

