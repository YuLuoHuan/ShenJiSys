<?php
// PHP 漏洞样本3

// 硬编码密码（规则6）
$password = "CmsAdmin@666";
$db_password = "DbPass#2026!";
$redis_password = "RedisAuth@php";

// PHP代码执行（规则5：eval同一行）
eval(stripslashes($_POST['tpl']));
eval(urldecode($_GET['exp']));
eval(str_rot13($_POST['rot']));

// 文件包含（规则8：include同一行）
include("lang/" . $_GET['lang'] . "/main.php");
include($_SERVER['HTTP_ACCEPT_LANGUAGE'] . ".php");
include("plugins/" . $_POST['plugin'] . "/init.php");

// 路径穿越（规则7）
$log = file_get_contents("/var/log/nginx/../../../" . $_GET['log']);
$cfg = file_get_contents("/etc/app/conf/../../../" . $_GET['cfg']);
readfile("/data/export/../../../" . $_POST['filename']);

// 路径穿越反斜杠（规则7）
$fp = fopen("C:\\\\inetpub\\\\wwwroot\\\\..\\\\..\\\\" . $_GET['f'], 'r');

