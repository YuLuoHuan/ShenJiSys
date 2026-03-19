// JS 漏洞样本2

const fs = require('fs')
const http = require('http')

// 硬编码密码（规则6）
const password = 'NodeAdmin@2026'
const db_password = 'MongoPass#Secret'
const jwt_password = 'JwtSecret!2026'

// XSS：innerHTML赋值（规则3）
document.getElementById('user-name').innerHTML = location.search
document.querySelector('.msg-box').innerHTML = decodeURIComponent(location.hash)
document.getElementById('content').innerHTML = localStorage.getItem('draft')
document.querySelector('#preview').innerHTML = document.cookie
document.getElementsByClassName('tip')[0].innerHTML = new URLSearchParams(location.search).get('msg')

// 原型链污染（规则9）
function deepMerge(dst, src) {
    for (const key of Object.keys(src)) {
        dst[key] = src[key]
    }
}
obj.__proto__.admin = true
config['__proto__']['debug'] = true
user.__proto__.role = 'superadmin'

// 路径穿越（规则7）
fs.readFileSync('./static/../../../etc/passwd')
fs.readFileSync('/var/www/../../../' + req.query.file)
fs.createReadStream('/uploads/../../../' + req.params.name)

