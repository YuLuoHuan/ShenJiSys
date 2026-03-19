# -*- coding: utf-8 -*-
"""
认证相关接口：登录、找回密码、修改密码
"""
from flask import Blueprint, request
from backend.db import query_one, execute, ok, fail

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json(force=True)
    uname = data.get('uname', '').strip()
    passwd = data.get('passwd', '').strip()
    if not uname or not passwd:
        return fail('用户名和密码不能为空')
    user = query_one(
        'SELECT uid,uname,realname,email,rolecode,status FROM userinfo WHERE uname=%s AND passwd=%s',
        (uname, passwd)
    )
    if not user:
        return fail('用户名或密码错误', 401)
    if user['status'] != 1:
        return fail('账号已被禁用，请联系管理员', 403)
    return ok(user, '登录成功')


@auth_bp.route('/secquestion', methods=['GET'])
def get_sec_question():
    """根据用户名获取安全问题（找回密码第一步）"""
    uname = request.args.get('uname', '').strip()
    if not uname:
        return fail('用户名不能为空')
    row = query_one(
        'SELECT sq.sqid, sq.question FROM secquestion sq '
        'JOIN userinfo u ON u.uid=sq.uid WHERE u.uname=%s',
        (uname,)
    )
    if not row:
        return fail('该用户未设置安全问题')
    return ok(row)


@auth_bp.route('/verifyanswer', methods=['POST'])
def verify_answer():
    """验证安全问题答案（找回密码第二步）"""
    data = request.get_json(force=True)
    uname = data.get('uname', '').strip()
    answer = data.get('answer', '').strip()
    if not uname or not answer:
        return fail('参数不完整')
    row = query_one(
        'SELECT sq.sqid FROM secquestion sq '
        'JOIN userinfo u ON u.uid=sq.uid '
        'WHERE u.uname=%s AND sq.answer=%s',
        (uname, answer)
    )
    if not row:
        return fail('答案错误', 401)
    return ok({'verified': True}, '验证通过')


@auth_bp.route('/resetpasswd', methods=['POST'])
def reset_passwd():
    """重置密码（找回密码第三步）"""
    data = request.get_json(force=True)
    uname = data.get('uname', '').strip()
    answer = data.get('answer', '').strip()
    newpasswd = data.get('newpasswd', '').strip()
    if not uname or not answer or not newpasswd:
        return fail('参数不完整')
    # 再次校验答案
    row = query_one(
        'SELECT u.uid FROM userinfo u '
        'JOIN secquestion sq ON sq.uid=u.uid '
        'WHERE u.uname=%s AND sq.answer=%s',
        (uname, answer)
    )
    if not row:
        return fail('安全问题答案错误', 401)
    execute('UPDATE userinfo SET passwd=%s WHERE uid=%s', (newpasswd, row['uid']))
    return ok(msg='密码重置成功')


@auth_bp.route('/changepasswd', methods=['POST'])
def change_passwd():
    """修改密码（已登录用户）"""
    data = request.get_json(force=True)
    uid = data.get('uid')
    oldpasswd = data.get('oldpasswd', '').strip()
    newpasswd = data.get('newpasswd', '').strip()
    if not uid or not oldpasswd or not newpasswd:
        return fail('参数不完整')
    user = query_one('SELECT uid FROM userinfo WHERE uid=%s AND passwd=%s', (uid, oldpasswd))
    if not user:
        return fail('原密码错误', 401)
    execute('UPDATE userinfo SET passwd=%s WHERE uid=%s', (newpasswd, uid))
    return ok(msg='密码修改成功')


@auth_bp.route('/setsecquestion', methods=['POST'])
def set_sec_question():
    """设置或更新安全问题"""
    data = request.get_json(force=True)
    uid = data.get('uid')
    question = data.get('question', '').strip()
    answer = data.get('answer', '').strip()
    if not uid or not question or not answer:
        return fail('参数不完整')
    exist = query_one('SELECT sqid FROM secquestion WHERE uid=%s', (uid,))
    if exist:
        execute('UPDATE secquestion SET question=%s,answer=%s WHERE uid=%s', (question, answer, uid))
    else:
        execute('INSERT INTO secquestion(uid,question,answer) VALUES(%s,%s,%s)', (uid, question, answer))
    return ok(msg='安全问题设置成功')

