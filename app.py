# app.py
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os

# ─────────────────────────────────────────────────────────────
# ✅ Load environment variables early
# ─────────────────────────────────────────────────────────────
load_dotenv()

# ─────────────────────────────────────────────────────────────
# ✅ Initialize Flask
# ─────────────────────────────────────────────────────────────
app = Flask(__name__)

# CORS: allow your React app to call this API.
# If you know your frontend origin (e.g., https://boostentryai.com),
# replace origins=["*"] with that exact origin for stricter security.
CORS(
    app,
    resources={r"/api/*": {"origins": ["*"]}},
    supports_credentials=False,
)

# ─────────────────────────────────────────────────────────────
# ✅ Import & register blueprints (routes)
# ─────────────────────────────────────────────────────────────
from routes.upload_routes import upload_bp
from routes.human_review_routes import human_review_bp
from routes.dashboard_routes import dashboard_bp
from routes.fix_review_routes import fix_review_bp
from routes.monitoring_routes import monitoring_bp
from routes.login_route import login_bp
from routes.users_logs_route import users_logs_bp
from routes.data_transformation_routes import data_transformation_bp
from routes.vehicle_hire_routes import vehicle_hire_bp
from routes.whatsapp_routes import whatsapp_bp  # ← NEW: WhatsApp webhook API

app.register_blueprint(upload_bp)
app.register_blueprint(monitoring_bp)
app.register_blueprint(human_review_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(fix_review_bp)
app.register_blueprint(login_bp)
app.register_blueprint(users_logs_bp)
app.register_blueprint(data_transformation_bp)
app.register_blueprint(vehicle_hire_bp)
app.register_blueprint(whatsapp_bp)  # ← register WhatsApp blueprint

# ─────────────────────────────────────────────────────────────
# ✅ Environment / Paths (for debugging + file serving)
# ─────────────────────────────────────────────────────────────
ENVIRONMENT = os.getenv("ENVIRONMENT", "LOCAL")
UPLOAD_FOLDER = os.path.abspath(os.getenv("UPLOAD_FOLDER", "uploaded_docs"))

print(f"✅ Environment: {ENVIRONMENT}")
print(f"✅ Upload folder: {UPLOAD_FOLDER}")

# Serve PDF/images uploaded by the app
@app.route("/uploaded_docs/<path:filename>")
def serve_uploaded_docs(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ─────────────────────────────────────────────────────────────
# ✅ Simple health check
# ─────────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "environment": ENVIRONMENT,
        "upload_folder": UPLOAD_FOLDER,
    }), 200

# ─────────────────────────────────────────────────────────────
# ✅ Error handlers (nice JSON for common cases)
# ─────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(err):
    return jsonify({"status": "error", "message": "Not found"}), 404

@app.errorhandler(500)
def server_error(err):
    return jsonify({"status": "error", "message": "Server error"}), 500

# ─────────────────────────────────────────────────────────────
# ✅ Entrypoint
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Start WhatsApp reminder scheduler
    try:
        from whatsapp_reminder import start_reminder_scheduler
        start_reminder_scheduler()
    except Exception as e:
        print(f"⚠️ Could not start WhatsApp reminder scheduler: {e}")
    
    print("\n📱 WhatsApp integration is active!")
    print("   - Webhook: /api/whatsapp/webhook")
    print("   - Reminders: Every 3 hours for pending sessions\n")
    
    # 0.0.0.0 exposes the server to the network (Docker friendly),
    # port 30010 matches your existing mapping.
    app.run(host="0.0.0.0", port=30010, debug=True, use_reloader=False)

