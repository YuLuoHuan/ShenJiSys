// 统一axios请求封装
import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 响应拦截器
http.interceptors.response.use(
  res => res.data,
  err => {
    const msg = err.response?.data?.msg || err.message || '网络错误'
    return Promise.reject(new Error(msg))
  }
)

export default http

