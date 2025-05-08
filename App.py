import os
from flask import Flask, render_template, redirect, url_for, session, request
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import jwt
from datetime import datetime, timedelta, timezone
import traceback
from flask_session import Session

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Session configuration (ensure to set secure cookies in production)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = True # Make this True for Production
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_session'
app.config['SESSION_PERMANENT'] = False

Session(app)
# Secret key for session management
app.secret_key = os.getenv("SECRET_KEY")

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)

# DB config
#Debug or testing
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SUPABASE_DB_URL")

db = SQLAlchemy(app)

# Google OAuth setup
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://oauth2.googleapis.com/token"
userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
scope = ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"]

# JWT secret
JWT_SECRET = os.getenv("JWT_SECRET_KEY")


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(128))
    email = db.Column(db.String(128))
    picture = db.Column(db.String(256))

@app.route('/login')
def login():
    next_url = request.args.get('next')
    session['next_url'] = next_url  # Save for after callback
    #chumma
    redirect_uri = url_for('callback', _external=True)
    print("Generated Redirect URI:", redirect_uri)  # <-- ADD THIS LINE
    
    google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
    authorization_url, state = google.authorization_url(authorization_base_url, access_type='offline', prompt='select_account')
    session['oauth_state'] = state
    return redirect(authorization_url)


@app.route('/login/callback')
def callback():
    try:
        if 'oauth_state' not in session:
            print("Missing 'oauth_state' in session. Possible session loss.")
            return redirect(url_for('login'))  # Redirect instead of 403
        redirect_uri = url_for('callback', _external=True)
        google = OAuth2Session(client_id, redirect_uri=redirect_uri, state=session['oauth_state'])

        token = google.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url, include_client_id=True)

        session['oauth_token'] = token
        resp = google.get(userinfo_url)
        user_data = resp.json()

        # Check if user exists
        user = User.query.filter_by(google_id=user_data["id"]).first()
        if not user:
            user = User(
                google_id=user_data["id"],
                name=user_data["name"],
                email=user_data["email"],
                picture=user_data["picture"]
            )
            db.session.add(user)
            db.session.commit()
            
        # Save user info in session
        session['user'] = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "picture": user.picture
        }


        # Generate JWT token
        payload = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        session['jwt'] = token
        # After login
        next_url = session.pop('next_url', None)
        if next_url:
            return redirect(next_url)
        return redirect(url_for('home'))
    
    except Exception as e:
        traceback.print_exc()
        return f"OAuth Error: {e}", 403


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))

# end

# Topic list and mapping
topics = [
    {"name": "Python", "description": "Learn Python programming from basics to advanced."},
    {"name": "Libraries", "description": "Explore libraries like Numpy, Pandas, Matplotlib, and more."},
    {"name": "Data Wrangling", "description": "Master data cleaning and preprocessing techniques."},
    {"name": "Statistics", "description": "Understand statistical concepts for data analysis."},
    {"name": "Probability", "description": "Dive into probability theory and its applications."},
    {"name": "Linear Algebra", "description": "Learn linear algebra for machine learning and data science."},
    {"name": "Calculus", "description": "Understand calculus concepts for optimization."},
    {"name": "DSA", "description": "Practice Data Structures and Algorithms."},
    {"name": "Tableau", "description": "Learn Tableau for data visualization."},
    {"name": "Power BI", "description": "Master Power BI for business intelligence."},
    {"name": "Power Query", "description": "Master Power Query for Data Cleaning."},
]

# Add slug to each topic
for topic in topics:
    topic['slug'] = topic['name'].lower().replace(" ", "-")

# Route: Home Page
@app.route('/')
def home():
    user = session.get('user')
    return render_template('home.html', topics=topics, user=user)

# Route: Subpages using slug
@app.route('/topic/<slug>')
def topic_page(slug):
    user = session.get('user')
    if not user:
        # Redirect to login and remember the page the user was trying to access
        return redirect(url_for('login', next=request.path))
        
    # Find topic by slug
    topic = next((t for t in topics if t['slug'] == slug), None)
    if topic:
        try:
            return render_template(f"{topic['name']}.html", topic_name=topic['name'])
        except:
            return render_template('404.html'), 404
    else:
        return render_template('404.html'), 404

# Route: 404 Error Page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Route: Contact Page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Run app for deployment
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
