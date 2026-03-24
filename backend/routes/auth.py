# -*- coding: utf-8 -*-
"""
认证相关接口：登录、注册、找回密码、修改密码
"""
import re
from flask import Blueprint, request
from backend.db import query_one, execute, execute_lastid, ok, fail
from backend.utils.password import hash_password, verify_password, validate_password_strength, validate_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json(force=True)
    uname = data.get('uname', '').strip()
    passwd = data.get('passwd', '').strip()
    if not uname or not passwd:
        return fail('用户名和密码不能为空')

    # 获取用户信息（包含密码哈希）
    user = query_one(
        'SELECT uid,uname,realname,email,rolecode,status,passwd FROM userinfo WHERE uname=%s',
        (uname,)
    )
    if not user:
        return fail('用户名或密码错误', 401)

    # 检查密码
    stored_password = user['passwd']
    password_correct = False

    # 优先尝试哈希验证
    password_correct = verify_password(stored_password, passwd)

    # 如果哈希验证失败，尝试向后兼容：明文密码比较（仅用于旧数据迁移期间）
    if not password_correct:
        password_correct = (stored_password == passwd)
        # 如果明文匹配成功，自动升级为哈希密码
        if password_correct:
            hashed = hash_password(passwd)
            execute('UPDATE userinfo SET passwd=%s WHERE uid=%s', (hashed, user['uid']))

    if not password_correct:
        return fail('用户名或密码错误', 401)

    if user['status'] != 1:
        return fail('账号已被禁用，请联系管理员', 403)

    # 返回用户信息（不包含密码）
    user_info = {
        'uid': user['uid'],
        'uname': user['uname'],
        'realname': user['realname'],
        'email': user['email'],
        'rolecode': user['rolecode'],
        'status': user['status']
    }
    return ok(user_info, '登录成功')


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json(force=True)
    uname = data.get('uname', '').strip()
    passwd = data.get('passwd', '').strip()
    realname = data.get('realname', '').strip()
    email = data.get('email', '').strip()
    invite_code = data.get('invite_code', '').strip()  # 可选邀请码

    # 基本验证
    if not uname or not passwd or not realname or not email:
        return fail('所有字段均为必填')

    # 用户名格式验证（字母数字下划线，3-20位）
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', uname):
        return fail('用户名只能包含字母、数字和下划线，长度3-20位')

    # 邮箱格式验证
    if not validate_email(email):
        return fail('邮箱格式不正确')

    # 密码强度检查
    strength_check = validate_password_strength(passwd)
    if not strength_check['valid']:
        return fail(f'密码强度不足：{strength_check["msg"]}')

    # 检查用户名是否已存在
    exist_user = query_one('SELECT uid FROM userinfo WHERE uname=%s', (uname,))
    if exist_user:
        return fail('用户名已存在')

    # 检查邮箱是否已注册
    exist_email = query_one('SELECT uid FROM userinfo WHERE email=%s', (email,))
    if exist_email:
        return fail('邮箱已被注册')

    # 如果有邀请码，检查邀请码有效性（这里简单实现，可扩展）
    rolecode = 2  # 默认审计员角色
    if invite_code:
        # 这里可以添加邀请码验证逻辑，例如邀请码对应特定角色
        # 简化：如果邀请码是特定字符串，可以赋予管理员角色
        if invite_code == 'ADMIN_REGISTER_2026':
            rolecode = 1  # 管理员
        else:
            return fail('无效的邀请码')

    # 生成密码哈希
    hashed_password = hash_password(passwd)

    # 插入用户
    from datetime import datetime
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    uid = execute_lastid(
        'INSERT INTO userinfo(uname,passwd,realname,email,rolecode,status,createtime) '
        'VALUES(%s,%s,%s,%s,%s,1,%s)',
        (uname, hashed_password, realname, email, rolecode, now)
    )

    # 注册成功，返回用户信息（不含密码）
    user_info = {
        'uid': uid,
        'uname': uname,
        'realname': realname,
        'email': email,
        'rolecode': rolecode,
        'status': 1
    }
    return ok(user_info, '注册成功')


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

    # 获取存储的答案哈希
    row = query_one(
        'SELECT sq.answer FROM secquestion sq '
        'JOIN userinfo u ON u.uid=sq.uid '
        'WHERE u.uname=%s',
        (uname,)
    )
    if not row:
        return fail('未设置安全问题', 404)

    stored_answer = row['answer']
    answer_correct = False

    # 优先尝试哈希验证
    answer_correct = verify_password(stored_answer, answer)

    # 如果哈希验证失败，尝试向后兼容：明文答案比较
    if not answer_correct:
        answer_correct = (stored_answer == answer)
        # 如果明文匹配成功，自动升级为哈希答案
        if answer_correct:
            hashed = hash_password(answer)
            execute('UPDATE secquestion SET answer=%s WHERE uid=(SELECT uid FROM userinfo WHERE uname=%s)', (hashed, uname))

    if not answer_correct:
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

    # 密码强度检查
    strength_check = validate_password_strength(newpasswd)
    if not strength_check['valid']:
        return fail(f'新密码强度不足：{strength_check["msg"]}')

    # 获取用户和安全答案
    row = query_one(
        'SELECT u.uid, sq.answer FROM userinfo u '
        'LEFT JOIN secquestion sq ON sq.uid=u.uid '
        'WHERE u.uname=%s',
        (uname,)
    )
    if not row:
        return fail('用户不存在', 404)

    if not row['answer']:
        return fail('未设置安全问题，请联系管理员重置密码', 400)

    stored_answer = row['answer']
    answer_correct = False

    # 优先尝试哈希验证
    answer_correct = verify_password(stored_answer, answer)

    # 如果哈希验证失败，尝试向后兼容：明文答案比较
    if not answer_correct:
        answer_correct = (stored_answer == answer)

    if not answer_correct:
        return fail('安全问题答案错误', 401)

    # 生成新密码哈希
    hashed_password = hash_password(newpasswd)
    execute('UPDATE userinfo SET passwd=%s WHERE uid=%s', (hashed_password, row['uid']))
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

    # 新密码强度检查
    strength_check = validate_password_strength(newpasswd)
    if not strength_check['valid']:
        return fail(f'新密码强度不足：{strength_check["msg"]}')

    # 获取用户当前密码哈希
    user = query_one('SELECT uid, passwd FROM userinfo WHERE uid=%s', (uid,))
    if not user:
        return fail('用户不存在', 404)

    stored_password = user['passwd']
    old_password_correct = False

    # 优先尝试哈希验证
    old_password_correct = verify_password(stored_password, oldpasswd)

    # 如果哈希验证失败，尝试向后兼容：明文密码比较
    if not old_password_correct:
        old_password_correct = (stored_password == oldpasswd)

    if not old_password_correct:
        return fail('原密码错误', 401)

    # 生成新密码哈希
    hashed_password = hash_password(newpasswd)
    execute('UPDATE userinfo SET passwd=%s WHERE uid=%s', (hashed_password, uid))
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

    # 对答案进行哈希
    hashed_answer = hash_password(answer)

    exist = query_one('SELECT sqid FROM secquestion WHERE uid=%s', (uid,))
    if exist:
        execute('UPDATE secquestion SET question=%s,answer=%s WHERE uid=%s', (question, hashed_answer, uid))
    else:
        execute('INSERT INTO secquestion(uid,question,answer) VALUES(%s,%s,%s)', (uid, question, hashed_answer))
    return ok(msg='安全问题设置成功')

