// Toast消息工具
import { reactive } from 'vue'

export const toastState = reactive({ list: [] })

let _id = 0
export function showToast(msg, type = 'info', duration = 2500) {
  const id = ++_id
  toastState.list.push({ id, msg, type })
  setTimeout(() => {
    const idx = toastState.list.findIndex(t => t.id === id)
    if (idx !== -1) toastState.list.splice(idx, 1)
  }, duration)
}
export const toast = {
  success: msg => showToast(msg, 'success'),
  error:   msg => showToast(msg, 'error'),
  info:    msg => showToast(msg, 'info'),
}

