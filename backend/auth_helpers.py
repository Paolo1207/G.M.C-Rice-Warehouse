# backend/auth_helpers.py
from functools import wraps
from flask import g, session, jsonify

# --- Example current user loader ---
def get_current_user():
    """
    Pull current user from session (or token, later if you add JWT).
    Assumes you store `session["user"] = {"id": ..., "role": ...}`
    """
    return session.get("user")

# --- Decorator for any role ---
def role_required(role):
    """
    Decorator that enforces a single role.
    Usage: @role_required("admin")
    """
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user or user.get("role") != role:
                return jsonify({"ok": False, "error": "Access denied"}), 403
            g.current_user = user  # stash in flask.g for downstream
            return f(*args, **kwargs)
        return decorated
    return wrapper

# --- Decorators for specific roles ---
def admin_required(f):
    return role_required("admin")(f)

def manager_required(f):
    return role_required("manager")(f)

# --- Optional: allow multiple roles ---
def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user or user.get("role") not in roles:
                return jsonify({"ok": False, "error": "Access denied"}), 403
            g.current_user = user
            return f(*args, **kwargs)
        return decorated
    return wrapper
