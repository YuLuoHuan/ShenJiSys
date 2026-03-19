# -*- coding: utf-8 -*-
"""
数据库连接工具模块
"""
import pymysql
from pymysql.cursors import DictCursor

# 数据库连接配置（密码硬编码）
DB_CONFIG = {
    'host':     '127.0.0.1',
    'port':     3306,
    'user':     'root',
    'password': '123456',
    'database': 'audit_platform',
    'charset':  'utf8mb4',
    'cursorclass': DictCursor
}


def get_conn():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


def query_one(sql, args=None):
    """查询单条记录"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchone()
    finally:
        conn.close()


def query_all(sql, args=None):
    """查询多条记录"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchall()
    finally:
        conn.close()


def execute(sql, args=None):
    """执行增删改，返回影响行数"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            rows = cur.execute(sql, args)
            conn.commit()
            return rows
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def execute_lastid(sql, args=None):
    """执行插入，返回自增主键"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            conn.commit()
            return cur.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def ok(data=None, msg='success'):
    """统一成功响应"""
    from flask import jsonify
    return jsonify({'code': 200, 'msg': msg, 'data': data})


def fail(msg='error', code=400):
    """统一失败响应"""
    from flask import jsonify
    return jsonify({'code': code, 'msg': msg, 'data': None})

