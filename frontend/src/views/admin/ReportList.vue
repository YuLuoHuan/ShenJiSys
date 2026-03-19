<template>
  <div>
    <div class="page-header">
      <div class="page-title">审计报告 <span>共 {{ total }} 份</span></div>
    </div>
    <div class="card">
      <table class="data-table">
        <thead><tr><th>ID</th><th>报告名称</th><th>项目</th><th>生成人</th><th>生成时间</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="r in list" :key="r.repid">
            <td>{{ r.repid }}</td>
            <td>{{ r.repname }}</td>
            <td>{{ r.pname }}</td>
            <td>{{ r.opername }}</td>
            <td>{{ r.createtime?.slice(0,16) }}</td>
            <td>
              <RouterLink :to="`/admin/reports/${r.repid}`" class="btn btn-ghost btn-sm">查看</RouterLink>
              <a :href="downloadUrl(r.repid)" class="btn btn-ghost btn-sm" style="margin-left:4px">下载PDF</a>
              <button class="btn btn-danger btn-sm" style="margin-left:4px" @click="delRep(r)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="empty-state" v-if="!list.length"><div class="icon">📄</div><p>暂无报告</p></div>
      <div class="pagination">
        <button class="page-btn" :disabled="page<=1" @click="page--;loadList()">上一页</button>
        <span class="page-btn active">{{ page }}</span>
        <button class="page-btn" :disabled="page*size>=total" @click="page++;loadList()">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { reportApi } from '@/api/index.js'
import { toast } from '@/utils/toast.js'

const list=ref([]),total=ref(0),page=ref(1),size=ref(10)
const downloadUrl=repid=>reportApi.download(repid)

async function loadList(){
  const res=await reportApi.list({page:page.value,size:size.value})
  if(res.code===200){list.value=res.data.list;total.value=res.data.total}
}
async function delRep(r){
  if(!confirm(`确认删除报告"${r.repname}"？`))return
  const res=await reportApi.del(r.repid)
  if(res.code===200){toast.success('删除成功');loadList()}else toast.error(res.msg)
}
onMounted(loadList)
</script>

