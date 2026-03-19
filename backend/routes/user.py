# -*- coding: utf-8 -*-
"""
用户管理接口：增删改查、角色分配（管理员功能）
"""
from flask import Blueprint, request
from datetime import datetime
from backend.db import query_one, query_all, execute, execute_lastid, ok, fail

user_bp = Blueprint('user', __name__)


@user_bp.route('/list', methods=['GET'])
def list_users():
    """获取用户列表（分页）"""
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    keyword = request.args.get('keyword', '').strip()
    offset = (page - 1) * size
    if keyword:
        sql = ('SELECT uid,uname,realname,email,rolecode,status,createtime '
               'FROM userinfo WHERE uname LIKE %s OR realname LIKE %s '
               'ORDER BY uid LIMIT %s OFFSET %s')
        kw = f'%{keyword}%'
        rows = query_all(sql, (kw, kw, size, offset))
        total = query_one(
            'SELECT COUNT(*) AS cnt FROM userinfo WHERE uname LIKE %s OR realname LIKE %s',
            (kw, kw)
        )['cnt']
    else:
        rows = query_all(
            'SELECT uid,uname,realname,email,rolecode,status,createtime '
            'FROM userinfo ORDER BY uid LIMIT %s OFFSET %s',
            (size, offset)
        )
        total = query_one('SELECT COUNT(*) AS cnt FROM userinfo')['cnt']
    return ok({'list': rows, 'total': total})


@user_bp.route('/detail', methods=['GET'])
def detail():
    """获取单个用户详情（包含安全问题）"""
    uid = request.args.get('uid')
    if not uid:
        return fail('uid不能为空')
    user = query_one(
        'SELECT uid,uname,realname,email,rolecode,status,createtime FROM userinfo WHERE uid=%s',
        (uid,)
    )
    if not user:
        return fail('用户不存在', 404)
    sq = query_one('SELECT question FROM secquestion WHERE uid=%s', (uid,))
    user['secquestion'] = sq['question'] if sq else None
    return ok(user)


@user_bp.route('/add', methods=['POST'])
def add_user():
    """新增用户（管理员）"""
    data = request.get_json(force=True)
    uname = data.get('uname', '').strip()
    passwd = data.get('passwd', '123456').strip()
    realname = data.get('realname', '').strip()
    email = data.get('email', '').strip()
    rolecode = int(data.get('rolecode', 2))
    if not uname or not realname or not email:
        return fail('必填字段不完整')
    exist = query_one('SELECT uid FROM userinfo WHERE uname=%s', (uname,))
    if exist:
        return fail('用户名已存在')
    uid = execute_lastid(
        'INSERT INTO userinfo(uname,passwd,realname,email,rolecode,status,createtime) '
        'VALUES(%s,%s,%s,%s,%s,1,%s)',
        (uname, passwd, realname, email, rolecode, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    return ok({'uid': uid}, '用户创建成功')


@user_bp.route('/update', methods=['POST'])
def update_user():
    """修改用户信息"""
    data = request.get_json(force=True)
    uid = data.get('uid')
    if not uid:
        return fail('uid不能为空')
    realname = data.get('realname', '').strip()
    email = data.get('email', '').strip()
    rolecode = data.get('rolecode')
    status = data.get('status')
    sets, args = [], []
    if realname:
        sets.append('realname=%s'); args.append(realname)
    if email:
        sets.append('email=%s'); args.append(email)
    if rolecode is not None:
        sets.append('rolecode=%s'); args.append(rolecode)
    if status is not None:
        sets.append('status=%s'); args.append(status)
    if not sets:
        return fail('无可更新字段')
    args.append(uid)
    execute(f"UPDATE userinfo SET {','.join(sets)} WHERE uid=%s", args)
    return ok(msg='用户信息更新成功')


@user_bp.route('/delete', methods=['POST'])
def delete_user():
    """删除用户"""
    data = request.get_json(force=True)
    uid = data.get('uid')
    if not uid:
        return fail('uid不能为空')
    execute('DELETE FROM secquestion WHERE uid=%s', (uid,))
    execute('DELETE FROM userinfo WHERE uid=%s', (uid,))
    return ok(msg='用户删除成功')


@user_bp.route('/updateprofile', methods=['POST'])
def update_profile():
    """审计员修改个人信息"""
    data = request.get_json(force=True)
    uid = data.get('uid')
    realname = data.get('realname', '').strip()
    email = data.get('email', '').strip()
    if not uid:
        return fail('uid不能为空')
    execute(
        'UPDATE userinfo SET realname=%s,email=%s WHERE uid=%s',
        (realname, email, uid)
    )
    return ok(msg='个人信息更新成功')


@user_bp.route('/stats', methods=['GET'])
def user_stats():
    """用户统计（管理员仪表盘）"""
    total = query_one('SELECT COUNT(*) AS cnt FROM userinfo')['cnt']
    admin_cnt = query_one('SELECT COUNT(*) AS cnt FROM userinfo WHERE rolecode=1')['cnt']
    auditor_cnt = query_one('SELECT COUNT(*) AS cnt FROM userinfo WHERE rolecode=2')['cnt']
    return ok({'total': total, 'admin': admin_cnt, 'auditor': auditor_cnt})

