# -*- coding: utf-8 -*-
"""
扫描任务接口：启动、暂停、继续、查询进度、上传源码
"""
import os
import threading
import zipfile
import tarfile
from flask import Blueprint, request
from datetime import datetime
from backend.db import query_one, query_all, execute, execute_lastid, ok, fail
from backend.engine.scanner import run_scan

scan_bp = Blueprint('scan', __name__)

# 全局任务状态缓存（内存级，重启清零）
_task_status: dict = {}

# 项目根目录（绝对路径），保证线程内相对路径解析正确
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _do_scan(tid: int, pid: int, sourcepath: str, language: str):
    """后台线程：执行扫描并将结果写库"""
    # 相对路径转绝对路径，防止线程中工作目录不一致
    if not os.path.isabs(sourcepath):
        sourcepath = os.path.join(BASE_DIR, sourcepath)
    try:
        execute(
            'UPDATE scantask SET status=1,starttime=%s WHERE tid=%s',
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), tid)
        )
        execute('UPDATE project SET status=1 WHERE pid=%s', (pid,))
        # 加载启用规则（按项目语言过滤）
        rules = query_all(
            'SELECT * FROM auditrule WHERE enabled=1 AND (language=%s OR language=%s)',
            (language, 'all')
        )

        def _progress(scanned, total):
            pct = int(scanned / total * 100) if total else 100
            _task_status[tid] = {'progress': pct, 'scanned': scanned, 'total': total}
            execute(
                'UPDATE scantask SET progress=%s,scannedfiles=%s,totalfiles=%s WHERE tid=%s',
                (pct, scanned, total, tid)
            )

        hits, total_files, scanned_files = run_scan(sourcepath, language, rules, _progress)

        # 写入漏洞
        for h in hits:
            execute(
                'INSERT INTO vulninfo(tid,pid,rid,filepath,lineno,codesnip,severity,vulnstate) '
                'VALUES(%s,%s,%s,%s,%s,%s,%s,0)',
                (tid, pid, h['rid'], h['filepath'], h['lineno'], h['codesnip'], h['severity'])
            )

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        execute(
            'UPDATE scantask SET status=2,progress=100,totalfiles=%s,scannedfiles=%s,endtime=%s WHERE tid=%s',
            (total_files, scanned_files, now, tid)
        )
        execute('UPDATE project SET status=2,updatetime=%s WHERE pid=%s', (now, pid))
        _task_status[tid] = {'progress': 100, 'scanned': scanned_files, 'total': total_files}
    except Exception as e:
        execute('UPDATE scantask SET status=4 WHERE tid=%s', (tid,))
        execute('UPDATE project SET status=0 WHERE pid=%s', (pid,))
        _task_status[tid] = {'error': str(e)}


@scan_bp.route('/start', methods=['POST'])
def start_scan():
    """启动扫描任务"""
    data = request.get_json(force=True)
    pid    = data.get('pid')
    operuid = data.get('operuid')
    if not pid or not operuid:
        return fail('参数不完整')
    proj = query_one('SELECT * FROM project WHERE pid=%s', (pid,))
    if not proj:
        return fail('项目不存在', 404)
    if proj['status'] == 1:
        return fail('项目正在扫描中')
    tid = execute_lastid(
        'INSERT INTO scantask(pid,operuid,status,progress,totalfiles,scannedfiles) VALUES(%s,%s,0,0,0,0)',
        (pid, operuid)
    )
    _task_status[tid] = {'progress': 0, 'scanned': 0, 'total': 0}
    t = threading.Thread(target=_do_scan, args=(tid, pid, proj['sourcepath'], proj['language']), daemon=True)
    t.start()
    return ok({'tid': tid}, '扫描任务已启动')


@scan_bp.route('/pause', methods=['POST'])
def pause_scan():
    """暂停扫描（标记状态，线程自然结束后不再继续）"""
    data = request.get_json(force=True)
    tid = data.get('tid')
    pid = data.get('pid')
    if not tid:
        return fail('tid不能为空')
    execute('UPDATE scantask SET status=3 WHERE tid=%s AND status=1', (tid,))
    if pid:
        execute('UPDATE project SET status=3 WHERE pid=%s', (pid,))
    return ok(msg='扫描已暂停')


@scan_bp.route('/resume', methods=['POST'])
def resume_scan():
    """继续扫描（重新发起扫描任务）"""
    data = request.get_json(force=True)
    pid    = data.get('pid')
    operuid = data.get('operuid')
    if not pid or not operuid:
        return fail('参数不完整')
    proj = query_one('SELECT * FROM project WHERE pid=%s', (pid,))
    if not proj:
        return fail('项目不存在', 404)
    tid = execute_lastid(
        'INSERT INTO scantask(pid,operuid,status,progress,totalfiles,scannedfiles) VALUES(%s,%s,0,0,0,0)',
        (pid, operuid)
    )
    _task_status[tid] = {'progress': 0, 'scanned': 0, 'total': 0}
    t = threading.Thread(target=_do_scan, args=(tid, pid, proj['sourcepath'], proj['language']), daemon=True)
    t.start()
    return ok({'tid': tid}, '扫描任务已重新启动')


@scan_bp.route('/progress', methods=['GET'])
def get_progress():
    """查询扫描进度"""
    tid = request.args.get('tid')
    if not tid:
        return fail('tid不能为空')
    row = query_one(
        'SELECT tid,pid,status,progress,totalfiles,scannedfiles,starttime,endtime FROM scantask WHERE tid=%s',
        (tid,)
    )
    if not row:
        return fail('任务不存在', 404)
    # 合并内存缓存实时进度
    mem = _task_status.get(int(tid), {})
    if mem:
        row['progress'] = mem.get('progress', row['progress'])
    return ok(row)


@scan_bp.route('/list', methods=['GET'])
def list_tasks():
    """获取扫描任务列表"""
    pid  = request.args.get('pid')
    uid  = request.args.get('uid')
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    offset = (page - 1) * size
    wheres, args = [], []
    if pid:
        wheres.append('t.pid=%s'); args.append(pid)
    if uid:
        wheres.append('t.operuid=%s'); args.append(uid)
    where_sql = ('WHERE ' + ' AND '.join(wheres)) if wheres else ''
    rows = query_all(
        f'SELECT t.*,p.pname,u.realname AS opername FROM scantask t '
        f'LEFT JOIN project p ON p.pid=t.pid '
        f'LEFT JOIN userinfo u ON u.uid=t.operuid '
        f'{where_sql} ORDER BY t.tid DESC LIMIT %s OFFSET %s',
        args + [size, offset]
    )
    total = query_one(f'SELECT COUNT(*) AS cnt FROM scantask t {where_sql}', args or None)['cnt']
    return ok({'list': rows, 'total': total})


@scan_bp.route('/upload', methods=['POST'])
def upload_source():
    """上传源码并解压到项目目录，支持 zip / tar.gz / tar / rar / 单个源码文件"""
    pid  = request.form.get('pid')
    file = request.files.get('file')
    if not pid or not file:
        return fail('参数不完整')
    proj = query_one('SELECT sourcepath FROM project WHERE pid=%s', (pid,))
    if not proj:
        return fail('项目不存在', 404)
    savepath = proj['sourcepath']
    os.makedirs(savepath, exist_ok=True)

    filename = file.filename or ''
    name_lower = filename.lower()
    tmppath = os.path.join(savepath, filename)
    file.save(tmppath)

    try:
        if name_lower.endswith('.zip'):
            with zipfile.ZipFile(tmppath, 'r') as zf:
                zf.extractall(savepath)
            os.remove(tmppath)
        elif name_lower.endswith(('.tar.gz', '.tgz', '.tar.bz2', '.tar')):
            with tarfile.open(tmppath, 'r:*') as tf:
                tf.extractall(savepath)
            os.remove(tmppath)
        elif name_lower.endswith('.rar'):
            try:
                import rarfile
                with rarfile.RarFile(tmppath, 'r') as rf:
                    rf.extractall(savepath)
                os.remove(tmppath)
            except ImportError:
                return fail('服务端未安装 rarfile 库，请上传 ZIP 或 TAR.GZ 格式')
            except Exception as e:
                return fail(f'RAR 解压失败：{str(e)}')
        else:
            # 单个源码文件，直接保留在项目目录下即可
            pass
    except Exception as e:
        return fail(f'处理失败：{str(e)}')
    return ok(msg='源码上传成功')

