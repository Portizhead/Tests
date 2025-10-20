from flask import Blueprint, request, jsonify, render_template
from ..models import db, Pokemon

main_bp = Blueprint("main", __name__)

@main_bp.get("/")
def home():
    return render_template("home.html")

@main_bp.get("/pokedex")
def list_pokemon():
    items = Pokemon.query.all()
    return jsonify([{"id":p.id, "name":p.name, "type":p.type, "level":p.level} for p in items])

@main_bp.post("/pokedex")
def create_pokemon():
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return {"error":"name required"}, 400
    p = Pokemon(name=name, type=data.get("type"), level=data.get("level", 1))
    db.session.add(p)
    db.session.commit()
    return {"id":p.id, "name":p.name, "type":p.type, "level":p.level}, 201

@main_bp.get("/pokedex/<int:pid>")
def get_pokemon(pid):
    p = Pokemon.query.get_or_404(pid)
    return {"id":p.id, "name":p.name, "type":p.type, "level":p.level}

@main_bp.put("/pokedex/<int:pid>")
def update_pokemon(pid):
    p = Pokemon.query.get_or_404(pid)
    data = request.get_json() or {}
    for f in ("name","type","level"):
        if f in data:
            setattr(p, f, data[f])
    db.session.commit()
    return {"id":p.id, "name":p.name, "type":p.type, "level":p.level}

@main_bp.delete("/pokedex/<int:pid>")
def delete_pokemon(pid):
    p = Pokemon.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return "", 204
