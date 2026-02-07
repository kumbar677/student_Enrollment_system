import os
import sys
from pyngrok import ngrok
from app import create_app, db, User

# Define the port
PORT = 5000

def start_app_with_tunnel():
    # Upgrade / Create DB if needed (same as app.py)
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            if not User.query.filter_by(role='admin').first():
                admin = User(name='Admin User', email='ACV@gmail.com', role='admin')
                admin.set_password('ACV123')
                db.session.add(admin)
                db.session.commit()
                print("Admin user created.")
        except Exception as e:
            print(f"Database error: {e}")

    # Open a ngrok tunnel to the HTTP server
    try:
        # Attempt to use the user's requested custom domain
        # Note: You must reserve this domain in your ngrok dashboard: https://dashboard.ngrok.com/cloud-edge/domains
        public_url = ngrok.connect(PORT, domain="iac3-cultural-sync-club.ngrok-free.dev").public_url
    except Exception as e:
        print(f"Warning: Could not use custom domain (iac3-cultural-sync-club.ngrok-free.dev).")
        print(f"Reason: {e}")
        print("Falling back to a random public URL...")
        public_url = ngrok.connect(PORT).public_url
    print("="*60)
    print(f" * PUBLIC URL GOES HERE -> {public_url}")
    print("   (Share this link to open on any mobile)")
    print("="*60)

    # Store public URL in config for email links
    app.config['PUBLIC_URL'] = public_url

    # Update app to run without reloader to prevent creating multiple tunnels
    app.run(port=PORT, debug=False)

if __name__ == '__main__':
    start_app_with_tunnel()
