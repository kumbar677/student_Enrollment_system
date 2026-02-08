from flask import Flask, redirect, url_for
from config import Config
from models import db, User
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)

    mail = Mail(app)
    app.extensions['mail'] = mail

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Import and register blueprints
    try:
        from routes.auth_routes import auth_bp
        from routes.admin_routes import admin_bp
        from routes.student_routes import student_bp
        from routes.chatbot_routes import chatbot_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(student_bp, url_prefix='/student')
        app.register_blueprint(chatbot_bp)
    except ImportError as e:
        print(f"Blueprints error: {e}")

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    @app.route('/debug-db')
    def debug_db():
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            users_columns = []
            if 'users' in tables:
                for col in inspector.get_columns('users'):
                    users_columns.append(f"{col['name']} ({col['type']})")
            
            return f"""
            <h1>Database Debug</h1>
            <p><strong>Database URL:</strong> {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[-1]}</p>
            <p><strong>Tables:</strong> {tables}</p>
            <p><strong>Users Columns:</strong> {users_columns}</p>
            """
        except Exception as e:
            return f"<h1>Debug Error</h1><p>{e}</p>"

    return app


# ✅ WSGI app for Gunicorn (RENDER NEEDS THIS)
app = create_app()

# ✅ Create tables on Render startup
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created successfully.")
        
        # Seed Admin User if not exists
        if not User.query.filter_by(role='admin').first():
            admin = User(name='Admin User', email='ACV@gmail.com', role='admin')
            admin.set_password('ACV123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created/verified.")
            
    except Exception as e:
        print(f"⚠️ Error initializing database: {e}")


# Local development only
if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()

            # Seed Admin User
            if not User.query.filter_by(role='admin').first():
                admin = User(name='Admin User', email='ACV@gmail.com', role='admin')
                admin.set_password('ACV123')
                db.session.add(admin)
                db.session.commit()
                print("Admin user created.")
        except Exception as e:
            print(f"Database error: {e}")

    app.run(debug=True, host='0.0.0.0', port=5000)
