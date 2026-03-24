<template>
  <div class="register-page">
    <div class="register-box">
      <div class="register-header">
        <div class="register-icon">🛡</div>
        <h1 class="register-title">用户注册</h1>
        <p class="register-subtitle">创建您的代码审计平台账户</p>
      </div>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <input v-model="form.uname" class="form-control" placeholder="3-20位字母、数字或下划线" required />
          <div v-if="errors.uname" class="field-error">{{ errors.uname }}</div>
        </div>
        <div class="form-group">
          <label class="form-label">真实姓名</label>
          <input v-model="form.realname" class="form-control" placeholder="请输入您的真实姓名" required />
          <div v-if="errors.realname" class="field-error">{{ errors.realname }}</div>
        </div>
        <div class="form-group">
          <label class="form-label">邮箱</label>
          <input v-model="form.email" type="email" class="form-control" placeholder="请输入有效邮箱地址" required />
          <div v-if="errors.email" class="field-error">{{ errors.email }}</div>
        </div>
        <div class="form-group">
          <label class="form-label">密码</label>
          <input v-model="form.passwd" type="password" class="form-control" placeholder="至少8位，包含大小写字母、数字和特殊字符" required />
          <div class="password-strength">
            <div class="strength-bar" :class="strengthClass"></div>
            <span class="strength-text">{{ strengthText }}</span>
          </div>
          <div v-if="errors.passwd" class="field-error">{{ errors.passwd }}</div>
        </div>
        <div class="form-group">
          <label class="form-label">确认密码</label>
          <input v-model="form.confirmPasswd" type="password" class="form-control" placeholder="请再次输入密码" required />
          <div v-if="errors.confirmPasswd" class="field-error">{{ errors.confirmPasswd }}</div>
        </div>
        <div class="form-group">
          <label class="form-label">邀请码（选填）</label>
          <input v-model="form.invite_code" class="form-control" placeholder="如有邀请码请填写" />
          <div class="form-hint">无邀请码将注册为审计员角色</div>
        </div>
        <div v-if="errMsg" class="error-tip">{{ errMsg }}</div>
        <button type="submit" class="btn btn-primary register-btn" :disabled="loading">
          {{ loading ? '注册中...' : '注 册' }}
        </button>
      </form>
      <div class="register-links">
        已有账户？<RouterLink to="/login">立即登录</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { authApi } from '@/api/index.js'

const router = useRouter()
const loading = ref(false)
const errMsg = ref('')
const form = ref({
  uname: '',
  realname: '',
  email: '',
  passwd: '',
  confirmPasswd: '',
  invite_code: ''
})

const errors = ref({
  uname: '',
  realname: '',
  email: '',
  passwd: '',
  confirmPasswd: ''
})

// 密码强度计算
const passwordStrength = computed(() => {
  const password = form.value.passwd
  if (!password) return { score: 0, text: '未输入' }

  let score = 0
  if (password.length >= 8) score += 1
  if (password.length >= 12) score += 1
  if (/[a-z]/.test(password)) score += 1
  if (/[A-Z]/.test(password)) score += 1
  if (/\d/.test(password)) score += 1
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 1

  if (score >= 5) return { score, text: '非常强' }
  if (score >= 4) return { score, text: '强' }
  if (score >= 3) return { score, text: '中等' }
  if (score >= 2) return { score, text: '弱' }
  return { score, text: '非常弱' }
})

const strengthClass = computed(() => {
  const score = passwordStrength.value.score
  if (score >= 5) return 'strength-very-strong'
  if (score >= 4) return 'strength-strong'
  if (score >= 3) return 'strength-medium'
  if (score >= 2) return 'strength-weak'
  return 'strength-very-weak'
})

const strengthText = computed(() => `密码强度：${passwordStrength.value.text}`)

// 表单验证
function validateForm() {
  let valid = true
  errors.value = { uname: '', realname: '', email: '', passwd: '', confirmPasswd: '' }

  // 用户名验证
  if (!form.value.uname) {
    errors.value.uname = '用户名不能为空'
    valid = false
  } else if (!/^[a-zA-Z0-9_]{3,20}$/.test(form.value.uname)) {
    errors.value.uname = '用户名只能包含字母、数字和下划线，长度3-20位'
    valid = false
  }

  // 真实姓名验证
  if (!form.value.realname) {
    errors.value.realname = '真实姓名不能为空'
    valid = false
  }

  // 邮箱验证
  if (!form.value.email) {
    errors.value.email = '邮箱不能为空'
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    errors.value.email = '邮箱格式不正确'
    valid = false
  }

  // 密码验证
  if (!form.value.passwd) {
    errors.value.passwd = '密码不能为空'
    valid = false
  } else if (form.value.passwd.length < 8) {
    errors.value.passwd = '密码长度至少8位'
    valid = false
  } else if (passwordStrength.value.score < 3) {
    errors.value.passwd = '密码强度不足，请使用更复杂的密码'
    valid = false
  }

  // 确认密码验证
  if (!form.value.confirmPasswd) {
    errors.value.confirmPasswd = '请确认密码'
    valid = false
  } else if (form.value.passwd !== form.value.confirmPasswd) {
    errors.value.confirmPasswd = '两次输入的密码不一致'
    valid = false
  }

  return valid
}

async function handleRegister() {
  if (!validateForm()) return

  loading.value = true
  errMsg.value = ''

  try {
    const payload = {
      uname: form.value.uname,
      passwd: form.value.passwd,
      realname: form.value.realname,
      email: form.value.email,
      invite_code: form.value.invite_code
    }

    const res = await authApi.register(payload)
    if (res.code === 200) {
      // 注册成功，跳转到登录页
      router.push({
        path: '/login',
        query: { registered: 'true', email: form.value.email }
      })
    } else {
      errMsg.value = res.msg
    }
  } catch (e) {
    errMsg.value = e.message || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: var(--bg-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.register-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 50%, #1f6feb18 0, transparent 50%),
    radial-gradient(circle at 80% 20%, #8957e518 0, transparent 40%);
  pointer-events: none;
}
.register-box {
  width: 420px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 40px 36px;
  position: relative;
  z-index: 1;
}
.register-header { text-align: center; margin-bottom: 32px; }
.register-icon { font-size: 48px; margin-bottom: 12px; }
.register-title { font-size: 18px; font-weight: 700; color: var(--text-primary); }
.register-subtitle { font-size: 12px; color: var(--text-muted); margin-top: 4px; letter-spacing: 0.5px; }

.form-group { margin-bottom: 20px; }
.form-label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}
.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-input);
  color: var(--text-primary);
  font-size: 14px;
  transition: border-color 0.2s;
}
.form-control:focus {
  outline: none;
  border-color: var(--primary);
}
.form-hint {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}
.field-error {
  font-size: 12px;
  color: var(--danger);
  margin-top: 4px;
}

.password-strength {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}
.strength-bar {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  background: var(--border-color);
  overflow: hidden;
  position: relative;
}
.strength-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 0%;
  transition: width 0.3s, background-color 0.3s;
}
.strength-very-weak::after { width: 20%; background: var(--danger); }
.strength-weak::after { width: 40%; background: #ff6b6b; }
.strength-medium::after { width: 60%; background: #ffa726; }
.strength-strong::after { width: 80%; background: #4caf50; }
.strength-very-strong::after { width: 100%; background: #2e7d32; }
.strength-text {
  font-size: 12px;
  color: var(--text-muted);
  min-width: 70px;
}

.error-tip {
  background: #3d0c0c;
  border: 1px solid var(--danger);
  border-radius: 6px;
  padding: 8px 12px;
  color: #f85149;
  font-size: 13px;
  margin-bottom: 12px;
}
.register-btn {
  width: 100%;
  justify-content: center;
  padding: 10px;
  font-size: 14px;
  margin-top: 4px;
}
.register-links {
  text-align: center;
  margin-top: 16px;
  font-size: 13px;
  color: var(--text-muted);
}
.register-links a {
  color: var(--primary);
  text-decoration: none;
  margin-left: 4px;
}
.register-links a:hover {
  text-decoration: underline;
}
</style>