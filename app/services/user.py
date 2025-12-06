from werkzeug.security import check_password_hash
from utils.config import *


class User:
    def __init__(self):
        # 初始化数据库连接
        from app import db_proxy
        self.db_proxy = db_proxy

    def validate(self, username: str, password: str):
        """
        登录验证
        :param username: 用户名
        :param password: 明文密码
        :return: (bool, dict/str) - True 和用户信息 或 False 和错误信息
        """
        sql = "SELECT id, name, passwd, role, avatar_path, points FROM tbl_users WHERE name=%s"
        row = self.db_proxy.run_sql_select(sql, params=(username,), fetch_one=True)
        if not row:
            return False, "User not found"
        
        # hashed_pw = generate_password_hash(password)  # 存入数据库

        # 验证密码
        if not check_password_hash(row['passwd'], password):
            return False, "Incorrect password"

        return True, row

    def validate_user(self, ip_address):
        sql = "SELECT id, ip_address, attempts FROM tbl_ip WHERE ip_address=%s"
        row = self.db_proxy.run_sql_select(sql, params=(ip_address,), fetch_one=True)
        if not row:
            return True
        
        if row['attempts'] >= IP_BLOCK_TIMES:
            return False
        return True
    
    def fail_attempt(self, ip_address):
        sql = "SELECT id, ip_address, attempts FROM tbl_ip WHERE ip_address=%s"
        row = self.db_proxy.run_sql_select(sql, params=(ip_address,), fetch_one=True)
        if not row:
            sql = "INSERT INTO tbl_ip (`ip_address`, `attempts`) VALUES (%s, 1)"
            self.db_proxy.run_sql_update(sql, params=(ip_address,))
            return 9
        failed_time = row['attempts']
        sql = "UPDATE tbl_ip SET attempts = %s WHERE id=%s"
        self.db_proxy.run_sql_update(sql, params=(row['attempts'] + 1, row['id'],))
        return 9 - failed_time
    