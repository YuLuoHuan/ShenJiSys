# -*- coding: utf-8 -*-
"""
代码扫描引擎：支持正则规则匹配和AST分析
"""
import os
import re

# AST分析器导入
try:
    from .python_ast import PythonASTAnalyzer
    AST_SUPPORT = True
except ImportError:
    AST_SUPPORT = False
    PythonASTAnalyzer = None


def _get_ast_analyzer(language: str):
    """
    根据语言获取AST分析器
    :param language: 语言标识
    :return: AST分析器实例或None
    """
    if not AST_SUPPORT:
        return None

    # 目前只支持Python
    if language == 'python':
        return PythonASTAnalyzer()

    # 未来可以添加其他语言的AST分析器
    # elif language == 'java':
    #     from .java_ast import JavaASTAnalyzer
    #     return JavaASTAnalyzer()

    return None

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


def _split_rules_by_type(rules: list) -> tuple:
    """
    将规则按类型分开
    :param rules: 规则列表
    :return: (regex_rules, ast_rules)
    """
    regex_rules = []
    ast_rules = []
    for rule in rules:
        # 规则类型：1=正则，2=AST
        rule_type = rule.get('rule_type', 1)
        if rule_type == 2 and AST_SUPPORT:
            ast_rules.append(rule)
        else:
            regex_rules.append(rule)
    return regex_rules, ast_rules


def scan_file_with_ast(filepath: str, ast_rules: list, language: str) -> list:
    """
    使用AST分析器扫描单个文件
    :param filepath: 文件绝对路径
    :param ast_rules: AST规则列表
    :param language: 文件语言
    :return: 命中漏洞列表 [{rid, filepath, lineno, codesnip, severity}, ...]
    """
    hits = []

    if not ast_rules or not AST_SUPPORT:
        return hits

    analyzer = _get_ast_analyzer(language)
    if not analyzer:
        return hits

    try:
        # 目前使用分析器内置模式
        ast_results = analyzer.scan_file(filepath)

        # 将AST结果转换为统一格式
        for result in ast_results:
            # AST结果中的pattern_id对应内置模式的ID
            pattern_id = result.get('pattern_id', 0)

            # 查找对应的数据库规则
            matched_rule = None
            for rule in ast_rules:
                if rule.get('rid') == pattern_id:
                    matched_rule = rule
                    break

            if matched_rule:
                hits.append({
                    'rid': matched_rule['rid'],
                    'filepath': filepath,
                    'lineno': result.get('lineno', 1),
                    'codesnip': result.get('code_snippet', '')[:500],
                    'severity': matched_rule['severity'],
                })
    except Exception as e:
        # 忽略AST分析错误，继续扫描
        print(f"AST扫描错误 {filepath}: {e}")

    return hits


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

    # 分离正则规则和AST规则
    regex_rules, ast_rules = _split_rules_by_type(rules)

    for idx, fpath in enumerate(files, start=1):
        # 正则规则扫描
        if regex_rules:
            regex_hits = scan_file(fpath, regex_rules)
            all_hits.extend(regex_hits)

        # AST规则扫描
        if ast_rules:
            ast_hits = scan_file_with_ast(fpath, ast_rules, language)
            all_hits.extend(ast_hits)

        if progress_callback:
            progress_callback(idx, total)

    return all_hits, total, total

