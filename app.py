from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_from_directory
from datetime import datetime, timedelta
import pytz
import hashlib
import json
import os

app = Flask(__name__)
app.secret_key = 'ctf_secret_key_2024_ultra_secure_random_key'

# Bangladesh timezone
BD_TZ = pytz.timezone('Asia/Dhaka')

# Competition times - 5 PM to 5 AM (12 hours)
# Get today's 5 PM or tomorrow's 5 PM depending on current time
now = datetime.now(BD_TZ)
if now.hour < 17:
    # If before 5 PM, start today at 5 PM
    START_TIME = now.replace(hour=17, minute=0, second=0, microsecond=0)
else:
    # If after 5 PM, start tomorrow at 5 PM
    START_TIME = (now + timedelta(days=1)).replace(hour=17, minute=0, second=0, microsecond=0)

END_TIME = (START_TIME + timedelta(hours=12)).replace(hour=5, minute=0, second=0, microsecond=0)

# Max contestants
MAX_CONTESTANTS = 50

# In-memory database (use proper database in production)
users = {}
submissions = {}

# 18 INSANE Level Challenges - NO DIFFICULTY LABELS, ONLY POINTS
CHALLENGES = [
    # CRYPTO (INSANE LEVEL)
    {'id': 1, 'name': 'Caesar Twist', 'category': 'Crypto', 'points': 150, 'flag': 'FLAG{d0uble_shift_d0nt_yield_shift}', 'description': 'Multi-layer Caesar cipher with position-based shifts and case manipulation. Decode the encrypted message.'},
    {'id': 2, 'name': 'RSA Madness', 'category': 'Crypto', 'points': 300, 'flag': 'FLAG{sm4ll_pr1m3s_ar3_b4d}', 'description': 'Vulnerable RSA with close twin primes. Use Fermat\'s factorization method to break the encryption.'},
    {'id': 3, 'name': 'Quantum Cipher', 'category': 'Crypto', 'points': 500, 'flag': 'FLAG{qu4ntum_3ntr0py_br0k3n}', 'description': 'BB84 quantum protocol with key reuse vulnerability. Analyze quantum measurements and break the cipher.'},
    
    # WEB (INSANE LEVEL)
    {'id': 4, 'name': 'SQL Injection', 'category': 'Web', 'points': 150, 'flag': 'FLAG{sql_1nj3ct10n_1s_cl4ss1c}', 'description': 'WAF-protected SQL injection. Bypass filters using advanced techniques to access admin panel.'},
    {'id': 5, 'name': 'XSS + CSRF Chain', 'category': 'Web', 'points': 300, 'flag': 'FLAG{ch41n_4tt4ck_succ3ss}', 'description': 'Chain XSS and CSRF vulnerabilities. Steal admin session and execute privileged actions.'},
    {'id': 6, 'name': 'Prototype Pollution', 'category': 'Web', 'points': 500, 'flag': 'FLAG{pr0t0typ3_p011ut10n_rc3}', 'description': 'Node.js prototype pollution leading to RCE. Exploit the merge function to gain admin privileges.'},
    
    # FORENSICS (INSANE LEVEL)
    {'id': 7, 'name': 'Hidden Data', 'category': 'Forensics', 'points': 150, 'flag': 'FLAG{st3g0_1s_h1dd3n_w3ll}', 'description': 'Multi-layer LSB steganography in PNG. Extract hidden data from complex image encoding.'},
    {'id': 8, 'name': 'Memory Dump', 'category': 'Forensics', 'points': 300, 'flag': 'FLAG{m3m0ry_s3cr3ts_f0und}', 'description': 'Advanced memory forensics with anti-analysis. Use Volatility to find hidden malware artifacts.'},
    {'id': 9, 'name': 'PCAP Analysis', 'category': 'Forensics', 'points': 500, 'flag': 'FLAG{n3tw0rk_tr4ff1c_d3c0d3d}', 'description': 'Encrypted network traffic analysis. Decrypt protocols and reconstruct the hidden communication.'},
    
    # REVERSE (INSANE LEVEL)
    {'id': 10, 'name': 'Basic Crackme', 'category': 'Reverse', 'points': 150, 'flag': 'FLAG{r3v3rs3_3ng1n33r1ng_w1n}', 'description': 'Obfuscated password checker with anti-tamper. Static analysis required to extract the key.'},
    {'id': 11, 'name': 'Anti-Debug', 'category': 'Reverse', 'points': 300, 'flag': 'FLAG{4nt1_d3bug_byp4ss3d}', 'description': 'Multiple anti-debugging techniques and VM detection. Bypass all protections to get the flag.'},
    {'id': 12, 'name': 'VM Obfuscation', 'category': 'Reverse', 'points': 500, 'flag': 'FLAG{v1rtu4l_m4ch1n3_d3c0d3d}', 'description': 'Custom VM with obfuscated bytecode. Reverse engineer the architecture and decode instructions.'},
    
    # PWN (INSANE LEVEL)
    {'id': 13, 'name': 'Buffer Overflow', 'category': 'Pwn', 'points': 150, 'flag': 'FLAG{buff3r_0v3rfl0w_pwn3d}', 'description': 'Stack buffer overflow with canaries. Bypass stack protection to execute win() function.'},
    {'id': 14, 'name': 'ROP Chain', 'category': 'Pwn', 'points': 300, 'flag': 'FLAG{r0p_ch41n_c0nstruct3d}', 'description': 'ASLR and NX enabled. Construct ROP chain with limited gadgets to gain code execution.'},
    {'id': 15, 'name': 'Heap Exploit', 'category': 'Pwn', 'points': 500, 'flag': 'FLAG{h34p_3xpl01t_m4st3r}', 'description': 'Custom heap allocator with metadata corruption. Advanced heap feng shui required.'},
    
    # OSINT (INSANE LEVEL)
    {'id': 16, 'name': 'Social Media Hunt', 'category': 'OSINT', 'points': 150, 'flag': 'FLAG{Alice_Rust_Berlin}', 'description': 'Multi-platform social media investigation. Find name, programming language, and city location.'},
    {'id': 17, 'name': 'Digital Footprint', 'category': 'OSINT', 'points': 300, 'flag': 'FLAG{d1g1t4l_tr4c3s_f0und}', 'description': 'Advanced digital reconnaissance across deep web. Correlate multiple sources to track the target.'},
    {'id': 18, 'name': 'Deep Investigation', 'category': 'OSINT', 'points': 500, 'flag': 'FLAG{d33p_1nv3st1g4t10n_c0mpl3t3}', 'description': 'Intelligence analysis with multi-source correlation. APT group attribution and infrastructure mapping.'}
]

def is_competition_active():
    """Check if competition is active"""
    now = datetime.now(BD_TZ)
    return START_TIME <= now <= END_TIME

def get_time_remaining():
    """Get time remaining in competition"""
    now = datetime.now(BD_TZ)
    if now < START_TIME:
        delta = START_TIME - now
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f"Starts in {hours}h {minutes}m"
    elif now > END_TIME:
        return "Competition Ended"
    else:
        remaining = END_TIME - now
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        return f"{hours}h {minutes}m remaining"

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('challenges'))
    return render_template('index.html', start_time=START_TIME, end_time=END_TIME, year=2024)

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
            'last_solve_time': None,
            'solve_times': []
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
        solve_time = datetime.now(BD_TZ)
        users[username]['last_solve_time'] = solve_time
        users[username]['solve_times'].append({
            'challenge_id': challenge_id,
            'points': challenge['points'],
            'time': solve_time
        })
        
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
    
    # Calculate stats for graphs
    category_stats = {}
    for challenge in CHALLENGES:
        cat = challenge['category']
        if cat not in category_stats:
            category_stats[cat] = {'total': 0, 'solved': 0}
        category_stats[cat]['total'] += 1
        
        # Count how many users solved this
        solved_count = sum(1 for u in users.values() if challenge['id'] in u['solved'])
        category_stats[cat]['solved'] += solved_count
    
    # Calculate solve progression over time
    all_solves = []
    for username, data in users.items():
        for solve in data.get('solve_times', []):
            all_solves.append({
                'username': username,
                'time': solve['time'],
                'points': solve['points']
            })
    all_solves.sort(key=lambda x: x['time'])
    
    return render_template('scoreboard.html', 
                         leaderboard=leaderboard,
                         time_remaining=get_time_remaining(),
                         category_stats=category_stats,
                         all_solves=all_solves,
                         total_challenges=len(CHALLENGES))

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
        'rank': idx + 1,
        'username': username,
        'score': data['score'],
        'solved_count': len(data['solved'])
    } for idx, (username, data) in enumerate(leaderboard)])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)