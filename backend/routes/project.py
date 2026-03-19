# -*- coding: utf-8 -*-
"""
项目管理接口：创建、修改、删除、查询项目
"""
import os
from flask import Blueprint, request
from datetime import datetime
from backend.db import query_one, query_all, execute, execute_lastid, ok, fail

project_bp = Blueprint('project', __name__)

UPLOAD_BASE = 'uploads'


@project_bp.route('/list', methods=['GET'])
def list_projects():
    """获取项目列表（分页，支持按创建人过滤）"""
    page  = int(request.args.get('page', 1))
    size  = int(request.args.get('size', 10))
    uid   = request.args.get('uid')         # 审计员只看自己的项目
    kw    = request.args.get('keyword', '').strip()
    offset = (page - 1) * size
    wheres, args = [], []
    if uid:
        wheres.append('p.ownerid=%s'); args.append(uid)
    if kw:
        wheres.append('p.pname LIKE %s'); args.append(f'%{kw}%')
    where_sql = ('WHERE ' + ' AND '.join(wheres)) if wheres else ''
    sql = (f'SELECT p.pid,p.pname,p.pdesc,p.language,p.sourcepath,p.ownerid,'
           f'u.realname AS ownername,p.status,p.createtime,p.updatetime '
           f'FROM project p LEFT JOIN userinfo u ON u.uid=p.ownerid '
           f'{where_sql} ORDER BY p.pid DESC LIMIT %s OFFSET %s')
    args += [size, offset]
    rows = query_all(sql, args)
    cnt_args = args[:-2]
    total = query_one(f'SELECT COUNT(*) AS cnt FROM project p {where_sql}', cnt_args or None)['cnt']
    return ok({'list': rows, 'total': total})


@project_bp.route('/detail', methods=['GET'])
def detail():
    """获取项目详情"""
    pid = request.args.get('pid')
    if not pid:
        return fail('pid不能为空')
    row = query_one(
        'SELECT p.*,u.realname AS ownername FROM project p '
        'LEFT JOIN userinfo u ON u.uid=p.ownerid WHERE p.pid=%s',
        (pid,)
    )
    if not row:
        return fail('项目不存在', 404)
    return ok(row)


@project_bp.route('/add', methods=['POST'])
def add_project():
    """创建新项目"""
    data = request.get_json(force=True)
    pname    = data.get('pname', '').strip()
    pdesc    = data.get('pdesc', '').strip()
    language = data.get('language', '').strip()
    ownerid  = data.get('ownerid')
    if not pname or not language or not ownerid:
        return fail('必填字段不完整')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 为项目创建上传目录占位
    pid = execute_lastid(
        'INSERT INTO project(pname,pdesc,language,sourcepath,ownerid,status,createtime) '
        'VALUES(%s,%s,%s,%s,%s,0,%s)',
        (pname, pdesc, language, '', ownerid, now)
    )
    sourcepath = f'{UPLOAD_BASE}/proj_{pid}'
    os.makedirs(sourcepath, exist_ok=True)
    execute('UPDATE project SET sourcepath=%s WHERE pid=%s', (sourcepath, pid))
    return ok({'pid': pid}, '项目创建成功')


@project_bp.route('/update', methods=['POST'])
def update_project():
    """修改项目信息"""
    data = request.get_json(force=True)
    pid = data.get('pid')
    if not pid:
        return fail('pid不能为空')
    sets, args = [], []
    for field in ('pname', 'pdesc', 'language'):
        val = data.get(field)
        if val is not None:
            sets.append(f'{field}=%s'); args.append(val)
    if not sets:
        return fail('无可更新字段')
    sets.append('updatetime=%s')
    args.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    args.append(pid)
    execute(f"UPDATE project SET {','.join(sets)} WHERE pid=%s", args)
    return ok(msg='项目更新成功')


@project_bp.route('/delete', methods=['POST'])
def delete_project():
    """删除项目（级联删除任务、漏洞、报告）"""
    data = request.get_json(force=True)
    pid = data.get('pid')
    if not pid:
        return fail('pid不能为空')
    tids = query_all('SELECT tid FROM scantask WHERE pid=%s', (pid,))
    for t in tids:
        execute('DELETE FROM vulninfo WHERE tid=%s', (t['tid'],))
        execute('DELETE FROM auditreport WHERE tid=%s', (t['tid'],))
    execute('DELETE FROM scantask WHERE pid=%s', (pid,))
    execute('DELETE FROM project WHERE pid=%s', (pid,))
    return ok(msg='项目删除成功')


@project_bp.route('/stats', methods=['GET'])
def stats():
    """项目总体统计"""
    total    = query_one('SELECT COUNT(*) AS cnt FROM project')['cnt']
    scanning = query_one('SELECT COUNT(*) AS cnt FROM project WHERE status=1')['cnt']
    done     = query_one('SELECT COUNT(*) AS cnt FROM project WHERE status=2')['cnt']
    pending  = query_one('SELECT COUNT(*) AS cnt FROM project WHERE status=0')['cnt']
    return ok({'total': total, 'scanning': scanning, 'done': done, 'pending': pending})

