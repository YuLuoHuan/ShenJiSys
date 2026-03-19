// JavaScript 测试样本 - 包含多种安全漏洞（仅用于审计工具测试）

// ===== 1. XSS 跨站脚本（规则3：未转义直接写入DOM） =====
document.getElementById('output').innerHTML = userInput;              // 漏洞：直接赋值用户内容
document.querySelector('.welcome').innerHTML = '<h2>' + name + '</h2>'; // 漏洞：拼接插入

// ===== 2. 原型链污染（规则9：__proto__） =====
obj.__proto__.isAdmin = true;          // 漏洞：原型链污染
target['__proto__']['role'] = 'admin'; // 漏洞：原型链污染

// ===== 3. 敏感信息硬编码（规则6：password\s*=） =====
const password = 'Mongo@2026';        // 漏洞：密码硬编码
var db_password = 'Redis#Secret';     // 漏洞：密码硬编码

// ===== 4. 路径穿越（规则7：\.\.\/） =====
const fs = require('fs');
const content = fs.readFileSync('./uploads/../../../etc/passwd');  // 漏洞：路径穿越

// ===== 正常代码（不应触发） =====
function safeRender(text) {
    const div = document.createElement('div');
    div.textContent = text;   // 使用 textContent，安全
    document.body.appendChild(div);
}


