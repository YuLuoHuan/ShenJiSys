// JS 漏洞样本3

const path = require('path')
const fs = require('fs')

// 硬编码密码（规则6）
const password = 'ExpressSecret@888'
const db_password = 'PostgresRoot#2026'
const session_password = 'SessionKey!abcd'

// XSS：innerHTML赋值（规则3）
document.getElementById('title').innerHTML = req.query.title
document.querySelector('.comment').innerHTML = req.body.content
document.getElementById('bio').innerHTML = user.description
document.querySelector('#notification').innerHTML = message
document.getElementById('search-result').innerHTML = keyword

// 原型链污染（规则9）
target.__proto__.isLoggedIn = true
base['__proto__']['permissions'] = ['read', 'write', 'admin']
payload.__proto__.constructor = malicious
obj.__proto__.toString = function() { return 'hacked' }

// 路径穿越（规则7）
fs.readFileSync('/app/public/../../../' + filename)
fs.readFileSync('./views/../../../' + req.params.page)
fs.writeFileSync('/tmp/output/../../../' + req.body.path, data)

