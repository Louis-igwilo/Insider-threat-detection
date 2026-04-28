from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random
import time
from datetime import datetime

app = Flask(__name__)
# This key secures your sessions. Keep it consistent.
app.secret_key = "soc_alpha_2026_sentinel_key"

# --- 1. GLOBAL STATE (Simulating the Database) ---
# Pre-populating 50 users
users_db = {
    f"USR-{1000+i}": {
        "user_id": f"USR-{1000+i}",
        "dept": random.choice(['IT', 'Finance', 'Legal', 'Ops']),
        "burn": 0.0
    } for i in range(50)
}

# Alerts will use user_id as keys to prevent duplicates automatically
active_alerts = {}
event_logs = []

# --- 2. THE SECURITY ENGINE ---
def run_simulation_engine():
    """Simulates background network activity and risk detection."""
    # Pick a random user ID from our keys
    uid = random.choice(list(users_db.keys()))
    user = users_db[uid]
    
    # 20% chance of a high-risk activity spike
    if random.random() < 0.20:
        user['burn'] += 0.4
    
    # Risk Logic
    burn_score = user['burn']
    if burn_score >= 0.8:
        lvl = "HIGH"
    elif burn_score >= 0.4:
        lvl = "MEDIUM"
    else:
        lvl = "LOW"
    
    # Deduplicated Alerting
    if lvl in ["HIGH", "MEDIUM"]:
        # If the user is already in alerts, we just update the level (no duplicate cards)
        active_alerts[uid] = {
            "id": f"AL-{int(time.time())}",
            "time": datetime.now().strftime("%H:%M:%S"),
            "user_id": uid,
            "level": lvl,
            "dept": user['dept']
        }

    # Add to live log feed
    log_entry = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "user_id": uid,
        "risk": lvl
    }
    event_logs.insert(0, log_entry) # Keep newest at top
    if len(event_logs) > 30: event_logs.pop()

# --- 3. ROUTES & PAGE RENDERING ---

@app.route('/')
def index():
    """Main Dashboard - Only accessible if logged in."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles Analyst Authorization."""
    error = None
    if request.method == 'POST':
        # Your specific credentials
        if request.form['username'] == 'admin' and request.form['password'] == 'soc_alpha_2026':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = "Invalid Analyst ID or Security Key"
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- 4. API ENDPOINTS (For JavaScript Communication) ---

@app.route('/api/status')
def get_status():
    """Endpoint called by dashboard.js every 3 seconds."""
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Run one cycle of the engine whenever the dashboard checks for status
    run_simulation_engine()
    
    return jsonify({
        "alerts": list(active_alerts.values()),
        "logs": event_logs,
        "stats": {
            "total_threats": len(active_alerts),
            "critical_count": len([a for a in active_alerts.values() if a['level'] == 'HIGH'])
        }
    })

@app.route('/api/resolve', methods=['POST'])
def resolve_threat():
    """Endpoint to clear a specific user's alerts and risk score."""
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    uid = data.get('user_id')
    
    if uid in active_alerts:
        del active_alerts[uid]
    
    if uid in users_db:
        users_db[uid]['burn'] = 0.0
        
    return jsonify({"status": "success", "message": f"User {uid} re-baselined."})

@app.route('/api/user_details/<uid>')
def user_details(uid):
    """Fetches forensic details for the investigation panel."""
    if uid in users_db:
        return jsonify(users_db[uid])
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)