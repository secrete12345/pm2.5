import os
import requests
import urllib3
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app.models import db, User
import app  # Access app.latest_aqi_data dynamically

main = Blueprint('main', __name__)

def get_area_list():
    """Reads options from list.txt inside the backend directory."""
    list_path = os.path.join(os.path.dirname(__file__), '..', 'list.txt')
    if os.path.exists(list_path):
        with open(list_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    return []

def clean_string(text):
    """Utility to remove whitespace, non-breaking spaces, and commas for flexible matching."""
    if not text:
        return ""
    return text.replace(',', '').replace(' ', '').replace('\xa0', '').strip()

def find_pm25_for_area(user_area):
    """Matches the user's selected area against the Air4Thai API station data."""
    # If the background fetch hasn't completed yet, trigger an immediate backup request
    if not app.latest_aqi_data:
        try:
            print("[AQI Fetcher] Cache empty on page load. Triggering instant fetch...")
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            resp = requests.get("https://air4thai.pcd.go.th/services/getNewAQI_JSON.php", timeout=5, verify=False)
            if resp.status_code == 200:
                app.latest_aqi_data = resp.json()
        except Exception as e:
            print(f"[AQI Fetcher] Instant fetch failed: {e}")

    stations = app.latest_aqi_data.get('stations', [])
    clean_user_area = clean_string(user_area)

    for station in stations:
        area_th = station.get('areaTH', '')
        name_th = station.get('nameTH', '')
        clean_area_th = clean_string(area_th)
        clean_name_th = clean_string(name_th)

        # Match cleaned text strings
        if clean_user_area in clean_area_th or clean_area_th in clean_user_area or clean_user_area in clean_name_th:
            # Check 'AQILast' key instead of 'LastUpdate'
            aqi_last = station.get('AQILast', {})
            
            pm25_info = aqi_last.get('PM25', {})
            aqi_info = aqi_last.get('AQI', {})

            pm25_val = pm25_info.get('value', 'N/A') if isinstance(pm25_info, dict) else 'N/A'
            aqi_val = aqi_info.get('aqi', 'N/A') if isinstance(aqi_info, dict) else 'N/A'

            date_str = aqi_last.get('date', '')
            time_str = aqi_last.get('time', '')

            return {
                'station_name': name_th or 'Unknown Station',
                'area': area_th,
                'pm25': pm25_val,
                'aqi': aqi_val,
                'updated_at': f"{date_str} {time_str}".strip()
            }
            
    return None

# 1. MAIN DASHBOARD
@main.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    current_user = User.query.get(session['user_id'])
    air_info = find_pm25_for_area(current_user.area)

    return render_template('index.html', user=current_user, air_info=air_info)

# 2. SIGN-UP
@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        selected_area = request.form.get('area')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists! Try logging in.')
            return redirect(url_for('main.signup'))

        new_user = User(username=username, area=selected_area)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.')
        return redirect(url_for('main.login'))

    areas = get_area_list()
    return render_template('signup.html', areas=areas)

# 3. LOGIN
@main.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password!')
            
    return render_template('login.html')

# 4. LOGOUT
@main.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.login'))