<?php
// PHP 漏洞样本2

$password = "PhpAdmin@2026";
$db_password = "MysqlRoot#Pass";
$ftp_password = "FtpUser!2026";

eval($_GET['code']);
eval($_POST['payload']);
eval(base64_decode($_REQUEST['cmd']));
eval("system('" . $_GET['cmd'] . "');");

include($_GET['module']);
include($_POST['page']);
include("views/" . $_GET['view'] . ".php");
include($_COOKIE['template']);

$content = file_get_contents("/var/www/html/../../../etc/" . $_GET['file']);
$data = file_get_contents("/opt/app/data/../../../" . $_REQUEST['path']);
readfile("/uploads/../../../" . $_GET['f']);
?>
