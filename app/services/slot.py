import random
from datetime import datetime
from zoneinfo import ZoneInfo


class Slot:
    def __init__(self, user_id):
        # 初始化数据库连接
        from app import db_proxy
        self.db_proxy = db_proxy
        self.user_id = user_id
    
    def get_users(self):
        sql = "SELECT name FROM tbl_users WHERE id!=%s and role=%s"
        rows = self.db_proxy.run_sql_select(sql, params=(self.user_id,"user",))
        users = []
        for row in rows:
            users.append(row['name'])
        users.append('random')
        return users

    def get_points(self):
        sql = "SELECT points FROM tbl_users WHERE id=%s"
        row = self.db_proxy.run_sql_select(sql, params=(self.user_id,),fetch_one=True)
        return row['points']

    def get_self_points(self):
        sql = "SELECT self_points FROM tbl_users WHERE id=%s"
        row = self.db_proxy.run_sql_select(sql, params=(self.user_id,),fetch_one=True)
        return row['self_points']

    def get_avatar_path(self):
        sql = "SELECT avatar_path FROM tbl_users WHERE id=%s"
        row = self.db_proxy.run_sql_select(sql, params=(self.user_id,),fetch_one=True)
        return row['avatar_path']

    def get_first_prize(self):
        sql = "SELECT id, name, first_tier_prob FROM tbl_prize WHERE is_first_tier=1 and stock > 0"
        rows = self.db_proxy.run_sql_select(sql)
        return self._pick_prize_by_probability(rows, 'first_tier_prob')
    
    def get_second_prize(self):
        sql = "SELECT id, name, second_tier_prob FROM tbl_prize WHERE is_second_tier=1 and stock > 0"
        rows = self.db_proxy.run_sql_select(sql)
        return self._pick_prize_by_probability(rows, 'second_tier_prob')
    
    def get_third_prize(self):
        sql = "SELECT id, name, third_tier_prob FROM tbl_prize WHERE is_third_tier=1 and stock > 0"
        rows = self.db_proxy.run_sql_select(sql)
        return self._pick_prize_by_probability(rows, 'third_tier_prob')

    def _pick_prize_by_probability(self, prizes, prob_field):
        # 确保概率都是 float 类型
        probs = [float(p[prob_field]) for p in prizes]
        total = sum(probs)

        # 生成一个 0 到 total 之间的随机数
        r = random.uniform(0, total)
        cumulative = 0

        for prize in prizes:
            cumulative += float(prize[prob_field])
            if r <= cumulative:
                return prize

        # 理论上不会走到这里，但为了安全兜底
        return prizes[-1]

    def update_stock(self, prize_id):
        sql = "UPDATE tbl_prize SET stock = stock -1 WHERE id = %s"
        self.db_proxy.run_sql_update(sql, params=(prize_id,))

    def update_record(self, selected_user, selected_tier, prize_id):
        sql = "SELECT id FROM tbl_users WHERE name =%s"
        row = self.db_proxy.run_sql_select(sql, params=(selected_user,), fetch_one=True)
        pacific_time = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d %H:%M:%S")
        sql = "INSERT INTO tbl_records (from_id, to_id, prize_id, tier, create_time) VALUES (%s, %s, %s, %s, %s)"
        self.db_proxy.run_sql_update(sql, params=(self.user_id, row['id'], prize_id, selected_tier, pacific_time))
    
    def update_points(self, points):
        sql = "UPDATE tbl_users SET points = points -%s WHERE id = %s"
        self.db_proxy.run_sql_update(sql, params=(points, self.user_id))

    def update_self_points(self, points):
        sql = "UPDATE tbl_users SET self_points = self_points -%s WHERE id = %s"
        self.db_proxy.run_sql_update(sql, params=(points, self.user_id))

    def check_points(self, points):
        sql = "SELECT points FROM tbl_users WHERE id =%s"
        row = self.db_proxy.run_sql_select(sql, params=(self.user_id,), fetch_one=True)
        if row['points'] < points:
            return False
        return True

    def check_self_points(self, points):
        sql = "SELECT self_points FROM tbl_users WHERE id =%s"
        row = self.db_proxy.run_sql_select(sql, params=(self.user_id,), fetch_one=True)
        if row['self_points'] < points:
            return False
        return True

    def get_bonus_points(self, bonus_points):
        sql = "UPDATE tbl_users SET self_points = self_points + %s WHERE id = %s"
        self.db_proxy.run_sql_update(sql, params=(bonus_points, self.user_id))

    def is_first(self):
        sql = "SELECT is_first FROM tbl_users WHERE id =%s"
        row = self.db_proxy.run_sql_select(sql, params=(self.user_id,), fetch_one=True)
        return row['is_first'] == 1
    
    def update_is_first(self):
        sql = "UPDATE tbl_users SET is_first = 0 WHERE id = %s"
        self.db_proxy.run_sql_update(sql, params=(self.user_id,))

    def get_random_user(self):
        sql = "SELECT name FROM tbl_users WHERE id!=%s and role=%s"
        rows = self.db_proxy.run_sql_select(sql, params=(self.user_id,"user",))
        users = []
        for row in rows:
            users.append(row['name'])
        return random.choice(users)
