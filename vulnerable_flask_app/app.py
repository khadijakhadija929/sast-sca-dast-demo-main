import os
from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)
# 1. Secret lu dans l'environnement (plus de secret en dur)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-temporaire')

# 3. Liste blanche de commandes autorisées
ALLOWED = {"date": ["date"], "uptime": ["uptime"]}

# 7. En-têtes de sécurité (Anti-Clickjacking, CSP, etc.)
@app.after_request
def security_headers(resp):
    resp.headers["Content-Security-Policy"] = "default-src 'self'"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp

@app.route('/')
def index():
    return """
    <h1>Welcome to our vulnerable Flask App! 😎</h1>
    <p>Explore the different pages:</p>
    <ul>
        <li><a href="/hello?name=World">Hello Page (try changing the name in the URL!)</a></li>
        <li><a href="/execute?cmd=date">Execute Command Page (try changing the command in the URL!)</a></li>
    </ul>
    """

@app.route('/hello')
def hello():
    name = request.args.get('name', 'Guest')
    # 2. Échappement HTML (anti-XSS)
    return f"<h1>Hello Page</h1><p>Hello, {escape(name)}!</p>"

@app.route('/execute')
def execute():
    import subprocess
    key = request.args.get('cmd', 'date')
    
    # Vérification de la liste blanche
    if key not in ALLOWED:
        return "Commande non autorisée", 400
        
    # Pas de shell=True (anti-injection de commande)
    out = subprocess.run(ALLOWED[key], capture_output=True, text=True)
    
    # Échappement HTML du résultat
    return f"<h1>Execute Command Page</h1><pre>{escape(out.stdout)}</pre>"

# 4. La route /admin a été supprimée (ou protégée par une authentification)

if __name__ == '__main__':
    # 5. Debug désactivé par défaut (sauf si FLASK_DEBUG=1)
    debug = os.environ.get("FLASK_DEBUG") == "1"
    app.run(debug=debug, host='0.0.0.0')
