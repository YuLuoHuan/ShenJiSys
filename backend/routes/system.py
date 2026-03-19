# -*- coding: utf-8 -*-
"""
系统设置接口：参数配置、邮件通知、数据备份、统计仪表盘
"""
import os
import shutil
from datetime import datetime
from flask import Blueprint, request
from backend.db import query_one, query_all, execute, ok, fail

system_bp = Blueprint('system', __name__)

BACKUP_DIR = 'backup'
os.makedirs(BACKUP_DIR, exist_ok=True)


@system_bp.route('/config/list', methods=['GET'])
def list_configs():
    """获取所有系统配置"""
    rows = query_all('SELECT * FROM sysconfig ORDER BY cfgid')
    return ok(rows)


@system_bp.route('/config/get', methods=['GET'])
def get_config():
    """获取单项配置"""
    cfgkey = request.args.get('cfgkey', '').strip()
    if not cfgkey:
        return fail('cfgkey不能为空')
    row = query_one('SELECT * FROM sysconfig WHERE cfgkey=%s', (cfgkey,))
    if not row:
        return fail('配置项不存在', 404)
    return ok(row)


@system_bp.route('/config/update', methods=['POST'])
def update_config():
    """更新系统配置（批量）"""
    data = request.get_json(force=True)
    configs = data.get('configs', [])   # [{cfgkey, cfgvalue}, ...]
    if not configs:
        return fail('configs不能为空')
    for item in configs:
        key = item.get('cfgkey', '').strip()
        val = item.get('cfgvalue', '')
        if key:
            exist = query_one('SELECT cfgid FROM sysconfig WHERE cfgkey=%s', (key,))
            if exist:
                execute('UPDATE sysconfig SET cfgvalue=%s WHERE cfgkey=%s', (val, key))
            else:
                execute(
                    'INSERT INTO sysconfig(cfgkey,cfgvalue) VALUES(%s,%s)',
                    (key, val)
                )
    return ok(msg='配置更新成功')


@system_bp.route('/email/test', methods=['POST'])
def test_email():
    """测试邮件发送配置"""
    import smtplib
    from email.mime.text import MIMEText
    cfg = {r['cfgkey']: r['cfgvalue'] for r in query_all('SELECT cfgkey,cfgvalue FROM sysconfig')}
    host    = cfg.get('email_host', '')
    port    = int(cfg.get('email_port', 465))
    user    = cfg.get('email_user', '')
    passwd  = cfg.get('email_passwd', '')
    enabled = cfg.get('email_enabled', '0')
    if enabled != '1':
        return fail('邮件通知未启用')
    to_addr = request.get_json(force=True).get('to', user)
    try:
        msg = MIMEText('这是来自代码审计系统的测试邮件。', 'plain', 'utf-8')
        msg['Subject'] = '代码审计系统 - 邮件配置测试'
        msg['From']    = user
        msg['To']      = to_addr
        with smtplib.SMTP_SSL(host, port, timeout=10) as smtp:
            smtp.login(user, passwd)
            smtp.sendmail(user, [to_addr], msg.as_string())
        return ok(msg='测试邮件发送成功')
    except Exception as e:
        return fail(f'邮件发送失败：{str(e)}')


@system_bp.route('/backup', methods=['POST'])
def backup():
    """创建系统数据备份（备份uploads和reports目录）"""
    now    = datetime.now().strftime('%Y%m%d_%H%M%S')
    bakdir = os.path.join(BACKUP_DIR, f'backup_{now}')
    os.makedirs(bakdir, exist_ok=True)
    backed = []
    for d in ('uploads', 'reports'):
        if os.path.isdir(d):
            dst = os.path.join(bakdir, d)
            shutil.copytree(d, dst)
            backed.append(d)
    return ok({'backup_path': bakdir, 'backed': backed, 'time': now}, '备份成功')


@system_bp.route('/backup/list', methods=['GET'])
def list_backups():
    """列出所有备份"""
    items = []
    if os.path.isdir(BACKUP_DIR):
        for name in sorted(os.listdir(BACKUP_DIR), reverse=True):
            full = os.path.join(BACKUP_DIR, name)
            if os.path.isdir(full):
                items.append({'name': name, 'path': full})
    return ok(items)


@system_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """管理员总览统计数据"""
    user_total    = query_one('SELECT COUNT(*) AS cnt FROM userinfo')['cnt']
    proj_total    = query_one('SELECT COUNT(*) AS cnt FROM project')['cnt']
    proj_done     = query_one('SELECT COUNT(*) AS cnt FROM project WHERE status=2')['cnt']
    vuln_total    = query_one('SELECT COUNT(*) AS cnt FROM vulninfo')['cnt']
    vuln_critical = query_one('SELECT COUNT(*) AS cnt FROM vulninfo WHERE severity=4')['cnt']
    vuln_high     = query_one('SELECT COUNT(*) AS cnt FROM vulninfo WHERE severity=3')['cnt']
    vuln_fixed    = query_one('SELECT COUNT(*) AS cnt FROM vulninfo WHERE vulnstate=3')['cnt']
    report_total  = query_one('SELECT COUNT(*) AS cnt FROM auditreport')['cnt']
    rule_total    = query_one('SELECT COUNT(*) AS cnt FROM auditrule WHERE enabled=1')['cnt']
    # 近期漏洞趋势（按项目统计）
    trend = query_all(
        'SELECT p.pname, COUNT(v.vid) AS cnt FROM vulninfo v '
        'LEFT JOIN project p ON p.pid=v.pid GROUP BY v.pid ORDER BY cnt DESC LIMIT 5'
    )
    return ok({
        'usertotal':    user_total,
        'projtotal':    proj_total,
        'projdone':     proj_done,
        'vulntotal':    vuln_total,
        'vulncritical': vuln_critical,
        'vulnhigh':     vuln_high,
        'vulnfixed':    vuln_fixed,
        'reporttotal':  report_total,
        'ruletotal':    rule_total,
        'trend':        trend,
    })


@system_bp.route('/auditor/workbench', methods=['GET'])
def auditor_workbench():
    """审计员个人工作台统计"""
    uid = request.args.get('uid')
    if not uid:
        return fail('uid不能为空')
    scan_cnt   = query_one('SELECT COUNT(*) AS cnt FROM scantask WHERE operuid=%s', (uid,))['cnt']
    report_cnt = query_one('SELECT COUNT(*) AS cnt FROM auditreport WHERE operuid=%s', (uid,))['cnt']
    vuln_found = query_one(
        'SELECT COUNT(*) AS cnt FROM vulninfo v '
        'JOIN scantask t ON t.tid=v.tid WHERE t.operuid=%s', (uid,)
    )['cnt']
    recent_tasks = query_all(
        'SELECT t.*,p.pname FROM scantask t LEFT JOIN project p ON p.pid=t.pid '
        'WHERE t.operuid=%s ORDER BY t.tid DESC LIMIT 5',
        (uid,)
    )
    return ok({
        'scancnt':    scan_cnt,
        'reportcnt':  report_cnt,
        'vulnfound':  vuln_found,
        'recenttasks': recent_tasks,
    })

