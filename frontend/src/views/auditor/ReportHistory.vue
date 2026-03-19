<template>
  <div>
    <div class="page-header">
      <div class="page-title">历史报告 <span>共 {{ total }} 份</span></div>
      <RouterLink to="/auditor/reports/generate" class="btn btn-primary btn-sm">+ 生成新报告</RouterLink>
    </div>
    <div class="card">
      <table class="data-table">
        <thead><tr><th>ID</th><th>报告名称</th><th>项目</th><th>生成时间</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="r in list" :key="r.repid">
            <td>{{ r.repid }}</td>
            <td>{{ r.repname }}</td>
            <td>{{ r.pname }}</td>
            <td>{{ r.createtime?.slice(0,16) }}</td>
            <td>
              <RouterLink :to="`/auditor/reports/${r.repid}`" class="btn btn-ghost btn-sm">查看</RouterLink>
              <a :href="downloadUrl(r.repid)" class="btn btn-ghost btn-sm" style="margin-left:4px">PDF</a>
              <button class="btn btn-danger btn-sm" style="margin-left:4px" @click="delRep(r)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="empty-state" v-if="!list.length"><div class="icon">📄</div><p>暂无报告，请先生成审计报告</p></div>
      <div class="pagination">
        <button class="page-btn" :disabled="page<=1" @click="page--;load()">上一页</button>
        <span class="page-btn active">{{ page }}</span>
        <button class="page-btn" :disabled="page*size>=total" @click="page++;load()">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { reportApi } from '@/api/index.js'
import { useUserStore } from '@/stores/user.js'
import { toast } from '@/utils/toast.js'

const store=useUserStore()
const list=ref([]),total=ref(0),page=ref(1),size=ref(10)
const downloadUrl=repid=>reportApi.download(repid)

async function load(){
  const res=await reportApi.list({page:page.value,size:size.value,uid:store.user?.uid})
  if(res.code===200){list.value=res.data.list;total.value=res.data.total}
}
async function delRep(r){
  if(!confirm(`确认删除报告"${r.repname}"？`))return
  const res=await reportApi.del(r.repid)
  if(res.code===200){toast.success('删除成功');load()}else toast.error(res.msg)
}
onMounted(load)
</script>

