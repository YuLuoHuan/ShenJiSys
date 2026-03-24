# -*- coding: utf-8 -*-
"""
审计报告接口：生成报告、PDF导出、历史报告查询
"""
import os
from datetime import datetime
from flask import Blueprint, request, send_file
from backend.db import query_one, query_all, execute, execute_lastid, ok, fail

report_bp = Blueprint('report', __name__)

REPORT_DIR = 'reports'
os.makedirs(REPORT_DIR, exist_ok=True)

# 尝试导入reportlab，若未安装则降级为文本报告
try:
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.pagesizes import A4
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def _build_pdf(repid: int, repname: str, summary: str,
               project: dict, vulns: list, pdfpath: str):
    """使用reportlab生成PDF报告"""
    c = canvas.Canvas(pdfpath, pagesize=A4)
    width, height = A4
    # 注册中文字体（需系统安装SimSun或Arial Unicode）
    font_paths = [
        'C:/Windows/Fonts/simsun.ttc',
        'C:/Windows/Fonts/msyh.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    font_name = 'Helvetica'
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont('CJK', fp))
                font_name = 'CJK'
                break
            except Exception:
                pass

    c.setFont(font_name, 16)
    c.drawString(50, height - 60, repname)
    c.setFont(font_name, 11)
    c.drawString(50, height - 90, f'项目：{project.get("pname","N/A")}  语言：{project.get("language","N/A")}')
    c.drawString(50, height - 110, f'生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    c.drawString(50, height - 130, f'摘要：{summary}')
    c.drawString(50, height - 160, f'漏洞总数：{len(vulns)}')
    y = height - 200
    sev_map = {1: '低危', 2: '中危', 3: '高危', 4: '危急'}
    for i, v in enumerate(vulns[:50], 1):    # PDF最多展示50条
        text = f'[{sev_map.get(v["severity"],"?")}] {v["filepath"]}:{v["lineno"]}  {v.get("rname","")}'
        c.drawString(50, y, text[:100])
        y -= 20
        if y < 60:
            c.showPage()
            c.setFont(font_name, 11)
            y = height - 60
    c.save()


@report_bp.route('/generate', methods=['POST'])
def generate():
    """生成审计报告"""
    data    = request.get_json(force=True)
    tid     = data.get('tid')
    pid     = data.get('pid')
    operuid = data.get('operuid')
    repname = data.get('repname', '').strip()
    if not tid or not pid or not operuid:
        return fail('参数不完整')
    task = query_one('SELECT * FROM scantask WHERE tid=%s', (tid,))
    if not task or task['status'] != 2:
        return fail('扫描任务未完成，无法生成报告')
    proj = query_one('SELECT * FROM project WHERE pid=%s', (pid,))
    vulns = query_all(
        'SELECT v.*,r.rname FROM vulninfo v LEFT JOIN auditrule r ON r.rid=v.rid WHERE v.tid=%s',
        (tid,)
    )
    total   = len(vulns)
    serious = sum(1 for v in vulns if v['severity'] >= 3)
    summary = (repname or f'{proj["pname"]}审计报告') + \
              f'，共发现{total}处漏洞，其中高危/危急{serious}处。'
    if not repname:
        repname = f'{proj["pname"]}审计报告-{datetime.now().strftime("%Y%m%d")}'
    now    = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    repid  = execute_lastid(
        'INSERT INTO auditreport(tid,pid,operuid,repname,summary,createtime) VALUES(%s,%s,%s,%s,%s,%s)',
        (tid, pid, operuid, repname, summary, now)
    )
    pdfpath = os.path.join(REPORT_DIR, f'report_{repid}.pdf')
    if HAS_REPORTLAB:
        try:
            _build_pdf(repid, repname, summary, proj, vulns, pdfpath)
        except Exception as e:
            pdfpath = ''
    else:
        pdfpath = ''
    execute('UPDATE auditreport SET pdfpath=%s WHERE repid=%s', (pdfpath, repid))
    return ok({'repid': repid, 'repname': repname, 'summary': summary}, '报告生成成功')


@report_bp.route('/list', methods=['GET'])
def list_reports():
    """报告列表"""
    page    = int(request.args.get('page', 1))
    size    = int(request.args.get('size', 10))
    uid     = request.args.get('uid')
    pid     = request.args.get('pid')
    offset  = (page - 1) * size
    wheres, args = [], []
    if uid:
        wheres.append('r.operuid=%s'); args.append(uid)
    if pid:
        wheres.append('r.pid=%s'); args.append(pid)
    where_sql = ('WHERE ' + ' AND '.join(wheres)) if wheres else ''
    rows = query_all(
        f'SELECT r.*,p.pname,u.realname AS opername FROM auditreport r '
        f'LEFT JOIN project p ON p.pid=r.pid '
        f'LEFT JOIN userinfo u ON u.uid=r.operuid '
        f'{where_sql} ORDER BY r.repid DESC LIMIT %s OFFSET %s',
        args + [size, offset]
    )
    total = query_one(f'SELECT COUNT(*) AS cnt FROM auditreport r {where_sql}', args or None)['cnt']
    return ok({'list': rows, 'total': total})


@report_bp.route('/detail', methods=['GET'])
def detail():
    """报告详情（含漏洞列表）"""
    repid = request.args.get('repid')
    if not repid:
        return fail('repid不能为空')
    rep = query_one(
        'SELECT r.*,p.pname FROM auditreport r LEFT JOIN project p ON p.pid=r.pid WHERE r.repid=%s',
        (repid,)
    )
    if not rep:
        return fail('报告不存在', 404)
    vulns = query_all(
        'SELECT v.*,rl.rname,rl.category FROM vulninfo v '
        'LEFT JOIN auditrule rl ON rl.rid=v.rid WHERE v.tid=%s ORDER BY v.severity DESC',
        (rep['tid'],)
    )
    rep['vulns'] = vulns
    return ok(rep)


@report_bp.route('/download', methods=['GET'])
def download():
    """下载PDF报告"""
    repid = request.args.get('repid')
    if not repid:
        return fail('repid不能为空')
    rep = query_one('SELECT pdfpath,repname,tid,pid,summary FROM auditreport WHERE repid=%s', (repid,))
    if not rep:
        return fail('报告不存在', 404)

    # 如果PDF路径为空或文件不存在，尝试重新生成
    if not rep['pdfpath'] or not os.path.exists(rep['pdfpath']):
        if not HAS_REPORTLAB:
            return fail('PDF文件不存在，且reportlab未安装，无法重新生成', 404)

        # 尝试重新生成PDF
        try:
            # 获取项目信息
            proj = query_one('SELECT * FROM project WHERE pid=%s', (rep['pid'],))
            if not proj:
                return fail('关联项目不存在', 404)

            # 获取漏洞信息
            vulns = query_all(
                'SELECT v.*,r.rname FROM vulninfo v LEFT JOIN auditrule r ON r.rid=v.rid WHERE v.tid=%s',
                (rep['tid'],)
            )

            # 生成PDF路径
            pdfpath = os.path.join(REPORT_DIR, f'report_{repid}.pdf')

            # 生成PDF
            _build_pdf(
                repid=repid,
                repname=rep['repname'],
                summary=rep['summary'] or '',
                project=proj,
                vulns=vulns,
                pdfpath=pdfpath
            )

            # 更新数据库
            execute('UPDATE auditreport SET pdfpath=%s WHERE repid=%s', (pdfpath, repid))
            rep['pdfpath'] = pdfpath

        except Exception as e:
            import traceback
            traceback.print_exc()
            return fail(f'PDF重新生成失败: {str(e)}', 500)

    # 再次检查文件是否存在
    if not os.path.exists(rep['pdfpath']):
        return fail('PDF文件生成失败，请稍后重试', 404)

    return send_file(rep['pdfpath'], as_attachment=True,
                     download_name=f'{rep["repname"]}.pdf')


@report_bp.route('/delete', methods=['POST'])
def delete_report():
    """删除报告"""
    data  = request.get_json(force=True)
    repid = data.get('repid')
    if not repid:
        return fail('repid不能为空')
    rep = query_one('SELECT pdfpath FROM auditreport WHERE repid=%s', (repid,))
    if rep and rep['pdfpath'] and os.path.exists(rep['pdfpath']):
        try:
            os.remove(rep['pdfpath'])
        except Exception:
            pass
    execute('DELETE FROM auditreport WHERE repid=%s', (repid,))
    return ok(msg='报告删除成功')

