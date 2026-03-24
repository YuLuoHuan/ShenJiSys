# -*- coding: utf-8 -*-
"""
Python AST分析器实现
基于Python内置ast模块，检测Python代码中的安全漏洞
"""
import ast
import inspect
from typing import Any, List, Dict, Optional, Set
from .ast_analyzer import ASTAnalyzer, ASTPattern, ASTVisitor, ASTPosition, DetectionResult


class PythonASTAnalyzer(ASTAnalyzer):
    """Python AST分析器"""

    def __init__(self):
        super().__init__('python')
        self._init_patterns()

    def parse_file(self, filepath: str) -> Optional[ast.AST]:
        """解析Python文件为AST"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return ast.parse(content, filename=filepath)
        except Exception:
            return None

    def traverse_ast(self, ast_node: ast.AST, visitor: ASTVisitor) -> None:
        """遍历Python AST树"""
        for node in ast.walk(ast_node):
            visitor.visit_node(node)

    def match_pattern(self, ast_node: ast.AST, pattern: ASTPattern) -> List[Dict]:
        """
        匹配Python漏洞模式
        :param ast_node: AST根节点
        :param pattern: 漏洞模式
        :return: 检测结果列表
        """
        pattern_type = pattern.pattern_data.get('type', '')
        pattern_name = pattern.name

        # 根据模式类型调用不同的检测方法
        if pattern_type == 'sql_injection':
            return self._detect_sql_injection(ast_node, pattern)
        elif pattern_type == 'command_injection':
            return self._detect_command_injection(ast_node, pattern)
        elif pattern_type == 'eval_injection':
            return self._detect_eval_injection(ast_node, pattern)
        elif pattern_type == 'path_traversal':
            return self._detect_path_traversal(ast_node, pattern)
        elif pattern_type == 'hardcoded_password':
            return self._detect_hardcoded_password(ast_node, pattern)
        else:
            # 通用模式匹配
            return self._generic_pattern_match(ast_node, pattern)

    def _detect_sql_injection(self, ast_node: ast.AST, pattern: ASTPattern) -> List[Dict]:
        """检测SQL注入漏洞"""
        results = []
        visitor = SQLInjectionVisitor(pattern)
        self.traverse_ast(ast_node, visitor)
        return visitor.get_results()

    def _detect_command_injection(self, ast_node: ast.AST, pattern: ASTPattern) -> List[Dict]:
        """检测命令注入漏洞"""
        results = []
        visitor = CommandInjectionVisitor(pattern)
        self.traverse_ast(ast_node, visitor)
        return visitor.get_results()

    def _detect_eval_injection(self, ast_node: ast.AST, pattern: ASTPattern) -> List[Dict]:
        """检测eval代码执行漏洞"""
        results = []
        visitor = EvalInjectionVisitor(pattern)
        self.traverse_ast(ast_node, visitor)
        return visitor.get_results()

    def _detect_path_traversal(self, ast_node: ast.AST, pattern: ASTPattern) -> List[Dict]:
        """检测路径穿越漏洞"""
        results = []
        visitor = PathTraversalVisitor(pattern)
        self.traverse_ast(ast_node, visitor)
        return visitor.get_results()

    def _detect_hardcoded_password(self, ast_node: ast.AST, pattern: ASTPattern) -> List[Dict]:
        """检测硬编码密码"""
        results = []
        visitor = HardcodedPasswordVisitor(pattern)
        self.traverse_ast(ast_node, visitor)
        return visitor.get_results()

    def _generic_pattern_match(self, ast_node: ast.AST, pattern: ASTPattern) -> List[Dict]:
        """通用模式匹配"""
        # 这里可以实现通用的AST模式匹配逻辑
        return []

    def _init_patterns(self):
        """初始化内置Python漏洞模式"""
        patterns = [
            ASTPattern(
                pattern_id=101,
                name='Python SQL注入检测',
                description='检测Python中字符串拼接的SQL查询',
                severity=3,
                language='python',
                pattern_data={
                    'type': 'sql_injection',
                    'dangerous_functions': ['execute', 'executemany', 'executequery'],
                    'dangerous_modules': ['sqlite3', 'mysql', 'psycopg2', 'pymysql']
                }
            ),
            ASTPattern(
                pattern_id=102,
                name='Python命令注入检测',
                description='检测os.system、subprocess.call等命令执行函数',
                severity=4,
                language='python',
                pattern_data={
                    'type': 'command_injection',
                    'dangerous_functions': [
                        'os.system', 'os.popen', 'subprocess.call',
                        'subprocess.Popen', 'subprocess.run'
                    ]
                }
            ),
            ASTPattern(
                pattern_id=103,
                name='Python eval/exec代码执行检测',
                description='检测eval、exec等动态代码执行',
                severity=4,
                language='python',
                pattern_data={
                    'type': 'eval_injection',
                    'dangerous_functions': ['eval', 'exec', 'compile']
                }
            ),
            ASTPattern(
                pattern_id=104,
                name='Python路径穿越检测',
                description='检测文件操作中的路径穿越风险',
                severity=3,
                language='python',
                pattern_data={
                    'type': 'path_traversal',
                    'dangerous_functions': [
                        'open', 'os.open', 'os.remove', 'os.rename',
                        'shutil.copy', 'shutil.move'
                    ]
                }
            ),
            ASTPattern(
                pattern_id=105,
                name='Python硬编码密码检测',
                description='检测代码中的硬编码密码和密钥',
                severity=2,
                language='python',
                pattern_data={
                    'type': 'hardcoded_password',
                    'keywords': ['password', 'passwd', 'secret', 'key', 'token'],
                    'patterns': [
                        r'password\s*=\s*["\'][^"\']{6,}["\']',
                        r'PASSWORD\s*:\s*["\'][^"\']{6,}["\']',
                        r'SECRET_KEY\s*=\s*["\'][^"\']{10,}["\']',
                        r'api_key\s*=\s*["\'][^"\']{10,}["\']'
                    ]
                }
            )
        ]

        for pattern in patterns:
            self.add_pattern(pattern)


class SQLInjectionVisitor(ASTVisitor):
    """SQL注入检测访问者"""

    def __init__(self, pattern: ASTPattern):
        self.pattern = pattern
        self.results = []
        self.dangerous_funcs = set(pattern.pattern_data.get('dangerous_functions', []))
        self.dangerous_modules = set(pattern.pattern_data.get('dangerous_modules', []))

    def visit_node(self, node: Any) -> None:
        """访问AST节点，检测SQL注入"""
        # 检测函数调用
        if isinstance(node, ast.Call):
            func_name = self._get_function_name(node.func)
            if func_name in self.dangerous_funcs:
                # 检查参数中是否有字符串拼接
                if self._has_string_concatenation(node):
                    position = ASTPosition(
                        lineno=node.lineno,
                        col_offset=node.col_offset,
                        end_lineno=getattr(node, 'end_lineno', None),
                        end_col_offset=getattr(node, 'end_col_offset', None)
                    )
                    code_snippet = ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
                    evidence = f"函数 {func_name} 使用字符串拼接构建SQL查询"

                    result = DetectionResult(
                        pattern_id=self.pattern.pattern_id,
                        position=position,
                        code_snippet=code_snippet[:500],
                        evidence=evidence
                    )
                    self.results.append(result.to_dict())

    def _get_function_name(self, func_node: ast.AST) -> str:
        """获取函数名"""
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            return func_node.attr
        elif isinstance(func_node, ast.Call):
            return self._get_function_name(func_node.func)
        return ''

    def _has_string_concatenation(self, call_node: ast.Call) -> bool:
        """检查函数调用参数中是否有字符串拼接"""
        for arg in call_node.args:
            if self._is_string_concatenation(arg):
                return True
        return False

    def _is_string_concatenation(self, node: ast.AST) -> bool:
        """检查节点是否为字符串拼接"""
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Add):
                # 检查左操作数或右操作数是否为字符串
                left_is_str = self._is_string_literal(node.left)
                right_is_str = self._is_string_literal(node.right)
                if left_is_str or right_is_str:
                    return True
                # 递归检查子节点
                return (self._is_string_concatenation(node.left) or
                        self._is_string_concatenation(node.right))
        elif isinstance(node, ast.JoinedStr):  # f-string
            return True
        elif isinstance(node, ast.Call):
            # 检查是否为format()调用
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == 'format':
                    return True
        return False

    def _is_string_literal(self, node: ast.AST) -> bool:
        """检查节点是否为字符串字面量"""
        return isinstance(node, ast.Constant) and isinstance(node.value, str)

    def get_results(self) -> List[Dict]:
        """获取检测结果"""
        return self.results


class CommandInjectionVisitor(ASTVisitor):
    """命令注入检测访问者"""

    def __init__(self, pattern: ASTPattern):
        self.pattern = pattern
        self.results = []
        self.dangerous_funcs = set(pattern.pattern_data.get('dangerous_functions', []))

    def visit_node(self, node: Any) -> None:
        """访问AST节点，检测命令注入"""
        if isinstance(node, ast.Call):
            func_name = self._get_full_function_name(node.func)

            # 检查是否为危险函数
            is_dangerous = any(func_name.endswith(dangerous)
                              for dangerous in self.dangerous_funcs)

            if is_dangerous:
                # 检查参数中是否有用户输入（变量或函数调用）
                has_user_input = self._has_user_input(node)

                if has_user_input:
                    position = ASTPosition(
                        lineno=node.lineno,
                        col_offset=node.col_offset,
                        end_lineno=getattr(node, 'end_lineno', None),
                        end_col_offset=getattr(node, 'end_col_offset', None)
                    )
                    code_snippet = ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
                    evidence = f"危险函数 {func_name} 接受用户输入作为参数"

                    result = DetectionResult(
                        pattern_id=self.pattern.pattern_id,
                        position=position,
                        code_snippet=code_snippet[:500],
                        evidence=evidence
                    )
                    self.results.append(result.to_dict())

    def _get_full_function_name(self, func_node: ast.AST) -> str:
        """获取完整函数名（包含模块）"""
        if isinstance(func_node, ast.Attribute):
            # 获取属性访问的完整路径，如os.system
            module = self._get_module_name(func_node.value)
            return f"{module}.{func_node.attr}" if module else func_node.attr
        elif isinstance(func_node, ast.Name):
            return func_node.id
        return ''

    def _get_module_name(self, node: ast.AST) -> str:
        """获取模块名"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_module_name(node.value)
        return ''

    def _has_user_input(self, call_node: ast.Call) -> bool:
        """检查函数调用参数中是否有用户输入"""
        for arg in call_node.args:
            if self._is_user_input(arg):
                return True
        return False

    def _is_user_input(self, node: ast.AST) -> bool:
        """检查节点是否可能包含用户输入"""
        # 变量名可能来自用户输入
        if isinstance(node, ast.Name):
            return True
        # 函数调用返回值可能来自用户输入
        elif isinstance(node, ast.Call):
            return True
        # 字符串格式化可能包含用户输入
        elif isinstance(node, ast.JoinedStr):  # f-string
            return True
        # 二元操作（如拼接）可能包含用户输入
        elif isinstance(node, ast.BinOp):
            return (self._is_user_input(node.left) or
                    self._is_user_input(node.right))
        # 列表、字典等容器
        elif isinstance(node, (ast.List, ast.Dict, ast.Tuple, ast.Set)):
            return any(self._is_user_input(el) for el in ast.iter_child_nodes(node))
        return False

    def get_results(self) -> List[Dict]:
        """获取检测结果"""
        return self.results


class EvalInjectionVisitor(ASTVisitor):
    """eval注入检测访问者"""

    def __init__(self, pattern: ASTPattern):
        self.pattern = pattern
        self.results = []
        self.dangerous_funcs = set(pattern.pattern_data.get('dangerous_functions', []))

    def visit_node(self, node: Any) -> None:
        """访问AST节点，检测eval注入"""
        if isinstance(node, ast.Call):
            func_name = self._get_function_name(node.func)

            if func_name in self.dangerous_funcs:
                # eval/exec总是危险的
                position = ASTPosition(
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                    end_lineno=getattr(node, 'end_lineno', None),
                    end_col_offset=getattr(node, 'end_col_offset', None)
                )
                code_snippet = ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
                evidence = f"危险函数 {func_name} 应避免使用，或严格验证输入"

                result = DetectionResult(
                    pattern_id=self.pattern.pattern_id,
                    position=position,
                    code_snippet=code_snippet[:500],
                    evidence=evidence
                )
                self.results.append(result.to_dict())

    def _get_function_name(self, func_node: ast.AST) -> str:
        """获取函数名"""
        if isinstance(func_node, ast.Name):
            return func_node.id
        return ''

    def get_results(self) -> List[Dict]:
        """获取检测结果"""
        return self.results


class PathTraversalVisitor(ASTVisitor):
    """路径穿越检测访问者"""

    def __init__(self, pattern: ASTPattern):
        self.pattern = pattern
        self.results = []
        self.dangerous_funcs = set(pattern.pattern_data.get('dangerous_functions', []))

    def visit_node(self, node: Any) -> None:
        """访问AST节点，检测路径穿越"""
        if isinstance(node, ast.Call):
            func_name = self._get_full_function_name(node.func)

            # 检查是否为危险的文件操作函数
            is_dangerous = any(func_name.endswith(dangerous)
                              for dangerous in self.dangerous_funcs)

            if is_dangerous:
                # 检查第一个参数是否包含路径穿越模式
                if node.args:
                    first_arg = node.args[0]
                    if self._contains_path_traversal(first_arg):
                        position = ASTPosition(
                            lineno=node.lineno,
                            col_offset=node.col_offset,
                            end_lineno=getattr(node, 'end_lineno', None),
                            end_col_offset=getattr(node, 'end_col_offset', None)
                        )
                        code_snippet = ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
                        evidence = f"文件操作函数 {func_name} 参数包含路径穿越风险"

                        result = DetectionResult(
                            pattern_id=self.pattern.pattern_id,
                            position=position,
                            code_snippet=code_snippet[:500],
                            evidence=evidence
                        )
                        self.results.append(result.to_dict())

    def _get_full_function_name(self, func_node: ast.AST) -> str:
        """获取完整函数名"""
        if isinstance(func_node, ast.Attribute):
            module = self._get_module_name(func_node.value)
            return f"{module}.{func_node.attr}" if module else func_node.attr
        elif isinstance(func_node, ast.Name):
            return func_node.id
        return ''

    def _get_module_name(self, node: ast.AST) -> str:
        """获取模块名"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_module_name(node.value)
        return ''

    def _contains_path_traversal(self, node: ast.AST) -> bool:
        """检查节点是否包含路径穿越模式"""
        # 获取节点的字符串表示
        code = ast.unparse(node) if hasattr(ast, 'unparse') else str(node)

        # 检查常见的路径穿越模式
        patterns = [
            '../', '..\\', '/../', '\\..\\',
            '~/', '~\\',  # 用户目录
            '//', '\\\\'  # 网络路径
        ]

        for pattern in patterns:
            if pattern in code:
                return True

        # 检查变量拼接
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return (self._contains_path_traversal(node.left) or
                    self._contains_path_traversal(node.right))

        return False

    def get_results(self) -> List[Dict]:
        """获取检测结果"""
        return self.results


class HardcodedPasswordVisitor(ASTVisitor):
    """硬编码密码检测访问者"""

    def __init__(self, pattern: ASTPattern):
        self.pattern = pattern
        self.results = []
        self.keywords = set(kw.lower() for kw in pattern.pattern_data.get('keywords', []))

    def visit_node(self, node: Any) -> None:
        """访问AST节点，检测硬编码密码"""
        # 检查赋值语句
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    # 检查变量名是否包含密码关键词
                    var_name = target.id.lower()
                    if any(keyword in var_name for keyword in self.keywords):
                        # 检查赋值右侧是否为字符串常量
                        if self._is_string_constant(node.value):
                            # 检查字符串长度（可能为密码）
                            str_value = self._get_string_value(node.value)
                            if str_value and len(str_value) >= 6:
                                position = ASTPosition(
                                    lineno=node.lineno,
                                    col_offset=node.col_offset,
                                    end_lineno=getattr(node, 'end_lineno', None),
                                    end_col_offset=getattr(node, 'end_col_offset', None)
                                )
                                code_snippet = ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
                                evidence = f"变量 {target.id} 包含硬编码密码或密钥"

                                result = DetectionResult(
                                    pattern_id=self.pattern.pattern_id,
                                    position=position,
                                    code_snippet=code_snippet[:500],
                                    evidence=evidence
                                )
                                self.results.append(result.to_dict())

        # 检查字典键值对
        elif isinstance(node, ast.Dict):
            keys = node.keys
            values = node.values
            for key, value in zip(keys, values):
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    key_str = key.value.lower()
                    if any(keyword in key_str for keyword in self.keywords):
                        if self._is_string_constant(value):
                            str_value = self._get_string_value(value)
                            if str_value and len(str_value) >= 6:
                                position = ASTPosition(
                                    lineno=node.lineno,
                                    col_offset=node.col_offset,
                                    end_lineno=getattr(node, 'end_lineno', None),
                                    end_col_offset=getattr(node, 'end_col_offset', None)
                                )
                                code_snippet = ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
                                evidence = f"字典键 {key.value} 包含硬编码密码或密钥"

                                result = DetectionResult(
                                    pattern_id=self.pattern.pattern_id,
                                    position=position,
                                    code_snippet=code_snippet[:500],
                                    evidence=evidence
                                )
                                self.results.append(result.to_dict())

    def _is_string_constant(self, node: ast.AST) -> bool:
        """检查节点是否为字符串常量"""
        return isinstance(node, ast.Constant) and isinstance(node.value, str)

    def _get_string_value(self, node: ast.AST) -> Optional[str]:
        """获取字符串值"""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    def get_results(self) -> List[Dict]:
        """获取检测结果"""
        return self.results