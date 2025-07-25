from flask import Flask
from src.routes import auth, dashboard, anak, user

app = Flask(__name__)
app.secret_key = "rahasia_super_secret"
app.template_folder = "templates"

# Register all route blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(dashboard.bp)
app.register_blueprint(anak.bp)
app.register_blueprint(user.bp)

if __name__ == "__main__":
    app.run(debug=True)
