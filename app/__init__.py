from flask import Flask, request
from .routes import main_bp, user_bp
from utils.db import DBProxy
from datetime import datetime, timedelta
import os
import hashlib

db_proxy = DBProxy() 

def create_app():
    app = Flask(__name__)
    app.secret_key = 'a8f4b0d12c7e48fbbd93a1ce920dcfa3'
    app.register_blueprint(main_bp)  # 注册页面蓝图
    app.register_blueprint(user_bp)
    
    # 添加静态文件缓存支持（支持文件更新检测）
    @app.after_request
    def add_cache_headers(response):
        # 检查是否是静态文件请求
        if request.endpoint == 'static' or request.path.startswith('/static/'):
            # 获取静态文件的完整路径
            static_path = request.path.lstrip('/')
            file_path = os.path.join(app.root_path, static_path)
            
            # 检查文件是否存在
            if os.path.exists(file_path) and os.path.isfile(file_path):
                # 获取文件修改时间和大小，用于生成ETag
                stat_info = os.stat(file_path)
                file_mtime = stat_info.st_mtime
                file_size = stat_info.st_size
                
                # 生成基于文件修改时间和大小的ETag
                etag_str = f"{file_path}:{file_mtime}:{file_size}"
                etag = hashlib.md5(etag_str.encode()).hexdigest()
                
                # 设置ETag
                response.headers['ETag'] = f'"{etag}"'
                
                # 设置Last-Modified头
                file_time = datetime.fromtimestamp(file_mtime)
                response.headers['Last-Modified'] = file_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
                
                # 检查客户端是否发送了If-None-Match或If-Modified-Since
                if_none_match = request.headers.get('If-None-Match')
                if_modified_since = request.headers.get('If-Modified-Since')
                
                # 如果文件未修改，返回304 Not Modified
                if if_none_match and f'"{etag}"' in if_none_match:
                    response.status_code = 304
                    return response
                
                if if_modified_since:
                    try:
                        client_time = datetime.strptime(if_modified_since, '%a, %d %b %Y %H:%M:%S GMT')
                        if file_time <= client_time:
                            response.status_code = 304
                            return response
                    except:
                        pass
                
                # 图片文件（png, jpg, jpeg, gif, webp, svg等）
                if any(request.path.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico']):
                    # 设置缓存策略：浏览器缓存7天，但会检查更新
                    response.headers['Cache-Control'] = 'public, max-age=604800, must-revalidate'  # 7天 = 604800秒
                # CSS和JS文件
                elif any(request.path.lower().endswith(ext) for ext in ['.css', '.js']):
                    # 设置缓存为1周，支持更新检测
                    response.headers['Cache-Control'] = 'public, max-age=604800, must-revalidate'
        
        return response
    
    return app
