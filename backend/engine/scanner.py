# -*- coding: utf-8 -*-
"""
代码扫描引擎：真实正则规则匹配，遍历目录中所有源码文件
"""
import os
import re

# 项目根目录绝对路径（code/），用于将相对路径转为绝对路径
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 各语言对应的文件后缀映射
LANG_EXT = {
    'python': ['.py'],
    'java':   ['.java'],
    'php':    ['.php'],
    'js':     ['.js', '.ts', '.jsx', '.tsx'],
    'all':    ['.py', '.java', '.php', '.js', '.ts', '.jsx', '.tsx'],
}


def get_scannable_files(sourcepath: str, language: str) -> list:
    """
    遍历源码目录，返回所有符合语言后缀的文件路径列表
    :param sourcepath: 项目源码根目录（相对路径或绝对路径均可）
    :param language:   项目语言标识
    :return: 文件路径列表
    """
    exts = LANG_EXT.get(language, ['.py', '.java', '.php', '.js'])
    all_exts = set(exts)
    file_list = []
    # 若是相对路径，转为基于项目根目录的绝对路径
    if not os.path.isabs(sourcepath):
        sourcepath = os.path.join(_BASE_DIR, sourcepath)
    if not os.path.isdir(sourcepath):
        return file_list
    for root, dirs, files in os.walk(sourcepath):
        # 跳过常见无关目录
        dirs[:] = [d for d in dirs if d not in ('__pycache__', 'node_modules', '.git', 'venv')]
        for f in files:
            _, ext = os.path.splitext(f)
            if ext.lower() in all_exts:
                file_list.append(os.path.join(root, f))
    return file_list


def scan_file(filepath: str, rules: list) -> list:
    """
    对单个文件执行所有规则的正则匹配
    :param filepath: 文件绝对路径
    :param rules:    启用的规则列表（来自数据库）
    :return: 命中漏洞列表 [{rid, filepath, lineno, codesnip, severity}, ...]
    """
    hits = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as fh:
            lines = fh.readlines()
    except Exception:
        return hits

    for rule in rules:
        try:
            pattern = re.compile(rule['pattern'], re.IGNORECASE)
        except re.error:
            continue
        for lineno, line in enumerate(lines, start=1):
            if pattern.search(line):
                hits.append({
                    'rid':      rule['rid'],
                    'filepath': filepath,
                    'lineno':   lineno,
                    'codesnip': line.rstrip('\n')[:500],   # 最多截取500字符
                    'severity': rule['severity'],
                })
    return hits


def run_scan(sourcepath: str, language: str, rules: list,
             progress_callback=None) -> tuple:
    """
    执行完整扫描
    :param sourcepath:         项目源码路径
    :param language:           项目语言
    :param rules:              启用的规则列表
    :param progress_callback:  进度回调 fn(scanned, total)
    :return: (all_hits, total_files, scanned_files)
    """
    files = get_scannable_files(sourcepath, language)
    total = len(files)
    all_hits = []
    for idx, fpath in enumerate(files, start=1):
        hits = scan_file(fpath, rules)
        all_hits.extend(hits)
        if progress_callback:
            progress_callback(idx, total)
    return all_hits, total, total

