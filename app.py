import os, json, uuid, hashlib, requests
from datetime import datetime
from functools import wraps
# pyrefly: ignore [missing-import]
from flask import (Flask, render_template, request, jsonify,
                   session, redirect, url_for, flash, send_from_directory)
# pyrefly: ignore [missing-import]
from werkzeug.security import generate_password_hash, check_password_hash
# pyrefly: ignore [missing-import]
from flask_dance.contrib.google import make_google_blueprint, google
from database import init_db, get_db, close_db
from skin_data import SKIN_CONDITIONS, PRODUCTS_DB, DIET_TIPS
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.teardown_appcontext(close_db)

app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'   # dev only – remove in prod

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_AI_STUDIO_API_KEY', '')
GEMINI_MODEL   = os.environ.get('GEMINI_MODEL', 'gemini-3.6-flash')
FREE_LIMIT     = 30

# ── Firebase Admin SDK Initialization
try:
    import firebase_admin
    from firebase_admin import credentials

    firebase_key_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY', 'serviceAccountKey.json')
    if os.path.exists(firebase_key_path):
        cred = credentials.Certificate(firebase_key_path)
        firebase_admin.initialize_app(cred)
        print(f"Firebase Admin SDK initialized using {firebase_key_path}")
    else:
        print(f"Firebase Admin SDK info: '{firebase_key_path}' not found. Place your serviceAccountKey.json in the project root to enable Admin features.")
except Exception as err:
    print(f"Firebase Admin SDK initialization note: {err}")

# ── Google OAuth blueprint
google_bp = make_google_blueprint(
    client_id     = os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET'),
    scope         = ['profile', 'email'],
    redirect_url  = '/auth/google/callback'
)
app.register_blueprint(google_bp, url_prefix='/login')


# ────────────────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────────────────

def gen_user_id():
    return 'SKN-' + hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16].upper()

def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return get_db().execute('SELECT * FROM users WHERE id=?', (uid,)).fetchone()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def can_analyze(uid):
    db  = get_db()
    row = db.execute('SELECT * FROM users WHERE id=?', (uid,)).fetchone()
    if not row:
        return False, 0, False
    return (bool(row['is_premium']) or row['analysis_count'] < FREE_LIMIT), \
           row['analysis_count'], bool(row['is_premium'])

def gemini_analyze(b64, skin_type, answers):
    if not GEMINI_API_KEY:
        return {
            "skin_type": skin_type or "Combination",
            "conditions_found": [
                {"name":"Acne","severity":"mild","affected_area":"T-zone","confidence":78},
                {"name":"Oily Skin","severity":"moderate","affected_area":"forehead","confidence":85}
            ],
            "overall_score": 65,
            "recommendations": {
                "creams":  ["Benzoyl peroxide cream","Niacinamide cream"],
                "soaps":   ["Salicylic acid face wash"],
                "tablets": ["Vitamin B5 supplement"],
                "serums":  ["Niacinamide 10% serum","Vitamin C serum"],
                "morning_routine": ["Gentle cleanser","Niacinamide serum","Oil-free moisturizer","SPF 50"],
                "evening_routine": ["Double cleanse","Salicylic acid toner","Light moisturizer"]
            },
            "diet_tips": {
                "eat":   ["Green vegetables","Omega-3 foods","Zinc-rich foods","Probiotics"],
                "avoid": ["Dairy","High-sugar foods","Greasy food","Processed snacks"]
            },
            "lifestyle_tips": [
                "Change pillowcases twice a week",
                "Clean phone screen daily",
                "Don't touch face with unwashed hands",
                "Use non-comedogenic products only"
            ],
            "see_doctor": False, "doctor_reason": ""
        }

    prompt = f"""You are an expert AI dermatologist. Analyze this facial skin image.
User skin type: {skin_type}. Questionnaire: {json.dumps(answers)}.

Return ONLY valid JSON (no markdown fences):
{{
  "skin_type":"Normal/Dry/Oily/Combination/Sensitive",
  "conditions_found":[{{"name":"...","severity":"mild/moderate/severe","affected_area":"...","confidence":80}}],
  "overall_score":70,
  "recommendations":{{"creams":[],"soaps":[],"tablets":[],"serums":[],"morning_routine":[],"evening_routine":[]}},
  "diet_tips":{{"eat":[],"avoid":[]}},
  "lifestyle_tips":[],
  "see_doctor":false,
  "doctor_reason":""
}}
Score 0=very poor, 100=perfect skin. confidence 0-100."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": b64
                        }
                    },
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }

    try:
        r = requests.post(url, json=payload, timeout=30)
        data = r.json()
        text = data['candidates'][0]['content']['parts'][0]['text'].strip()
        for fence in ['```json','```']:
            if text.startswith(fence): text = text[len(fence):]
        if text.endswith('```'): text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Gemini error: {e}")
        return None


# ────────────────────────────────────────────────────────────
# AUTH ROUTES
# ────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('index'))
    
    active_tab = request.args.get('active_tab', 'login')
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html', active_tab='login')
            
        db = get_db()
        # Find user by username or email
        row = db.execute('SELECT * FROM users WHERE username=? OR email=?', (username, username)).fetchone()
        
        if row and row['password_hash'] and check_password_hash(row['password_hash'], password):
            session['user_id'] = row['id']
            session['user_name'] = row['name'] or row['username'] or 'User'
            session['user_avatar'] = row['avatar'] or ''
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
            
    return render_template('login.html', active_tab=active_tab)

@app.route('/register', methods=['POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('index'))
        
    email = request.form.get('email', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    if not email or not username or not password or not confirm_password:
        flash('All fields are required.', 'error')
        return redirect(url_for('login', active_tab='register'))
        
    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('login', active_tab='register'))
        
    db = get_db()
    # Check if username exists
    exists_user = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
    if exists_user:
        flash('Username is already taken.', 'error')
        return redirect(url_for('login', active_tab='register'))
        
    # Check if email exists
    exists_email = db.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
    if exists_email:
        flash('Email is already registered.', 'error')
        return redirect(url_for('login', active_tab='register'))
        
    uid = gen_user_id()
    pw_hash = generate_password_hash(password)
    db.execute(
        'INSERT INTO users (id, username, name, email, password_hash, created_at, analysis_count) VALUES (?, ?, ?, ?, ?, ?, 0)',
        (uid, username, username, email, pw_hash, datetime.now().isoformat())
    )
    db.commit()
    
    session['user_id'] = uid
    session['user_name'] = username
    session['user_avatar'] = ''
    return redirect(url_for('index'))

@app.route('/auth/google/callback')
def google_callback():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get('/oauth2/v2/userinfo')
    if not resp.ok:
        flash('Google login failed. Try again.', 'error')
        return redirect(url_for('login'))

    info      = resp.json()
    google_id = info['id']
    email     = info.get('email', '')
    name      = info.get('name', 'User')
    avatar    = info.get('picture', '')

    db  = get_db()
    row = db.execute('SELECT * FROM users WHERE google_id=?', (google_id,)).fetchone()
    if row:
        uid = row['id']
        db.execute('UPDATE users SET name=?, avatar=? WHERE id=?', (name, avatar, uid))
    else:
        uid = gen_user_id()
        db.execute(
            'INSERT INTO users (id,google_id,name,email,avatar,created_at,analysis_count) VALUES (?,?,?,?,?,?,0)',
            (uid, google_id, name, email, avatar, datetime.now().isoformat())
        )
    db.commit()
    session['user_id'] = uid
    session['user_name'] = name
    session['user_avatar'] = avatar
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/auth/guest')
def guest_login():
    uid = gen_user_id()
    db  = get_db()
    guest_username = f"guest_{uid.split('-')[-1].lower()}"
    db.execute(
        'INSERT INTO users (id, username, name, email, created_at, analysis_count) VALUES (?, ?, ?, NULL, ?, 0)',
        (uid, guest_username, 'Guest', datetime.now().isoformat())
    )
    db.commit()
    session['user_id']   = uid
    session['user_name'] = 'Guest'
    return redirect(url_for('analyze'))


# ────────────────────────────────────────────────────────────
# MAIN ROUTES
# ────────────────────────────────────────────────────────────

@app.route('/sw.js')
def service_worker():
    return send_from_directory('.', 'sw.js', mimetype='application/javascript')

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/')
def index():
    user = current_user()
    return render_template('index.html', user=user)

@app.route('/analyze')
@login_required
def analyze():
    uid = session['user_id']
    ok, count, premium = can_analyze(uid)
    return render_template('analyze.html',
        user_id=uid, can_analyze=ok,
        count_used=count, free_limit=FREE_LIMIT, is_premium=premium)

@app.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    uid = session['user_id']
    ok, count, premium = can_analyze(uid)
    if not ok:
        return jsonify({'error':'free_limit_reached',
                        'message':f'All {FREE_LIMIT} free analyses used. Upgrade for ₹50/month.'}), 403

    data       = request.get_json()
    image_data = data.get('image','')
    skin_type  = data.get('skin_type','')
    answers    = data.get('answers',{})

    if not image_data:
        return jsonify({'error':'No image provided'}), 400
    if ',' in image_data:
        image_data = image_data.split(',')[1]

    analysis = gemini_analyze(image_data, skin_type, answers)
    if not analysis:
        return jsonify({'error':'Analysis failed. Please try again.'}), 500

    aid = str(uuid.uuid4())[:8].upper()
    db  = get_db()
    db.execute('''INSERT INTO analyses
        (id,user_id,skin_type,conditions,recommendations,diet_tips,
         lifestyle_tips,overall_score,see_doctor,doctor_reason,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (
        aid, uid,
        analysis.get('skin_type', skin_type),
        json.dumps(analysis.get('conditions_found',[])),
        json.dumps(analysis.get('recommendations',{})),
        json.dumps(analysis.get('diet_tips',{})),
        json.dumps(analysis.get('lifestyle_tips',[])),
        analysis.get('overall_score',0),
        1 if analysis.get('see_doctor') else 0,
        analysis.get('doctor_reason',''),
        datetime.now().isoformat()
    ))
    db.execute('UPDATE users SET analysis_count=analysis_count+1 WHERE id=?', (uid,))
    db.commit()

    return jsonify({'success':True, 'analysis_id':aid, 'analysis':analysis})

@app.route('/results/<aid>')
@login_required
def results(aid):
    db  = get_db()
    row = db.execute('SELECT * FROM analyses WHERE id=?', (aid,)).fetchone()
    if not row:
        return redirect(url_for('analyze'))

    uid = session['user_id']
    _, count, premium = can_analyze(uid)
    remaining = 999 if premium else max(0, FREE_LIMIT - count)

    return render_template('results.html',
        analysis={
            'id': row['id'], 'skin_type': row['skin_type'],
            'conditions':     json.loads(row['conditions']),
            'recommendations':json.loads(row['recommendations']),
            'diet_tips':      json.loads(row['diet_tips']),
            'lifestyle_tips': json.loads(row['lifestyle_tips']),
            'overall_score':  row['overall_score'],
            'see_doctor':     bool(row['see_doctor']),
            'doctor_reason':  row['doctor_reason'] or '',
            'created_at':     row['created_at']
        },
        products=PRODUCTS_DB,
        remaining=remaining,
        user=current_user()
    )

@app.route('/chat/<aid>')
@login_required
def chat(aid):
    db  = get_db()
    row = db.execute('SELECT * FROM analyses WHERE id=?', (aid,)).fetchone()
    if not row:
        return redirect(url_for('analyze'))
    chats = db.execute('SELECT * FROM chats WHERE analysis_id=? ORDER BY created_at', (aid,)).fetchall()
    return render_template('chat.html',
        analysis_id=aid,
        skin_type=row['skin_type'],
        conditions=json.loads(row['conditions']),
        chat_history=[{'role':c['role'],'message':c['message']} for c in chats],
        user=current_user()
    )

@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    data      = request.get_json()
    message   = data.get('message','').strip()
    aid       = data.get('analysis_id','')
    if not message:
        return jsonify({'error':'Empty message'}), 400

    db  = get_db()
    row = db.execute('SELECT * FROM analyses WHERE id=?', (aid,)).fetchone()
    context = ''
    if row:
        context = (f"User skin type: {row['skin_type']}. "
                   f"Conditions: {row['conditions']}. "
                   f"Recommendations: {row['recommendations']}.")

    prev = db.execute('SELECT role,message FROM chats WHERE analysis_id=? ORDER BY created_at',(aid,)).fetchall()
    messages = [{'role':c['role'],'content':c['message']} for c in prev]
    messages.append({'role':'user','content':message})

    if not GEMINI_API_KEY:
        ai_resp = ("Based on your skin analysis, I recommend starting with a gentle cleanser "
                   "followed by niacinamide serum (Minimalist 10%, ₹599 on Amazon India) to control oiliness. "
                   "Always finish your morning routine with SPF 50+. Consult a dermatologist for persistent concerns.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        system_text = (f"You are DermAI, a friendly AI skincare assistant. {context} "
                       "Give concise, accurate skincare advice. Suggest products with Indian ₹ prices "
                       "and mention Flipkart/Amazon India/Nykaa availability. "
                       "Always remind users to consult a dermatologist for serious conditions.")
        
        contents = []
        for msg_item in prev:
            role = "model" if msg_item['role'] == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": msg_item['message']}]})
        contents.append({"role": "user", "parts": [{"text": message}]})

        payload = {
            "system_instruction": {
                "parts": [{"text": system_text}]
            },
            "contents": contents
        }
        try:
            r = requests.post(url, json=payload, timeout=20)
            res_data = r.json()
            ai_resp = res_data['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    now = datetime.now().isoformat()
    db.execute('INSERT INTO chats (analysis_id,role,message,created_at) VALUES (?,?,?,?)',
               (aid,'user',message,now))
    db.execute('INSERT INTO chats (analysis_id,role,message,created_at) VALUES (?,?,?,?)',
               (aid,'assistant',ai_resp,now))
    db.commit()
    return jsonify({'response':ai_resp})

@app.route('/profile')
@login_required
def profile():
    uid  = session['user_id']
    db   = get_db()
    user = db.execute('SELECT * FROM users WHERE id=?', (uid,)).fetchone()
    rows = db.execute('SELECT * FROM analyses WHERE user_id=? ORDER BY created_at DESC', (uid,)).fetchall()
    history = [{'id':r['id'],'skin_type':r['skin_type'],
                'conditions':json.loads(r['conditions']),
                'overall_score':r['overall_score'],
                'see_doctor':bool(r['see_doctor']),
                'created_at':r['created_at']} for r in rows]
    return render_template('profile.html', user=user, history=history,
                           free_limit=FREE_LIMIT)

if __name__ == '__main__':
    init_db()
    print("DermAI starting -> http://127.0.0.1:5000")
    print("Set GEMINI_API_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET in .env")
    app.run(debug=True, port=5000)
