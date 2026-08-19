import os, json, uuid, hashlib, requests
from datetime import datetime, timedelta
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

app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'dermai-skincare-secret-key-2026-production'
if not os.environ.get('VERCEL') and not os.environ.get('OAUTHLIB_INSECURE_TRANSPORT'):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'   # dev only – remove in prod

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_AI_STUDIO_API_KEY', '')
GEMINI_MODEL   = os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash')
FREE_LIMIT     = 30

# ── Firebase Admin SDK Initialization
try:
    import firebase_admin
    from firebase_admin import credentials

    firebase_key = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY', 'serviceAccountKey.json')
    if firebase_key and firebase_key.strip().startswith('{'):
        cred_dict = json.loads(firebase_key)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized using JSON environment variable.")
    elif os.path.exists(firebase_key):
        cred = credentials.Certificate(firebase_key)
        firebase_admin.initialize_app(cred)
        print(f"Firebase Admin SDK initialized using {firebase_key}")
    else:
        print(f"Firebase Admin SDK info: '{firebase_key}' not found. Place your serviceAccountKey.json in the project root to enable Admin features.")
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

AUTO_PURGE_SECONDS = 18060  # 5 Hours 1 Minute (5*3600 + 60)

def auto_purge_expired_images_and_data():
    """
    5-Hour 1-Minute Auto-Purge Protocol:
    Automatically deletes all temporary image files, uploaded photos,
    and sensitive cached assets older than 5 hours 1 minute (18,060 seconds).
    Facial photos are never stored permanently.
    """
    temp_dirs = [os.path.join('static', 'temp_scans'), os.path.join('static', 'uploads'), 'temp_scans']
    now_ts = datetime.now().timestamp()
    for tdir in temp_dirs:
        if os.path.exists(tdir):
            for fname in os.listdir(tdir):
                fpath = os.path.join(tdir, fname)
                if os.path.isfile(fpath):
                    file_age = now_ts - os.path.getmtime(fpath)
                    if file_age >= AUTO_PURGE_SECONDS:
                        try:
                            os.remove(fpath)
                            print(f"[5-Hour Auto-Purge] Deleted expired sensitive image asset: {fname}")
                        except Exception as e:
                            print(f"[Purge Warning] Could not remove {fname}: {e}")

@app.before_request
def trigger_auto_purge():
    auto_purge_expired_images_and_data()

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

def get_fallback_analysis(skin_type, answers):
    st = skin_type or "Combination"
    conditions = []
    if "Oily" in st or "Combination" in st:
        conditions.append({"name": "Excess Sebum & Oiliness", "severity": "moderate", "affected_area": "T-Zone & Forehead", "confidence": 88})
        conditions.append({"name": "Enlarged Pores", "severity": "mild", "affected_area": "Nose & Cheeks", "confidence": 82})
    if "Dry" in st or "Sensitive" in st:
        conditions.append({"name": "Dehydration & Dryness", "severity": "moderate", "affected_area": "Cheeks & Jawline", "confidence": 85})
        conditions.append({"name": "Skin Barrier Sensitivity", "severity": "mild", "affected_area": "Cheeks", "confidence": 79})
    if not conditions:
        conditions.append({"name": "Mild Acne & Blemishes", "severity": "mild", "affected_area": "Chin & Forehead", "confidence": 80})
        conditions.append({"name": "Uneven Skin Tone", "severity": "mild", "affected_area": "Cheeks", "confidence": 75})

    return {
        "skin_type": st,
        "conditions_found": conditions,
        "overall_score": 72 if "Normal" in st else 65,
        "recommendations": {
            "creams":  ["CeraVe Moisturizing Lotion", "Minimalist 10% Niacinamide Cream", "Neutrogena Hydro Boost Water Gel"],
            "soaps":   ["Cetaphil Gentle Skin Cleanser", "Minimalist 2% Salicylic Acid Face Wash"],
            "tablets": ["Zinc & Vitamin B5 Skin Supplement"],
            "serums":  ["Minimalist 10% Niacinamide Serum (₹599)", "Derma Co 2% Salicylic Acid Serum (₹499)", "Plum 15% Vitamin C Serum (₹550)"],
            "morning_routine": [
                "Gentle cleansing with lukewarm water",
                "Apply Niacinamide 10% serum",
                "Lightweight oil-free moisturizer",
                "Broad-spectrum SPF 50+ Sunscreen (Reapply every 3 hours)"
            ],
            "evening_routine": [
                "Double cleanse to remove sunscreen & impurites",
                "Apply Salicylic Acid treatment",
                "Apply barrier repair night moisturizer"
            ]
        },
        "diet_tips": {
            "eat":   ["Green leafy vegetables & berries", "Omega-3 rich seeds & fish oil", "Probiotic yogurt & green tea"],
            "avoid": ["Excessive refined sugar & dairy", "Deep-fried & high-sodium snacks", "Alcohol & sugary drinks"]
        },
        "lifestyle_tips": [
            "Drink at least 2.5–3 Liters of water daily",
            "Change pillowcases twice a week to prevent bacteria build-up",
            "Avoid touching your face with unwashed hands",
            "Always use non-comedogenic and dermatologically tested products"
        ],
        "see_doctor": False,
        "doctor_reason": ""
    }

def gemini_analyze(b64, skin_type, answers):
    if not GEMINI_API_KEY:
        return get_fallback_analysis(skin_type, answers)

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
        if r.status_code != 200:
            print(f"Gemini API returned status {r.status_code}: {r.text[:200]}")
            return get_fallback_analysis(skin_type, answers)
        data = r.json()
        text = data['candidates'][0]['content']['parts'][0]['text'].strip()
        for fence in ['```json','```']:
            if text.startswith(fence): text = text[len(fence):]
        if text.endswith('```'): text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Gemini error: {e}")
        return get_fallback_analysis(skin_type, answers)


# ────────────────────────────────────────────────────────────
# AUTH ROUTES
# ────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('index'))
    
    active_tab = request.args.get('active_tab', 'login')
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username or not password:
                flash('Please enter both username and password.', 'error')
                return render_template('login.html', active_tab='login')
                
            db = get_db()
            row = db.execute('SELECT * FROM users WHERE username=? OR email=?', (username, username)).fetchone()
            
            if row and row['password_hash'] and check_password_hash(row['password_hash'], password):
                session['user_id'] = row['id']
                session['user_name'] = row['name'] or row['username'] or 'User'
                session['user_avatar'] = row['avatar'] or ''
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.', 'error')
        except Exception as e:
            print(f"[Login Error] {e}")
            flash('Login error occurred. Please try again.', 'error')
            
    return render_template('login.html', active_tab=active_tab)

@app.route('/register', methods=['POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('index'))
        
    try:
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
    except Exception as e:
        print(f"[Register Error] {e}")
        flash(f'Registration error: {str(e)}', 'error')
        return redirect(url_for('login', active_tab='register'))

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
    try:
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
    except Exception as e:
        print(f"[Guest Auth Warning] {e}")
        if 'uid' not in locals():
            uid = gen_user_id()
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
    try:
        user = current_user()
        return render_template('index.html', user=user)
    except Exception as e:
        print(f"[Index Route Error] {e}")
        return render_template('index.html', user=None)

@app.route('/analyze')
@login_required
def analyze():
    try:
        uid = session['user_id']
        ok, count, premium = can_analyze(uid)
        return render_template('analyze.html',
            user_id=uid, can_analyze=ok,
            count_used=count, free_limit=FREE_LIMIT, is_premium=premium)
    except Exception as e:
        print(f"[Analyze Route Error] {e}")
        return render_template('analyze.html',
            user_id=session.get('user_id', 'SKN-GUEST'), can_analyze=True,
            count_used=0, free_limit=FREE_LIMIT, is_premium=False)

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
            if r.status_code == 200:
                res_data = r.json()
                ai_resp = res_data['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"Gemini Chat API Error status {r.status_code}: {r.text[:200]}")
                ai_resp = ("Based on your skin profile, I recommend maintaining a consistent daily routine: "
                           "use a gentle pH-balanced cleanser twice daily, apply a 10% Niacinamide serum for oil/pore control "
                           "(e.g., Minimalist 10% Niacinamide at ~₹599 on Nykaa/Amazon), and never skip an SPF 50+ sunscreen. "
                           "If you experience persistent inflammation or cystic lesions, please consult a certified dermatologist.")
        except Exception as e:
            print(f"Gemini chat error: {e}")
            ai_resp = ("Based on your skin profile, I recommend maintaining a consistent daily routine: "
                       "use a gentle pH-balanced cleanser twice daily, apply a 10% Niacinamide serum for oil/pore control "
                       "(e.g., Minimalist 10% Niacinamide at ~₹599 on Nykaa/Amazon), and never skip an SPF 50+ sunscreen. "
                       "If you experience persistent inflammation or cystic lesions, please consult a certified dermatologist.")

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

@app.route('/privacy')
def privacy():
    user = current_user()
    return render_template('privacy.html', user=user)

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    if request.path.startswith('/privacy') or request.path.startswith('/analyze'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

if __name__ == '__main__':
    init_db()
    print("DermAI starting -> http://127.0.0.1:5000")
    print("Set GEMINI_API_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET in .env")
    app.run(debug=True, port=5000)

