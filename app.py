# -*- coding: utf-8 -*-
"""
代码审计系统 - Flask 主入口
运行方式：python app.py
"""
import os
# 强制将工作目录切换到 app.py 所在目录，保证 uploads/ 相对路径始终可用
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from backend.routes.auth import auth_bp
from backend.routes.user import user_bp
from backend.routes.project import project_bp
from backend.routes.rule import rule_bp
from backend.routes.scan import scan_bp
from backend.routes.vuln import vuln_bp
from backend.routes.report import report_bp
from backend.routes.system import system_bp

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 最大上传50MB

# 注册蓝图
app.register_blueprint(auth_bp,    url_prefix='/api/auth')
app.register_blueprint(user_bp,    url_prefix='/api/user')
app.register_blueprint(project_bp, url_prefix='/api/project')
app.register_blueprint(rule_bp,    url_prefix='/api/rule')
app.register_blueprint(scan_bp,    url_prefix='/api/scan')
app.register_blueprint(vuln_bp,    url_prefix='/api/vuln')
app.register_blueprint(report_bp,  url_prefix='/api/report')
app.register_blueprint(system_bp,  url_prefix='/api/system')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

