import os
from datetime import datetime
import json
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
# ... (Configuration, Extensions, and Models are the same as before) ...
app.config["SECRET_KEY"] = "a-super-secret-key-that-you-should-change"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "home"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    body_type = db.Column(db.String(50), nullable=True)
    logs = db.relationship(
        "Log", backref="author", lazy=True, cascade="all, delete-orphan"
    )
    plans = db.relationship(
        "Plan", backref="author", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config["SECRET_KEY"])
        return s.dumps({"user_id": self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token, max_age=expires_sec)["user_id"]
        except:
            return None
        return db.session.get(User, user_id)


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    date_logged = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    plan_data = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
def home():
    return render_template("index.html")


# ... (All previous API routes remain the same) ...
@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json()
    if not data or not all(k in data for k in ["name", "email", "phone", "password"]):
        return jsonify({"error": "Missing required fields"}), 400
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email address already in use"}), 409
    new_user = User(name=data["name"], email=data["email"], phone=data["phone"])
    new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    if not data or not all(k in data for k in ["email", "password"]):
        return jsonify({"error": "Missing email or password"}), 400
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401
    login_user(user)
    return (
        jsonify(
            {
                "message": "Login successful",
                "user": {"name": user.name, "email": user.email},
            }
        ),
        200,
    )


@app.route("/api/logout", methods=["POST"])
@login_required
def api_logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200


@app.route("/api/status")
@login_required
def api_status():
    return jsonify(
        {
            "logged_in": True,
            "user": {"name": current_user.name, "email": current_user.email},
        }
    )


# --- NEW PASSWORD RESET ROUTES ---
@app.route("/api/forgot-password", methods=["POST"])
def api_forgot_password():
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "Email field is required"}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if user:
        token = user.get_reset_token()
        # In a real app, you would email this link. For now, we print it.
        print("--- PASSWORD RESET ---")
        print(f"Click here to reset password for {user.email}:")
        print(f"http://127.0.0.1:5000/reset-password/{token}")
        print("--- END PASSWORD RESET ---")

    # For security, always return the same message whether the user exists or not.
    return (
        jsonify(
            {
                "message": "If an account with that email exists, a reset link has been generated."
            }
        ),
        200,
    )


@app.route("/api/reset-password/<token>", methods=["POST"])
def api_reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        return jsonify({"error": "Token is invalid or has expired"}), 401

    data = request.get_json()
    if not data or "password" not in data:
        return jsonify({"error": "Password is required"}), 400

    user.set_password(data["password"])
    db.session.commit()
    return jsonify({"message": "Your password has been updated successfully."}), 200


# ... (The rest of the API routes: /api/details, /api/logs, /api/generate-plan, /api/plans) ...
@app.route("/api/details", methods=["GET", "POST"])
@login_required
def api_details():
    if request.method == "POST":
        data = request.get_json()
        current_user.age = data.get("age", current_user.age)
        current_user.height = data.get("height", current_user.height)
        current_user.weight = data.get("weight", current_user.weight)
        current_user.body_type = data.get("bodyType", current_user.body_type)
        db.session.commit()
        return jsonify({"message": "Details updated successfully"}), 200
    return jsonify(
        {
            "age": current_user.age,
            "height": current_user.height,
            "weight": current_user.weight,
            "bodyType": current_user.body_type,
        }
    )


@app.route("/api/logs", methods=["GET", "POST"])
@login_required
def api_logs():
    if request.method == "POST":
        data = request.get_json()
        if not data or "weight" not in data:
            return jsonify({"error": "Missing weight field"}), 400
        try:
            weight = float(data["weight"])
        except ValueError:
            return jsonify({"error": "Invalid weight format"}), 400
        new_log = Log(weight=weight, author=current_user)
        db.session.add(new_log)
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Log added successfully",
                    "log": {
                        "id": new_log.id,
                        "weight": new_log.weight,
                        "date": new_log.date_logged,
                    },
                }
            ),
            201,
        )
    logs = [
        {
            "id": log.id,
            "weight": log.weight,
            "date": log.date_logged.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for log in current_user.logs
    ]
    return jsonify(logs)


@app.route("/api/generate-plan", methods=["POST"])
@login_required
def api_generate_plan():
    data = request.get_json()
    body_type = data.get("bodyType")
    plan = {"diet": [], "workouts": []}
    if body_type == "ectomorph":
        plan["diet"] = [
            {
                "title": "Overnight Oats",
                "time": "Prep 5 min",
                "steps": [
                    "Combine oats, milk, protein powder.",
                    "Stir in peanut butter and honey.",
                    "Top with banana and refrigerate.",
                ],
            },
            {
                "title": "High-Calorie Chicken Bowl",
                "time": "25 min",
                "steps": [
                    "Marinate & grill 200g chicken.",
                    "Serve with 1.5 cups rice and veggies.",
                ],
            },
        ]
        plan["workouts"] = [
            {
                "level": "Beginner (3x/week) — Full-body compound",
                "desc": "Focus on heavy compound lifts.",
                "exercises": [
                    {"name": "Back Squat", "steps": ["3 working sets × 6–8 reps."]},
                    {"name": "Deadlift", "steps": ["3 sets × 4–6 reps."]},
                    {"name": "Bench Press", "steps": ["3 sets × 6–8 reps."]},
                ],
            }
        ]
    elif body_type == "mesomorph":
        plan["diet"] = [
            {
                "title": "Veggie Omelet",
                "time": "10 min",
                "steps": [
                    "Whisk 3 eggs.",
                    "Sauté veggies, pour eggs, cook. Serve with toast.",
                ],
            },
            {
                "title": "Grilled Chicken + Sweet Potato",
                "time": "30 min",
                "steps": [
                    "Grill chicken breasts.",
                    "Roast sweet potato wedges. Serve with greens.",
                ],
            },
        ]
        plan["workouts"] = [
            {
                "level": "Push / Pull / Legs (4x week)",
                "desc": "Balanced hypertrophy & strength.",
                "exercises": [
                    {"name": "Squat", "steps": ["4 sets × 6–8 reps."]},
                    {"name": "Incline Bench", "steps": ["4 sets × 8–10 reps."]},
                    {"name": "Barbell Row", "steps": ["3 sets × 8–10 reps."]},
                ],
            }
        ]
    elif body_type == "endomorph":
        plan["diet"] = [
            {
                "title": "Greek Yogurt Bowl",
                "time": "5 min",
                "steps": ["200g Greek yogurt, add chia seeds and berries."],
            },
            {
                "title": "Grilled Fish + Large Salad",
                "time": "20 min",
                "steps": ["Grill fish fillet, serve over mixed greens."],
            },
        ]
        plan["workouts"] = [
            {
                "level": "Circuit + Strength (Beginner)",
                "desc": "Cardio-focused circuits.",
                "exercises": [
                    {
                        "name": "HIIT Sprints",
                        "steps": ["8–10 rounds of 30s sprint / 60s walk."],
                    },
                    {
                        "name": "Burpees Circuit",
                        "steps": ["3 rounds: 12 burpees, 20 squats, 30s plank."],
                    },
                ],
            }
        ]
    else:
        return jsonify({"error": "Invalid body type specified"}), 400
    return jsonify(plan)


@app.route("/api/plans", methods=["GET", "POST"])
@login_required
def api_plans():
    if request.method == "POST":
        data = request.get_json()
        if not data or "planData" not in data or "userDetails" not in data:
            return jsonify({"error": "Missing plan data"}), 400
        user_details = data["userDetails"]
        body_type = user_details.get("bodyType", "Custom").capitalize()
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        plan_name = f"{body_type} Plan - {date_str}"
        new_plan = Plan(name=plan_name, plan_data=json.dumps(data), author=current_user)
        db.session.add(new_plan)
        db.session.commit()
        return (
            jsonify({"message": "Plan saved successfully", "plan_name": plan_name}),
            201,
        )
    plans = []
    sorted_plans = sorted(
        current_user.plans, key=lambda p: p.date_created, reverse=True
    )
    for plan in sorted_plans:
        plans.append(
            {
                "id": plan.id,
                "name": plan.name,
                "date_created": plan.date_created.strftime("%Y-%m-%d"),
                "data": json.loads(plan.plan_data),
            }
        )
    return jsonify(plans)


@app.route("/reset-password/<token>")
def reset_token(token):
    # This route just serves the main page. JS will handle the token.
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
