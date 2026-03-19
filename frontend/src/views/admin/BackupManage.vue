<template>
  <div>
    <div class="page-header">
      <div class="page-title">数据备份</div>
      <button class="btn btn-primary btn-sm" @click="doBackup" :disabled="backing">
        {{ backing ? '备份中...' : '🗄 立即备份' }}
      </button>
    </div>
    <div class="card">
      <div class="section-title">备份记录</div>
      <table class="data-table">
        <thead><tr><th>备份目录名</th><th>完整路径</th></tr></thead>
        <tbody>
          <tr v-for="b in backups" :key="b.name">
            <td>{{ b.name }}</td>
            <td><span style="font-family:var(--font-mono);font-size:12px;color:var(--text-secondary)">{{ b.path }}</span></td>
          </tr>
        </tbody>
      </table>
      <div class="empty-state" v-if="!backups.length"><div class="icon">💾</div><p>暂无备份记录</p></div>
    </div>
    <div class="card" style="margin-top:16px">
      <div class="section-title">备份说明</div>
      <ul style="color:var(--text-secondary);font-size:13px;line-height:2;padding-left:20px">
        <li>点击"立即备份"将当前所有上传源码和报告文件备份到 backup/ 目录</li>
        <li>数据库备份请使用 Navicat 或 mysqldump 手动导出</li>
        <li>建议定期执行备份并将备份文件转移至安全存储位置</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { systemApi } from '@/api/index.js'
import { toast } from '@/utils/toast.js'

const backups=ref([]),backing=ref(false)

async function loadBackups(){
  const res=await systemApi.backupList()
  if(res.code===200)backups.value=res.data
}

async function doBackup(){
  backing.value=true
  try{
    const res=await systemApi.backup()
    if(res.code===200){ toast.success('备份成功！路径：'+res.data.backup_path); loadBackups() }
    else toast.error(res.msg)
  }finally{ backing.value=false }
}

onMounted(loadBackups)
</script>
<style scoped>
.section-title{font-size:14px;font-weight:600;margin-bottom:14px}
</style>

