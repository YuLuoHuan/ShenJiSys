// 所有后端接口调用
import http from '@/utils/http.js'

// ========== 认证 ==========
export const authApi = {
  login:          data  => http.post('/auth/login', data),
  register:       data  => http.post('/auth/register', data),
  getSecQuestion: uname => http.get('/auth/secquestion', { params: { uname } }),
  verifyAnswer:   data  => http.post('/auth/verifyanswer', data),
  resetPasswd:    data  => http.post('/auth/resetpasswd', data),
  changePasswd:   data  => http.post('/auth/changepasswd', data),
  setSecQuestion: data  => http.post('/auth/setsecquestion', data),
}

// ========== 用户 ==========
export const userApi = {
  list:          params => http.get('/user/list', { params }),
  detail:        uid    => http.get('/user/detail', { params: { uid } }),
  add:           data   => http.post('/user/add', data),
  update:        data   => http.post('/user/update', data),
  del:           uid    => http.post('/user/delete', { uid }),
  updateProfile: data   => http.post('/user/updateprofile', data),
  stats:         ()     => http.get('/user/stats'),
}

// ========== 项目 ==========
export const projectApi = {
  list:   params => http.get('/project/list', { params }),
  detail: pid    => http.get('/project/detail', { params: { pid } }),
  add:    data   => http.post('/project/add', data),
  update: data   => http.post('/project/update', data),
  del:    pid    => http.post('/project/delete', { pid }),
  stats:  ()     => http.get('/project/stats'),
}

// ========== 规则 ==========
export const ruleApi = {
  list:   params => http.get('/rule/list', { params }),
  detail: rid    => http.get('/rule/detail', { params: { rid } }),
  add:    data   => http.post('/rule/add', data),
  update: data   => http.post('/rule/update', data),
  del:    rid    => http.post('/rule/delete', { rid }),
  toggle: data   => http.post('/rule/toggle', data),
  stats:  ()     => http.get('/rule/stats'),
}

// ========== 扫描 ==========
export const scanApi = {
  start:      data   => http.post('/scan/start', data),
  pause:      data   => http.post('/scan/pause', data),
  resume:     data   => http.post('/scan/resume', data),
  progress:   tid    => http.get('/scan/progress', { params: { tid } }),
  list:       params => http.get('/scan/list', { params }),
  upload:     (pid, file) => {
    const fd = new FormData()
    fd.append('pid', pid)
    fd.append('file', file)
    return http.post('/scan/upload', fd)
  },
}

// ========== 漏洞 ==========
export const vulnApi = {
  list:        params => http.get('/vuln/list', { params }),
  detail:      vid    => http.get('/vuln/detail', { params: { vid } }),
  updateState: data   => http.post('/vuln/updatestate', data),
  exportUrl:   params => '/api/vuln/export?' + new URLSearchParams(params).toString(),
  stats:       params => http.get('/vuln/stats', { params }),
}

// ========== 报告 ==========
export const reportApi = {
  generate: data   => http.post('/report/generate', data),
  list:     params => http.get('/report/list', { params }),
  detail:   repid  => http.get('/report/detail', { params: { repid } }),
  download: repid  => `/api/report/download?repid=${repid}`,
  del:      repid  => http.post('/report/delete', { repid }),
}

// ========== 系统 ==========
export const systemApi = {
  configList:   ()       => http.get('/system/config/list'),
  configUpdate: data     => http.post('/system/config/update', data),
  testEmail:    data     => http.post('/system/email/test', data),
  backup:       ()       => http.post('/system/backup'),
  backupList:   ()       => http.get('/system/backup/list'),
  dashboard:    ()       => http.get('/system/dashboard'),
  workbench:    uid      => http.get('/system/auditor/workbench', { params: { uid } }),
}

