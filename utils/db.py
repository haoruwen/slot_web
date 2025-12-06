from utils.config import *
from utils.utils import print_info

import pymysql
pymysql.install_as_MySQLdb()
import time


class DBProxy(object):
    # "Can't connect to MySQL server on '127.0.0.1'"
    ERROR_CODE_CANNOT_CONNECT_SERVER = 2003
    
    # "MySQL connection has gone away"
    ERROR_CODE_CONNECTION_LOST = 2006

    # "MySQL was disconnected by the server"
    ERROR_CODE_SERVER_DISCONNECTED = 4031

    # "Incorrect string value: '\\xF0\\x9F\\x95\\xB5\\xEF\\xB8...' for column 'advisory' at row 1"
    ERROR_CODE_INCORRECT_STRING_VALUE = 1366

    def __init__(self, use_dict_cursor=True):
        self.use_dict_cursor = use_dict_cursor
        self._create_db_connection()

    def __del__(self):
        try:
            self.connection.close()
        except:
            # db connection already lost
            pass

    def recreate_connection(self):
        try:
            del self.connection
        except:
            pass
        self._create_db_connection()

    def _create_db_connection(self):
        conn = None
        while True:
            try:
                conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, charset='utf8mb4')
                break
            except Exception as e:
                print_info(str(e) + '\n[*]Retrying to create db connection ...')
                time.sleep(3)

        self.connection = conn
        if self.use_dict_cursor:
            self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        else:
            self.cursor = self.connection.cursor(pymysql.cursors.Cursor)

    def _run_sql(self, sql, params=None):
        """
        执行 SQL 语句，可带参数
        """
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
        except pymysql.OperationalError as e:
            if e.args[0] in (self.ERROR_CODE_CONNECTION_LOST, self.ERROR_CODE_SERVER_DISCONNECTED):
                self._create_db_connection()
                if params:
                    self.cursor.execute(sql, params)
                else:
                    self.cursor.execute(sql)
            elif e.args[0] == self.ERROR_CODE_INCORRECT_STRING_VALUE:
                print_info(str(e))
                print_info(sql)
                raise

    def run_sql_select(self, sql, params=None, fetch_one=False):
        """
        执行 SELECT 语句，可带参数
        :param sql: SQL 语句
        :param params: tuple 或 list 参数
        :param fetch_one: 是否只取一条
        """
        self._run_sql(sql, params)
        if fetch_one:
            return self.cursor.fetchone()
        return self.cursor.fetchall()


    def run_sql_update(self, sql, params=None):
        """
        run one of following statements: INSERT, UPDATE, DELETE
        """
        self._run_sql(sql, params)
        self.connection.commit()
