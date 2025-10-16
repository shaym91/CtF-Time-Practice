from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_from_directory
from datetime import datetime, timedelta
import pytz
import hashlib
import json
import os

app = Flask(__name__)
app.secret_key = 'ctf_secret_key_2024_secure_random'

# Bangladesh timezone
BD_TZ = pytz.timezone('Asia/Dhaka')

# Competition times - 6 PM to 6 PM next day (12 hours)
START_TIME = datetime.now(BD_TZ).replace(hour=18, minute=0, second=0, microsecond=0)
END_TIME = START_TIME + timedelta(hours=12)

# Max contestants
MAX_CONTESTANTS = 10

# In-memory database (use proper database in production)
users = {}
submissions = {}

# 18 Real Challenges
CHALLENGES = [
    # CRYPTO
    {'id': 1, 'name': 'Caesar Twist', 'category': 'Crypto', 'difficulty': 'Medium', 'points': 150, 'flag': 'FLAG{d0uble_shift_d0nt_yield_shift}', 'description': 'Julius Caesar used simple shifts, but this one has a twist! Decode the encrypted message.'},
    {'id': 2, 'name': 'RSA Madness', 'category': 'Crypto', 'difficulty': 'Hard', 'points': 300, 'flag': 'FLAG{sm4ll_pr1m3s_ar3_b4d}', 'description': 'A custom RSA implementation with some interesting properties. Can you break it?'},
    {'id': 3, 'name': 'Quantum Cipher', 'category': 'Crypto', 'difficulty': 'Insane', 'points': 500, 'flag': 'FLAG{qu4ntum_3ntr0py_br0k3n}', 'description': 'A cutting-edge quantum cipher. Break the quantum encryption.'},
    
    # WEB
    {'id': 4, 'name': 'SQL Injection', 'category': 'Web', 'difficulty': 'Medium', 'points': 150, 'flag': 'FLAG{sql_1nj3ct10n_1s_cl4ss1c}', 'description': 'A simple login portal. Bypass the authentication.'},
    {'id': 5, 'name': 'XSS + CSRF Chain', 'category': 'Web', 'difficulty': 'Hard', 'points': 300, 'flag': 'FLAG{ch41n_4tt4ck_succ3ss}', 'description': 'Chain XSS and CSRF to perform a sophisticated attack.'},
    {'id': 6, 'name': 'Prototype Pollution', 'category': 'Web', 'difficulty': 'Insane', 'points': 500, 'flag': 'FLAG{pr0t0typ3_p011ut10n_rc3}', 'description': 'A Node.js application vulnerable to prototype pollution leading to RCE.'},
    
    # FORENSICS
    {'id': 7, 'name': 'Hidden Data', 'category': 'Forensics', 'difficulty': 'Medium', 'points': 150, 'flag': 'FLAG{st3g0_1s_h1dd3n_w3ll}', 'description': 'An image file with hidden data. Extract the secret.'},
    {'id': 8, 'name': 'Memory Dump', 'category': 'Forensics', 'difficulty': 'Hard', 'points': 300, 'flag': 'FLAG{m3m0ry_s3cr3ts_f0und}', 'description': 'A memory dump from a compromised system. Find the evidence.'},
    {'id': 9, 'name': 'PCAP Analysis', 'category': 'Forensics', 'difficulty': 'Insane', 'points': 500, 'flag': 'FLAG{n3tw0rk_tr4ff1c_d3c0d3d}', 'description': 'Network packet capture with encrypted protocols. Decrypt and analyze.'},
    
    # REVERSE
    {'id': 10, 'name': 'Basic Crackme', 'category': 'Reverse', 'difficulty': 'Medium', 'points': 150, 'flag': 'FLAG{r3v3rs3_3ng1n33r1ng_w1n}', 'description': 'A password checker program. Find the correct password.'},
    {'id': 11, 'name': 'Anti-Debug', 'category': 'Reverse', 'difficulty': 'Hard', 'points': 300, 'flag': 'FLAG{4nt1_d3bug_byp4ss3d}', 'description': 'Binary with anti-debugging protection. Bypass it.'},
    {'id': 12, 'name': 'VM Obfuscation', 'category': 'Reverse', 'difficulty': 'Insane', 'points': 500, 'flag': 'FLAG{v1rtu4l_m4ch1n3_d3c0d3d}', 'description': 'Binary implementing a custom virtual machine. Reverse the bytecode.'},
    
    # PWN
    {'id': 13, 'name': 'Buffer Overflow', 'category': 'Pwn', 'difficulty': 'Medium', 'points': 150, 'flag': 'FLAG{buff3r_0v3rfl0w_pwn3d}', 'description': 'Classic buffer overflow. Overwrite the return address.'},
    {'id': 14, 'name': 'ROP Chain', 'category': 'Pwn', 'difficulty': 'Hard', 'points': 300, 'flag': 'FLAG{r0p_ch41n_c0nstruct3d}', 'description': 'Build a ROP chain to execute win() function.'},
    {'id': 15, 'name': 'Heap Exploit', 'category': 'Pwn', 'difficulty': 'Insane', 'points': 500, 'flag': 'FLAG{h34p_3xpl01t_m4st3r}', 'description': 'Advanced heap exploitation. Corrupt the heap metadata.'},
    
    # OSINT
    {'id': 16, 'name': 'Social Media Hunt', 'category': 'OSINT', 'difficulty': 'Medium', 'points': 150, 'flag': 'FLAG{Alice_Rust_Berlin}', 'description': 'Find the hacker: ctf_hacker_2024. Discover their name, language, and city.'},
    {'id': 17, 'name': 'Digital Footprint', 'category': 'OSINT', 'difficulty': 'Hard', 'points': 300, 'flag': 'FLAG{d1g1t4l_tr4c3s_f0und}', 'description': 'Advanced digital footprint investigation. Follow the traces.'},
    {'id': 18, 'name': 'Deep Investigation', 'category': 'OSINT', 'difficulty': 'Insane', 'points': 500, 'flag': 'FLAG{d33p_1nv3st1g4t10n_c0mpl3t3}', 'description': 'Intelligence analysis with multi-source correlation.'}
]

def is_competition_active():
    """Check if competition is active"""
    now = datetime.now(BD_TZ)
    return START_TIME <= now <= END_TIME

def get_time_remaining():
    """Get time remaining in competition"""
    now = datetime.now(BD_TZ)
    if now < START_TIME:
        return "Not started"
    elif now > END_TIME:
        return "Ended"
    else:
        remaining = END_TIME - now
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        return f"{hours}h {minutes}m"

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('challenges'))
    return render_template('index.html', start_time=START_TIME, end_time=END_TIME)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if len(users) >= MAX_CONTESTANTS:
        return "Maximum contestants reached!", 403
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if username in users:
            return "Username already exists!", 400
        
        users[username] = {
            'email': email,
            'password': hashlib.sha256(password.encode()).hexdigest(),
            'score': 0,
            'solved': [],
            'last_solve_time': None
        }
        
        session['username'] = username
        return redirect(url_for('challenges'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == hashlib.sha256(password.encode()).hexdigest():
            session['username'] = username
            return redirect(url_for('challenges'))
        
        return "Invalid credentials!", 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/challenges')
def challenges():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if not is_competition_active():
        return render_template('challenges.html', 
                             challenges=CHALLENGES, 
                             time_remaining=get_time_remaining(),
                             active=False)
    
    username = session['username']
    solved_ids = users[username]['solved']
    
    return render_template('challenges.html', 
                         challenges=CHALLENGES, 
                         solved=solved_ids,
                         time_remaining=get_time_remaining(),
                         active=True)

@app.route('/challenge/<int:challenge_id>')
def challenge(challenge_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if not is_competition_active():
        return "Competition not active!", 403
    
    challenge = next((c for c in CHALLENGES if c['id'] == challenge_id), None)
    if not challenge:
        return "Challenge not found!", 404
    
    username = session['username']
    solved = challenge_id in users[username]['solved']
    
    return render_template('challenge.html', 
                         challenge=challenge, 
                         solved=solved,
                         time_remaining=get_time_remaining())

@app.route('/submit/<int:challenge_id>', methods=['POST'])
def submit(challenge_id):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    if not is_competition_active():
        return jsonify({'success': False, 'message': 'Competition not active'})
    
    username = session['username']
    flag = request.form['flag'].strip()
    
    challenge = next((c for c in CHALLENGES if c['id'] == challenge_id), None)
    if not challenge:
        return jsonify({'success': False, 'message': 'Challenge not found'})
    
    if challenge_id in users[username]['solved']:
        return jsonify({'success': False, 'message': 'Already solved'})
    
    if flag == challenge['flag']:
        users[username]['solved'].append(challenge_id)
        users[username]['score'] += challenge['points']
        users[username]['last_solve_time'] = datetime.now(BD_TZ)
        
    return jsonify({
            'success': True, 
            'message': f'Correct! +{challenge["points"]} points',
            'points': challenge['points']
        })
    
    return jsonify({'success': False, 'message': 'Incorrect flag'})

@app.route('/scoreboard')
def scoreboard():
    # Sort users by score (desc) and last solve time (asc)
    leaderboard = sorted(
        [(username, data) for username, data in users.items()],
        key=lambda x: (-x[1]['score'], x[1]['last_solve_time'] or datetime.max.replace(tzinfo=BD_TZ))
    )
    
    return render_template('scoreboard.html', 
                         leaderboard=leaderboard,
                         time_remaining=get_time_remaining())

@app.route('/files/<path:filename>')
def download_file(filename):
    return send_from_directory('static/files', filename)

@app.route('/api/scoreboard')
def api_scoreboard():
    leaderboard = sorted(
        [(username, data) for username, data in users.items()],
        key=lambda x: (-x[1]['score'], x[1]['last_solve_time'] or datetime.max.replace(tzinfo=BD_TZ))
    )
    
    return jsonify([{
        'username': username,
        'score': data['score'],
        'solved_count': len(data['solved'])
    } for username, data in leaderboard])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)