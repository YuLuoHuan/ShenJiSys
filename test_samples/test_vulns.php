<?php
/**
 * PHP 测试样本 - 包含多种安全漏洞（仅用于审计工具测试）
 */

// ===== 1. PHP 代码执行（规则5：直接调用危险函数） =====
eval($_POST['tpl']);                   // 漏洞：直接eval用户输入
eval("echo " . $_GET['code'] . ";");  // 漏洞：eval拼接用户输入

// ===== 2. 文件包含（规则8：用户输入直接用于文件加载） =====
include($_GET['page']);                // 漏洞：任意文件包含
include("modules/" . $_GET['mod']);   // 漏洞：拼接路径文件包含

// ===== 3. 敏感信息硬编码（规则6：password\s*=） =====
$password = "Mysql@2026";             // 漏洞：密码硬编码
$db_password = "Redis#Pass123";       // 漏洞：密码硬编码

// ===== 4. 路径穿越（规则7：\.\.\/） =====
$file = file_get_contents("/var/www/uploads/../../../etc/" . $_GET['f']);  // 漏洞：路径穿越

// ===== 正常代码（不应触发） =====
function safe_include($mod) {
    $allowed = ['home', 'about', 'contact'];
    if (in_array($mod, $allowed)) {
        require $mod . '.php';   // 白名单限制，安全
    }
}
?>


