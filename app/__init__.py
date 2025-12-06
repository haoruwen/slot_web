from flask import Flask
from .routes import main_bp, user_bp
from utils.db import DBProxy

db_proxy = DBProxy() 

def create_app():
    app = Flask(__name__)
    app.secret_key = 'a8f4b0d12c7e48fbbd93a1ce920dcfa3'
    app.register_blueprint(main_bp)  # 注册页面蓝图
    app.register_blueprint(user_bp)
    return app
