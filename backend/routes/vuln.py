# -*- coding: utf-8 -*-
"""
漏洞管理接口：查询、筛选、状态标记、导出
"""
import csv
import io
from flask import Blueprint, request, Response
from backend.db import query_one, query_all, execute, ok, fail

vuln_bp = Blueprint('vuln', __name__)

# 严重等级标签
SEVERITY_LABEL = {1: '低危', 2: '中危', 3: '高危', 4: '危急'}
# 漏洞状态标签
STATE_LABEL = {0: '未处理', 1: '已确认', 2: '误报', 3: '已修复'}


def _build_vuln_sql(pid=None, tid=None, severity=None, vulnstate=None, keyword=None):
    """构建漏洞查询WHERE子句"""
    wheres, args = [], []
    if pid:
        wheres.append('v.pid=%s'); args.append(pid)
    if tid:
        wheres.append('v.tid=%s'); args.append(tid)
    if severity:
        wheres.append('v.severity=%s'); args.append(int(severity))
    if vulnstate is not None and vulnstate != '':
        wheres.append('v.vulnstate=%s'); args.append(int(vulnstate))
    if keyword:
        wheres.append('(v.filepath LIKE %s OR v.codesnip LIKE %s)')
        args += [f'%{keyword}%', f'%{keyword}%']
    where_sql = ('WHERE ' + ' AND '.join(wheres)) if wheres else ''
    return where_sql, args


@vuln_bp.route('/list', methods=['GET'])
def list_vulns():
    """漏洞列表（分页、多条件筛选）"""
    page      = int(request.args.get('page', 1))
    size      = int(request.args.get('size', 20))
    pid       = request.args.get('pid')
    tid       = request.args.get('tid')
    severity  = request.args.get('severity')
    vulnstate = request.args.get('vulnstate', '')
    keyword   = request.args.get('keyword', '').strip()
    offset    = (page - 1) * size
    where_sql, args = _build_vuln_sql(pid, tid, severity, vulnstate, keyword)
    rows = query_all(
        f'SELECT v.*,r.rname,r.category,r.suggestion,p.pname FROM vulninfo v '
        f'LEFT JOIN auditrule r ON r.rid=v.rid '
        f'LEFT JOIN project p ON p.pid=v.pid '
        f'{where_sql} ORDER BY v.severity DESC,v.vid DESC LIMIT %s OFFSET %s',
        args + [size, offset]
    )
    total = query_one(
        f'SELECT COUNT(*) AS cnt FROM vulninfo v {where_sql}', args or None
    )['cnt']
    return ok({'list': rows, 'total': total})


@vuln_bp.route('/detail', methods=['GET'])
def detail():
    """漏洞详情"""
    vid = request.args.get('vid')
    if not vid:
        return fail('vid不能为空')
    row = query_one(
        'SELECT v.*,r.rname,r.category,r.suggestion,p.pname FROM vulninfo v '
        'LEFT JOIN auditrule r ON r.rid=v.rid '
        'LEFT JOIN project p ON p.pid=v.pid WHERE v.vid=%s',
        (vid,)
    )
    if not row:
        return fail('漏洞不存在', 404)
    return ok(row)


@vuln_bp.route('/updatestate', methods=['POST'])
def update_state():
    """标记漏洞状态"""
    data      = request.get_json(force=True)
    vid       = data.get('vid')
    vulnstate = data.get('vulnstate')
    remark    = data.get('remark', '').strip()
    if vid is None or vulnstate is None:
        return fail('参数不完整')
    execute(
        'UPDATE vulninfo SET vulnstate=%s,remark=%s WHERE vid=%s',
        (int(vulnstate), remark, vid)
    )
    return ok(msg=f'漏洞状态已更新为：{STATE_LABEL.get(int(vulnstate), "未知")}')


@vuln_bp.route('/export', methods=['GET'])
def export_vulns():
    """导出漏洞数据为CSV"""
    pid       = request.args.get('pid')
    tid       = request.args.get('tid')
    severity  = request.args.get('severity')
    vulnstate = request.args.get('vulnstate', '')
    where_sql, args = _build_vuln_sql(pid, tid, severity, vulnstate)
    rows = query_all(
        f'SELECT v.vid,p.pname,r.rname,r.category,v.filepath,v.lineno,'
        f'v.severity,v.vulnstate,v.remark FROM vulninfo v '
        f'LEFT JOIN auditrule r ON r.rid=v.rid '
        f'LEFT JOIN project p ON p.pid=v.pid '
        f'{where_sql} ORDER BY v.severity DESC',
        args or None
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['漏洞ID', '项目名称', '规则名称', '漏洞类别', '文件路径', '行号', '严重等级', '处理状态', '备注'])
    for r in rows:
        writer.writerow([
            r['vid'], r['pname'], r['rname'], r['category'],
            r['filepath'], r['lineno'],
            SEVERITY_LABEL.get(r['severity'], str(r['severity'])),
            STATE_LABEL.get(r['vulnstate'], str(r['vulnstate'])),
            r['remark'] or ''
        ])
    csv_data = '\ufeff' + output.getvalue()   # 添加BOM，Excel可直接识别UTF-8
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=vuln_export.csv'}
    )


@vuln_bp.route('/stats', methods=['GET'])
def stats():
    """漏洞统计（按严重等级、状态）"""
    pid = request.args.get('pid')
    where_sql = 'WHERE pid=%s' if pid else ''
    args = (pid,) if pid else None
    by_sev = query_all(
        f'SELECT severity,COUNT(*) AS cnt FROM vulninfo {where_sql} GROUP BY severity',
        args
    )
    by_state = query_all(
        f'SELECT vulnstate,COUNT(*) AS cnt FROM vulninfo {where_sql} GROUP BY vulnstate',
        args
    )
    total = query_one(
        f'SELECT COUNT(*) AS cnt FROM vulninfo {where_sql}',
        args
    )['cnt']
    return ok({'total': total, 'byseverity': by_sev, 'bystate': by_state})

