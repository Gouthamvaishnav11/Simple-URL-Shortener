from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(10), unique=True, nullable=False)

def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(6))
    return short_url

@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form.get('url')
    if not original_url:
        return "URL parameter is required", 400
    
    short_url = generate_short_url()
    url_exists = URL.query.filter_by(short_url=short_url).first()
    while url_exists:
        short_url = generate_short_url()
        url_exists = URL.query.filter_by(short_url=short_url).first()

    new_url = URL(original_url=original_url, short_url=short_url)
    db.session.add(new_url)
    db.session.commit()

    return f'Shortened URL: {request.host_url}{short_url}'

@app.route('/<short_url>')
def redirect_url(short_url):
    url = URL.query.filter_by(short_url=short_url).first_or_404()
    return redirect(url.original_url)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    
    app.run(debug=True, port=3000)
