# -*- coding: utf-8 -*-
"""
抽象语法树（AST）分析引擎基类
提供AST解析、遍历和漏洞模式匹配的基础框架
"""
import ast
import os
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple


class ASTPattern:
    """AST漏洞模式定义"""

    def __init__(self, pattern_id: int, name: str, description: str,
                 severity: int, language: str, pattern_data: Dict):
        """
        初始化漏洞模式
        :param pattern_id: 模式ID
        :param name: 模式名称
        :param description: 模式描述
        :param severity: 严重等级（1-4）
        :param language: 适用语言
        :param pattern_data: 模式数据（语言相关）
        """
        self.pattern_id = pattern_id
        self.name = name
        self.description = description
        self.severity = severity
        self.language = language
        self.pattern_data = pattern_data

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'pattern_id': self.pattern_id,
            'name': self.name,
            'description': self.description,
            'severity': self.severity,
            'language': self.language
        }


class ASTAnalyzer(ABC):
    """AST分析器抽象基类"""

    def __init__(self, language: str):
        self.language = language
        self.patterns: List[ASTPattern] = []

    @abstractmethod
    def parse_file(self, filepath: str) -> Optional[Any]:
        """
        解析源代码文件为AST
        :param filepath: 文件路径
        :return: AST根节点（语言相关类型）
        """
        pass

    @abstractmethod
    def traverse_ast(self, ast_node: Any, visitor: 'ASTVisitor') -> None:
        """
        遍历AST树
        :param ast_node: AST根节点
        :param visitor: 访问者对象
        """
        pass

    @abstractmethod
    def match_pattern(self, ast_node: Any, pattern: ASTPattern) -> List[Dict]:
        """
        匹配单个漏洞模式
        :param ast_node: AST根节点
        :param pattern: 漏洞模式
        :return: 匹配结果列表 [{位置信息, 代码片段, 证据}, ...]
        """
        pass

    def scan_file(self, filepath: str) -> List[Dict]:
        """
        扫描单个文件的所有漏洞模式
        :param filepath: 文件路径
        :return: 漏洞检测结果列表
        """
        results = []

        try:
            # 解析文件为AST
            ast_root = self.parse_file(filepath)
            if ast_root is None:
                return results

            # 遍历所有模式进行匹配
            for pattern in self.patterns:
                if pattern.language == self.language or pattern.language == 'all':
                    matches = self.match_pattern(ast_root, pattern)
                    for match in matches:
                        match.update(pattern.to_dict())
                        match['filepath'] = filepath
                        results.append(match)

        except Exception as e:
            # 记录错误但继续扫描其他文件
            print(f"AST分析错误 {filepath}: {e}")

        return results

    def add_pattern(self, pattern: ASTPattern) -> None:
        """添加漏洞模式"""
        self.patterns.append(pattern)

    def load_patterns_from_json(self, json_path: str) -> None:
        """从JSON文件加载漏洞模式"""
        if not os.path.exists(json_path):
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data.get('patterns', []):
            pattern = ASTPattern(
                pattern_id=item.get('id', 0),
                name=item.get('name', ''),
                description=item.get('description', ''),
                severity=item.get('severity', 2),
                language=item.get('language', 'all'),
                pattern_data=item.get('pattern_data', {})
            )
            self.add_pattern(pattern)


class ASTVisitor(ABC):
    """AST访问者模式基类"""

    @abstractmethod
    def visit_node(self, node: Any) -> None:
        """访问AST节点"""
        pass


class ASTPosition:
    """AST节点位置信息"""

    def __init__(self, lineno: int, col_offset: int = 0, end_lineno: int = None,
                 end_col_offset: int = None):
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'lineno': self.lineno,
            'col_offset': self.col_offset,
            'end_lineno': self.end_lineno,
            'end_col_offset': self.end_col_offset
        }


class DetectionResult:
    """检测结果"""

    def __init__(self, pattern_id: int, position: ASTPosition,
                 code_snippet: str, evidence: str = ''):
        self.pattern_id = pattern_id
        self.position = position
        self.code_snippet = code_snippet
        self.evidence = evidence

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        result = {
            'pattern_id': self.pattern_id,
            'lineno': self.position.lineno,
            'col_offset': self.position.col_offset,
            'code_snippet': self.code_snippet,
            'evidence': self.evidence
        }
        if self.position.end_lineno:
            result['end_lineno'] = self.position.end_lineno
        if self.position.end_col_offset:
            result['end_col_offset'] = self.position.end_col_offset
        return result