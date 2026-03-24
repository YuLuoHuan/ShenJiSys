# -*- coding: utf-8 -*-
"""
密码安全工具模块：密码哈希、验证、强度检查
"""
import re
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """生成密码哈希"""
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)


def verify_password(hashed_password: str, password: str) -> bool:
    """验证密码是否匹配"""
    return check_password_hash(hashed_password, password)


def validate_password_strength(password: str) -> dict:
    """
    检查密码强度
    返回：{'valid': bool, 'msg': str, 'strength': int (1-5)}
    """
    if not password or len(password) < 8:
        return {'valid': False, 'msg': '密码长度至少8位', 'strength': 0}

    score = 0
    msgs = []

    # 长度评分
    if len(password) >= 12:
        score += 1
    elif len(password) >= 8:
        score += 0.5

    # 包含小写字母
    if re.search(r'[a-z]', password):
        score += 1
    else:
        msgs.append('至少包含一个小写字母')

    # 包含大写字母
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        msgs.append('至少包含一个大写字母')

    # 包含数字
    if re.search(r'\d', password):
        score += 1
    else:
        msgs.append('至少包含一个数字')

    # 包含特殊字符
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        msgs.append('至少包含一个特殊字符(!@#$%^&*等)')

    # 确定强度等级
    if score >= 4.5:
        strength = 5
        strength_text = '非常强'
    elif score >= 3.5:
        strength = 4
        strength_text = '强'
    elif score >= 2.5:
        strength = 3
        strength_text = '中等'
    elif score >= 1.5:
        strength = 2
        strength_text = '弱'
    else:
        strength = 1
        strength_text = '非常弱'

    valid = len(password) >= 8 and score >= 2.5  # 至少中等强度
    if not valid and not msgs:
        msgs.append('密码强度不足，请使用更复杂的密码')

    return {
        'valid': valid,
        'msg': '；'.join(msgs) if msgs else f'密码强度：{strength_text}',
        'strength': strength,
        'score': score
    }


def validate_email(email: str) -> bool:
    """简单的邮箱格式验证"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))