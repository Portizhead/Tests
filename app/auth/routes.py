from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

@auth_bp.get("/ping")
def ping():
    return {"auth": "ok"}
