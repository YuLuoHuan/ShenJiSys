# -*- coding: utf-8 -*-
import pymysql, os, sys

# 模拟 app.py 的 chdir
os.chdir(os.path.dirname(os.path.abspath(__file__)))
cwd = os.getcwd()
print('工作目录:', cwd)
print()

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456',
                       database='audit_platform', charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()
cur.execute('SELECT pid, pname, language, sourcepath FROM project ORDER BY pid')
rows = cur.fetchall()
conn.close()

for r in rows:
    sp = r['sourcepath']
    abs_sp = os.path.abspath(sp)   # 相对路径转绝对路径
    exists = os.path.isdir(abs_sp)
    print(f"pid={r['pid']}  lang={r['language']}  sourcepath={sp}")
    print(f"  绝对路径: {abs_sp}")
    print(f"  目录存在: {exists}")
    if exists:
        all_files = []
        for root, dirs, files in os.walk(abs_sp):
            dirs[:] = [d for d in dirs if d not in ('__pycache__', 'node_modules', '.git')]
            for f in files:
                all_files.append(os.path.join(root, f).replace(abs_sp, ''))
        print(f"  文件({len(all_files)}个): {all_files}")
    print()

# 额外测试：扫描引擎对某个目录的识别
print('=' * 50)
print('测试扫描引擎 get_scannable_files:')
sys.path.insert(0, cwd)
from backend.engine.scanner import get_scannable_files
for r in rows:
    sp = r['sourcepath']
    files = get_scannable_files(sp, r['language'])
    print(f"pid={r['pid']} lang={r['language']} sourcepath={sp} => 找到{len(files)}个文件: {files}")

