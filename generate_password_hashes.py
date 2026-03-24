#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成密码哈希并更新audit_db.sql中的初始数据
运行方式：python generate_password_hashes.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from werkzeug.security import generate_password_hash
except ImportError:
    print("错误：请先安装werkzeug (pip install Werkzeug)")
    sys.exit(1)

def hash_password(password):
    """生成密码哈希"""
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

# 需要哈希的密码（从audit_db.sql中获取）
passwords_to_hash = [
    "123456",  # admin
    "123456",  # auditor1
    "123456",  # auditor2
    "123456",  # auditor3
    "123456",  # manager1
]

# 生成哈希
hashed_passwords = [hash_password(pwd) for pwd in passwords_to_hash]

print("生成的密码哈希：")
for i, (pwd, hashed) in enumerate(zip(passwords_to_hash, hashed_passwords)):
    print(f"{i+1}. 明文: {pwd}")
    print(f"   哈希: {hashed}")
    print()

print("请手动更新audit_db.sql中的INSERT语句，将明文密码替换为上述哈希值。")
print("例如：")
print("将: (1,'admin','123456','系统管理员','admin@auditpro.com',1,1,'2026-01-01 09:00:00'),")
print("改为: (1,'admin','{hashed}','系统管理员','admin@auditpro.com',1,1,'2026-01-01 09:00:00'),".format(hashed=hashed_passwords[0]))