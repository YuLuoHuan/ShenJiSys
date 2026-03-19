# -*- coding: utf-8 -*-
"""
审计规则管理接口：增删改查、启用禁用
"""
from flask import Blueprint, request
from backend.db import query_one, query_all, execute, execute_lastid, ok, fail

rule_bp = Blueprint('rule', __name__)


@rule_bp.route('/list', methods=['GET'])
def list_rules():
    """获取规则列表（支持按语言、类别、状态过滤）"""
    page     = int(request.args.get('page', 1))
    size     = int(request.args.get('size', 20))
    language = request.args.get('language', '').strip()
    category = request.args.get('category', '').strip()
    enabled  = request.args.get('enabled', '')
    keyword  = request.args.get('keyword', '').strip()
    offset   = (page - 1) * size
    wheres, args = [], []
    if language:
        wheres.append('language=%s'); args.append(language)
    if category:
        wheres.append('category=%s'); args.append(category)
    if enabled != '':
        wheres.append('enabled=%s'); args.append(int(enabled))
    if keyword:
        wheres.append('rname LIKE %s'); args.append(f'%{keyword}%')
    where_sql = ('WHERE ' + ' AND '.join(wheres)) if wheres else ''
    rows = query_all(
        f'SELECT * FROM auditrule {where_sql} ORDER BY rid LIMIT %s OFFSET %s',
        args + [size, offset]
    )
    total = query_one(f'SELECT COUNT(*) AS cnt FROM auditrule {where_sql}', args or None)['cnt']
    return ok({'list': rows, 'total': total})


@rule_bp.route('/detail', methods=['GET'])
def detail():
    """获取单条规则详情"""
    rid = request.args.get('rid')
    if not rid:
        return fail('rid不能为空')
    row = query_one('SELECT * FROM auditrule WHERE rid=%s', (rid,))
    if not row:
        return fail('规则不存在', 404)
    return ok(row)


@rule_bp.route('/add', methods=['POST'])
def add_rule():
    """新增审计规则"""
    data = request.get_json(force=True)
    rname    = data.get('rname', '').strip()
    category = data.get('category', '').strip()
    language = data.get('language', '').strip()
    pattern  = data.get('pattern', '').strip()
    severity = int(data.get('severity', 2))
    suggestion = data.get('suggestion', '').strip()
    if not rname or not category or not language or not pattern:
        return fail('必填字段不完整')
    rid = execute_lastid(
        'INSERT INTO auditrule(rname,category,language,pattern,severity,suggestion,enabled) '
        'VALUES(%s,%s,%s,%s,%s,%s,1)',
        (rname, category, language, pattern, severity, suggestion)
    )
    return ok({'rid': rid}, '规则创建成功')


@rule_bp.route('/update', methods=['POST'])
def update_rule():
    """修改规则内容"""
    data = request.get_json(force=True)
    rid = data.get('rid')
    if not rid:
        return fail('rid不能为空')
    sets, args = [], []
    for field in ('rname', 'category', 'language', 'pattern', 'severity', 'suggestion'):
        val = data.get(field)
        if val is not None:
            sets.append(f'{field}=%s'); args.append(val)
    if not sets:
        return fail('无可更新字段')
    args.append(rid)
    execute(f"UPDATE auditrule SET {','.join(sets)} WHERE rid=%s", args)
    return ok(msg='规则更新成功')


@rule_bp.route('/delete', methods=['POST'])
def delete_rule():
    """删除规则"""
    data = request.get_json(force=True)
    rid = data.get('rid')
    if not rid:
        return fail('rid不能为空')
    execute('DELETE FROM auditrule WHERE rid=%s', (rid,))
    return ok(msg='规则删除成功')


@rule_bp.route('/toggle', methods=['POST'])
def toggle_rule():
    """启用/禁用规则"""
    data = request.get_json(force=True)
    rid     = data.get('rid')
    enabled = data.get('enabled')   # 传入 1 或 0
    if rid is None or enabled is None:
        return fail('参数不完整')
    execute('UPDATE auditrule SET enabled=%s WHERE rid=%s', (int(enabled), rid))
    status_text = '启用' if int(enabled) == 1 else '禁用'
    return ok(msg=f'规则已{status_text}')


@rule_bp.route('/stats', methods=['GET'])
def stats():
    """规则统计"""
    total   = query_one('SELECT COUNT(*) AS cnt FROM auditrule')['cnt']
    enabled = query_one('SELECT COUNT(*) AS cnt FROM auditrule WHERE enabled=1')['cnt']
    by_cat  = query_all(
        'SELECT category, COUNT(*) AS cnt FROM auditrule GROUP BY category'
    )
    return ok({'total': total, 'enabled': enabled, 'bycategory': by_cat})

