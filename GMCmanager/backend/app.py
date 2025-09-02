import os
from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS

def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # Enable CORS for APIs
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # --- ROUTES ---

    @app.get("/")
    def index():
        return render_template("dashboard.html")  # Make sure the filename matches (case-sensitive)

    # Serve each HTML page
    @app.get("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.get("/analytics")
    def analytics():
        return render_template("analytics.html")

    @app.get("/forecast")
    def forecast():
        return render_template("forecast.html")

    @app.get("/regional")
    def regional():
        return render_template("regional.html")

    @app.get("/inventory")
    def inventory():
        return render_template("inventory.html")

    @app.get("/sales")
    def sales():
        return render_template("sales.html")

    @app.get("/deliver")
    def deliver():
        return render_template("deliver.html")

    @app.get("/purchase")
    def purchase():
        return render_template("purchase.html")

    @app.get("/reports")
    def reports():
        return render_template("reports.html")

    @app.get("/user")
    def user():
        return render_template("user.html")
    
    @app.get("/notifications")
    def notifications():
        return render_template("notifications.html")

    @app.get("/settings")
    def settings():
        return render_template("settings.html")

    # Health check
    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "app": "GMC Manager"})

    return app


# Expose app for Gunicorn/Render
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
