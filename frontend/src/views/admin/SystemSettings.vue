<template>
  <div>
    <div class="page-header">
      <div class="page-title">系统设置</div>
      <button class="btn btn-primary btn-sm" @click="saveAll">💾 保存设置</button>
    </div>
    <div class="settings-grid">
      <!-- 扫描配置 -->
      <div class="card">
        <div class="section-title">🔍 扫描参数</div>
        <div class="form-group">
          <label class="form-label">扫描超时（秒）</label>
          <input v-model="cfg.scan_timeout" class="form-control" type="number" />
        </div>
        <div class="form-group">
          <label class="form-label">单文件最大大小（字节）</label>
          <input v-model="cfg.scan_max_filesize" class="form-control" type="number" />
        </div>
        <div class="form-group">
          <label class="form-label">允许扫描的文件后缀</label>
          <input v-model="cfg.scan_file_exts" class="form-control" placeholder="py,java,php,js" />
        </div>
      </div>
      <!-- 邮件配置 -->
      <div class="card">
        <div class="section-title">📧 邮件通知</div>
        <div class="form-group">
          <label class="form-label">是否启用邮件通知</label>
          <select v-model="cfg.email_enabled" class="form-control">
            <option value="1">启用</option><option value="0">禁用</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">SMTP服务器</label>
          <input v-model="cfg.email_host" class="form-control" />
        </div>
        <div class="form-group">
          <label class="form-label">SMTP端口</label>
          <input v-model="cfg.email_port" class="form-control" type="number" />
        </div>
        <div class="form-group">
          <label class="form-label">发件人账号</label>
          <input v-model="cfg.email_user" class="form-control" />
        </div>
        <div class="form-group">
          <label class="form-label">发件人密码</label>
          <input v-model="cfg.email_passwd" type="password" class="form-control" />
        </div>
        <button class="btn btn-ghost btn-sm" @click="testEmail">发送测试邮件</button>
      </div>
      <!-- 系统信息 -->
      <div class="card">
        <div class="section-title">ℹ️ 系统信息</div>
        <div class="form-group">
          <label class="form-label">系统名称</label>
          <input v-model="cfg.system_name" class="form-control" />
        </div>
        <div class="form-group">
          <label class="form-label">系统版本</label>
          <input v-model="cfg.system_version" class="form-control" disabled />
        </div>
        <div class="form-group">
          <label class="form-label">备份保留天数</label>
          <input v-model="cfg.backup_keep_days" class="form-control" type="number" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { systemApi } from '@/api/index.js'
import { toast } from '@/utils/toast.js'

const cfg = ref({
  scan_timeout:'3600', scan_max_filesize:'10485760', scan_file_exts:'py,java,php,js',
  email_enabled:'1', email_host:'', email_port:'465', email_user:'', email_passwd:'',
  system_name:'', system_version:'', backup_keep_days:'30'
})

async function loadConfigs(){
  const res=await systemApi.configList()
  if(res.code===200){
    res.data.forEach(item=>{ cfg.value[item.cfgkey]=item.cfgvalue })
  }
}

async function saveAll(){
  const configs=Object.entries(cfg.value).map(([cfgkey,cfgvalue])=>({cfgkey,cfgvalue}))
  const res=await systemApi.configUpdate({configs})
  if(res.code===200)toast.success('配置保存成功')
  else toast.error(res.msg)
}

async function testEmail(){
  const res=await systemApi.testEmail({to:cfg.value.email_user})
  if(res.code===200)toast.success(res.msg)
  else toast.error(res.msg)
}

onMounted(loadConfigs)
</script>

<style scoped>
.settings-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.section-title{font-size:14px;font-weight:600;margin-bottom:16px;color:var(--text-primary)}
</style>

