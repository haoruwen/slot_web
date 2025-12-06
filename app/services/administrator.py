from datetime import datetime
from zoneinfo import ZoneInfo
from utils.utils import time_to_string

class Administrator:
    def __init__(self):
        # 初始化数据库连接
        from app import db_proxy
        self.db_proxy = db_proxy
    
    def get_all_users(self):
        sql = "SELECT id, name, points, update_time FROM tbl_users WHERE role='user'"
        rows = self.db_proxy.run_sql_select(sql)
        return rows

    def update_user_points(self, user_id, user_points):
        pacific_time = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d %H:%M:%S")
        sql = "UPDATE tbl_users SET points = %s, update_time = %s WHERE id=%s"
        self.db_proxy.run_sql_update(sql, params=(user_points, pacific_time, user_id,))
    
    def get_all_records(self):
        sql = "SELECT r.id, r.from_id,fu.name AS from_name,r.to_id,tu.name AS to_name,r.prize_id,p.name AS prize_name,r.tier,r.create_time FROM tbl_records r JOIN tbl_users fu ON r.from_id = fu.id JOIN tbl_users tu ON r.to_id = tu.id JOIN tbl_prize p ON r.prize_id = p.id ORDER BY r.create_time DESC"
        rows = self.db_proxy.run_sql_select(sql)
        records = []
        for row in rows:
            record = "%s drew a %s-tier %s for %s at %s" % (row['from_name'],row['tier'],row['prize_name'],row['to_name'],time_to_string(row['create_time']))
            records.append(record)
        return records