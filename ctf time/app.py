#!/usr/bin/env python3
"""
CTF Platform with Automatic Flag Checking
Individual competition, 10 contestants max, 6-hour duration
Start: 1:30 PM BD Time
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import json
import hashlib
import secrets
import pytz

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Bangladesh timezone
BD_TZ = pytz.timezone('Asia/Dhaka')

# Competition settings
START_TIME = datetime.now(BD_TZ).replace(hour=14, minute=0, second=0, microsecond=0)
END_TIME = START_TIME + timedelta(hours=12)
MAX_CONTESTANTS = 10
COMPETITION_ACTIVE = True

# Storage (in production, use database)
users = {}  # username: {password_hash, score, solves, registration_time}
scoreboard = []
challenge_solves = {}  # challenge_name: [users who solved]

# Load challenges
with open('ctfd-import/challenges.json', 'r') as f:
    CHALLENGES = json.load(f)['challenges']

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_flag(challenge_name, submitted_flag):
    """Check if submitted flag is correct"""
    for challenge in CHALLENGES:
        if challenge['name'] == challenge_name:
            correct_flags = challenge['flags']
            # Normalize flags (strip whitespace, case-sensitive)
            submitted_flag = submitted_flag.strip()
            return submitted_flag in correct_flags
    return False

def get_challenge_points(challenge_name):
    """Get points for a challenge"""
    for challenge in CHALLENGES:
        if challenge['name'] == challenge_name:
            return challenge['value']
    return 0

def is_competition_active():
    """Check if competition is currently active"""
    now = datetime.now(BD_TZ)
    return START_TIME <= now <= END_TIME

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    now = datetime.now(BD_TZ)
    time_remaining = END_TIME - now if now < END_TIME else timedelta(0)
    time_until_start = START_TIME - now if now < START_TIME else timedelta(0)
    
    return render_template('index.html',
                         username=session['username'],
                         challenges=CHALLENGES,
                         start_time=START_TIME.strftime('%I:%M %p'),
                         end_time=END_TIME.strftime('%I:%M %p'),
                         time_remaining=str(time_remaining).split('.')[0],
                         time_until_start=str(time_until_start).split('.')[0],
                         competition_started=now >= START_TIME,
                         competition_ended=now > END_TIME,
                         user_score=users[session['username']]['score'],
                         user_solves=users[session['username']]['solves'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '').strip()
        
        # Validation
        if not username or not password or not email:
            return jsonify({'error': 'All fields required'}), 400
        
        if username in users:
            return jsonify({'error': 'Username already exists'}), 400
        
        if len(users) >= MAX_CONTESTANTS:
            return jsonify({'error': f'Maximum {MAX_CONTESTANTS} contestants reached'}), 400
        
        # Register user
        users[username] = {
            'password_hash': hash_password(password),
            'email': email,
            'score': 0,
            'solves': [],
            'registration_time': datetime.now(BD_TZ).isoformat()
        }
        
        session['username'] = username
        return jsonify({'success': True, 'redirect': url_for('index')})
    
    return render_template('register.html', 
                         max_contestants=MAX_CONTESTANTS,
                         current_contestants=len(users))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if username not in users:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if users[username]['password_hash'] != hash_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        session['username'] = username
        return jsonify({'success': True, 'redirect': url_for('index')})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/submit_flag', methods=['POST'])
def submit_flag():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    if not is_competition_active():
        return jsonify({'error': 'Competition not active'}), 403
    
    username = session['username']
    challenge_name = request.json.get('challenge_name')
    submitted_flag = request.json.get('flag', '').strip()
    
    # Check if already solved
    if challenge_name in users[username]['solves']:
        return jsonify({'error': 'Already solved this challenge'}), 400
    
    # Validate flag
    if check_flag(challenge_name, submitted_flag):
        # Correct flag!
        points = get_challenge_points(challenge_name)
        users[username]['score'] += points
        users[username]['solves'].append(challenge_name)
        
        # Track solve
        if challenge_name not in challenge_solves:
            challenge_solves[challenge_name] = []
        challenge_solves[challenge_name].append({
            'username': username,
            'time': datetime.now(BD_TZ).isoformat()
        })
        
        return jsonify({
            'success': True,
            'message': f'Correct! +{points} points',
            'new_score': users[username]['score'],
            'total_solves': len(users[username]['solves'])
        })
    else:
        return jsonify({'error': 'Incorrect flag'}), 400

@app.route('/scoreboard')
def scoreboard():
    # Generate scoreboard
    leaderboard = []
    for username, data in users.items():
        leaderboard.append({
            'username': username,
            'score': data['score'],
            'solves': len(data['solves'])
        })
    
    # Sort by score (descending), then by solve count
    leaderboard.sort(key=lambda x: (-x['score'], -x['solves']))
    
    return render_template('scoreboard.html', 
                         leaderboard=leaderboard,
                         total_challenges=len(CHALLENGES))

@app.route('/challenges')
def challenges():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user_solves = users[username]['solves']
    
    # Group challenges by category
    categories = {}
    for challenge in CHALLENGES:
        cat = challenge['category']
        if cat not in categories:
            categories[cat] = []
        
        challenge_info = challenge.copy()
        challenge_info['solved'] = challenge['name'] in user_solves
        challenge_info['solve_count'] = len(challenge_solves.get(challenge['name'], []))
        categories[cat].append(challenge_info)
    
    return render_template('challenges.html', categories=categories)

@app.route('/challenge/<challenge_name>')
def challenge_detail(challenge_name):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    challenge = None
    for c in CHALLENGES:
        if c['name'] == challenge_name:
            challenge = c
            break
    
    if not challenge:
        return "Challenge not found", 404
    
    username = session['username']
    solved = challenge_name in users[username]['solves']
    
    return render_template('challenge.html', 
                         challenge=challenge, 
                         solved=solved,
                         solve_count=len(challenge_solves.get(challenge_name, [])))

@app.route('/api/time')
def api_time():
    """API endpoint for time synchronization"""
    now = datetime.now(BD_TZ)
    return jsonify({
        'current_time': now.isoformat(),
        'start_time': START_TIME.isoformat(),
        'end_time': END_TIME.isoformat(),
        'time_remaining_seconds': (END_TIME - now).total_seconds() if now < END_TIME else 0,
        'competition_active': is_competition_active()
    })

@app.route('/api/stats')
def api_stats():
    """API endpoint for competition statistics"""
    return jsonify({
        'total_contestants': len(users),
        'max_contestants': MAX_CONTESTANTS,
        'total_challenges': len(CHALLENGES),
        'total_solves': sum(len(users[u]['solves']) for u in users)
    })

if __name__ == '__main__':
    print("="*60)
    print("CTF COMPETITION SERVER")
    print("="*60)
    print(f"Start Time: {START_TIME.strftime('%I:%M %p BD Time')}")
    print(f"End Time: {END_TIME.strftime('%I:%M %p BD Time')}")
    print(f"Duration: 12 hours")
    print(f"Max Contestants: {MAX_CONTESTANTS}")
    print(f"Total Challenges: {len(CHALLENGES)}")
    print(f"\nScoring:")
    print("  150 points")
    print("  300 points")
    print("  500 points")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)

