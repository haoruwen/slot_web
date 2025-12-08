from flask import session, request, Blueprint, render_template, redirect, url_for
from app.services.user import User
from app.services.administrator import Administrator
from app.services.slot import Slot
from utils.decorators import login_required
from utils.config import *

# 创建页面蓝图
main_bp = Blueprint('main', __name__)

# 首页路由
@main_bp.route('/', methods=['GET', 'POST'])
@login_required
def admin_home():
    admin = Administrator()
    if request.method == 'GET':
        if session.get('role') != 'administrator':
            # 普通用户不能访问首页，跳到 draw home 页面
            return redirect(url_for('main.draw'))
        users = admin.get_all_users()
        return render_template('index.html', users=users)
    if request.method == 'POST':
        update_user_id = request.form['update_user']
        update_user_points = request.form.get(f'points_{update_user_id}')
        if update_user_points:
            admin.update_user_points(update_user_id, update_user_points)
        return redirect(url_for('main.admin_home'))

@main_bp.route('/draw', methods=['GET', 'POST'])
@login_required
def draw():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('user.login'))
    slot = Slot(current_user_id)
    avatar_path = slot.get_avatar_path()
    if request.method == 'GET':
        return render_template('draw_home.html', avatar_path = avatar_path)

    
@main_bp.route('/draw/others', methods=['GET', 'POST'])
@login_required
def draw_others():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('user.login'))
    slot = Slot(current_user_id)
    avatar_path = slot.get_avatar_path()
    user_points = slot.get_points()
    if request.method == 'GET':
        user_names = slot.get_users()
        return render_template('draw_others.html', users=user_names, points = user_points, tiers=TIERS, avatar_path = avatar_path)
    if request.method == 'POST':
        selected_user = request.form.get('user')
        if selected_user == RANDOM_USER:
            selected_user = slot.get_random_user()
        selected_tier = request.form.get('tier')
        prize = None
        if selected_tier == 'first':
            if not slot.check_points(FIRST_TIER_POINTS):
                user_names = slot.get_users()
                return render_template('draw_others.html', users=user_names, points = user_points,tiers=TIERS, error=POINTS_ERROR_MESSAGE, avatar_path = avatar_path)
            prize = slot.get_first_prize()
            slot.update_points(FIRST_TIER_POINTS)
            if slot.is_first():
                slot.update_is_first()
                slot.get_bonus_points(FIRST_TIER_POINTS)
            else:
                slot.get_bonus_points(FIRST_TIER_BONUS_POINTS)
        elif selected_tier == 'second':
            if not slot.check_points(SECOND_TIER_POINTS):
                user_names = slot.get_users()
                return render_template('draw_others.html', users=user_names, points = user_points,tiers=TIERS, error=POINTS_ERROR_MESSAGE, avatar_path = avatar_path)
            prize = slot.get_second_prize()
            slot.update_points(SECOND_TIER_POINTS)
            if slot.is_first():
                slot.update_is_first()
                slot.get_bonus_points(SECOND_TIER_POINTS)
            else:
                slot.get_bonus_points(SECOND_TIER_BONUS_POINTS)
        else:
            if not slot.check_points(THIRD_TIER_POINTS):
                user_names = slot.get_users()
                return render_template('draw_others.html', users=user_names, points = user_points,tiers=TIERS, error=POINTS_ERROR_MESSAGE, avatar_path = avatar_path)
            prize = slot.get_third_prize()
            slot.update_points(THIRD_TIER_POINTS)
            if slot.is_first():
                slot.update_is_first()
                slot.get_bonus_points(THIRD_TIER_POINTS)
            else:
                slot.get_bonus_points(THIRD_TIER_BONUS_POINTS)
        slot.update_stock(prize['id'])
        slot.update_record(selected_user, selected_tier, prize['id'])
        return render_template('result.html', prize=prize['name'], mode="others")
    
@main_bp.route('/draw/self', methods=['GET', 'POST'])
@login_required
def draw_self():
    current_user_id = session.get('user_id')
    current_user_name = session.get('username')
    if not current_user_id:
        return redirect(url_for('user.login'))
    slot = Slot(current_user_id)
    avatar_path = slot.get_avatar_path()
    user_self_points = slot.get_self_points()
    if request.method == 'GET':
        return render_template('draw_self.html', points = user_self_points, tiers=TIERS, avatar_path = avatar_path)
    if request.method == 'POST':
        selected_tier = request.form.get('tier')
        prize = None
        if selected_tier == 'first':
            if not slot.check_self_points(FIRST_TIER_POINTS):
                return render_template('draw_self.html', points = user_self_points, tiers=TIERS, error=POINTS_ERROR_MESSAGE, avatar_path = avatar_path)
            prize = slot.get_first_prize()
            slot.update_self_points(FIRST_TIER_POINTS)
        elif selected_tier == 'second':
            if not slot.check_self_points(SECOND_TIER_POINTS):
                return render_template('draw_self.html',points = user_self_points, tiers=TIERS, error=POINTS_ERROR_MESSAGE, avatar_path = avatar_path)
            prize = slot.get_second_prize()
            slot.update_self_points(SECOND_TIER_POINTS)
        else:
            if not slot.check_self_points(THIRD_TIER_POINTS):
                return render_template('draw_self.html', points = user_self_points, tiers=TIERS, error=POINTS_ERROR_MESSAGE, avatar_path = avatar_path)
            prize = slot.get_third_prize()
            slot.update_self_points(THIRD_TIER_POINTS)

        slot.update_stock(prize['id'])
        slot.update_record(current_user_name, selected_tier, prize['id'])
        return render_template('result.html', prize=prize['name'], mode="self")

@main_bp.route('/records', methods=['GET'])
@login_required
def records():
    admin = Administrator()
    if request.method == 'GET':
        all_records = admin.get_all_records()
        return render_template('records.html', records=all_records)

def get_client_ip():
    # 获取真实 IP（支持反向代理）
    if request.headers.get('X-Forwarded-For'):
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    return request.remote_addr

user_bp = Blueprint('user', __name__)
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    client_ip = get_client_ip()
    user = User()
    if not user.validate_user(ip_address=client_ip):
        return f"permission denied", 403

    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        validate, info = user.validate(username, password)
        
        if validate:
            session['user_id'] = info['id']
            session['username'] = info['name']
            session['role'] = info['role']

            if session['role'] == 'user':
                return redirect(url_for('main.draw'))
            if session['role'] == 'administrator':
                return redirect(url_for('main.admin_home'))

        remaining_time = user.fail_attempt(client_ip)
        if remaining_time == 0:
            return f"permission denied", 403
        return render_template('login.html', msg=info + ". %s attempts left before permanent ban." % remaining_time)

@user_bp.route('/logout')
def logout():
    # 清空当前用户的 session
    session.clear()
    return redirect(url_for('user.login'))
