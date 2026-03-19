<template>
  <RouterView />
  <!-- 全局 Toast 消息 -->
  <div class="toast-wrap">
    <div
      v-for="t in toastState.list"
      :key="t.id"
      :class="['toast', `toast-${t.type}`]"
    >{{ t.msg }}</div>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import { toastState } from '@/utils/toast.js'
</script>

