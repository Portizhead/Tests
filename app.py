from flask import Flask, request, jsonify, Response
import sqlite3
from pathlib import Path

app = Flask(__name__)
#----------- EndPoint para el webcheck -------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok"), 200


# ---------- Suma (tu endpoint existente) ----------
def suma(a, b):
    return a + b

@app.get("/")
def home():
    return 'API: usa /suma?a=2&b=3 o /pokedex/ui', 200

@app.get("/suma")
def suma_endpoint():
    try:
        a = float(request.args.get("a")) if request.args.get("a") is not None else None
        b = float(request.args.get("b")) if request.args.get("b") is not None else None
    except ValueError:
        return jsonify(error="Parámetros no numéricos"), 400

    if a is None or b is None:
        return jsonify(error="Faltan parámetros a y b (numéricos)"), 400

    return jsonify(resultado=suma(a, b)), 200


# ---------- Pokédex (v1) ----------
DB_PATH = Path("pokedex.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_schema():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pokemon (
              id   INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT UNIQUE NOT NULL,
              type TEXT,
              hp   INTEGER
            );
        """)

ensure_schema()

@app.get("/pokedex")
def list_pokemon():
    with get_conn() as conn:
        rows = conn.execute("SELECT id, name, type, hp FROM pokemon ORDER BY id").fetchall()
        data = [dict(r) for r in rows]
        return jsonify(data), 200

@app.post("/pokedex")
def create_pokemon():
    body = request.get_json(silent=True) or {}
    name = (body.get("name") or "").strip()
    ptype = (body.get("type") or "").strip()
    hp = body.get("hp")

    if not name:
        return jsonify(error="name es requerido"), 400
    try:
        hp = int(hp) if hp is not None else None
    except ValueError:
        return jsonify(error="hp debe ser entero"), 400

    try:
        with get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO pokemon(name, type, hp) VALUES(?,?,?)",
                (name, ptype or None, hp)
            )
            new_id = cur.lastrowid
            row = conn.execute("SELECT id, name, type, hp FROM pokemon WHERE id = ?", (new_id,)).fetchone()
            return jsonify(dict(row)), 201
    except sqlite3.IntegrityError:
        return jsonify(error="name ya existe"), 409

@app.get("/pokedex/<int:pid>")
def get_pokemon(pid):
    with get_conn() as conn:
        row = conn.execute("SELECT id, name, type, hp FROM pokemon WHERE id = ?", (pid,)).fetchone()
        if not row:
            return jsonify(error="no encontrado"), 404
        return jsonify(dict(row)), 200

@app.delete("/pokedex/<int:pid>")
def delete_pokemon(pid):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM pokemon WHERE id = ?", (pid,))
        if cur.rowcount == 0:
            return jsonify(error="no encontrado"), 404
        return Response(status=204)

# Mini UI
@app.get("/pokedex/ui")
def pokedex_ui():
    html = """
<!doctype html>
<meta charset="utf-8" />
<title>Pokédex v1</title>
<h1>Pokédex</h1>
<form id="f">
  <input name="name" placeholder="Name" required />
  <input name="type" placeholder="Type (e.g., Fire)" />
  <input name="hp" type="number" placeholder="HP" />
  <button type="submit">Añadir</button>
</form>
<pre id="out"></pre>
<script>
async function load() {
  const r = await fetch('/pokedex');
  const j = await r.json();
  document.getElementById('out').textContent = JSON.stringify(j, null, 2);
}
document.getElementById('f').addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const body = {
    name: form.get('name'),
    type: form.get('type'),
    hp: form.get('hp') ? Number(form.get('hp')) : null
  };
  const r = await fetch('/pokedex', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
  if(!r.ok){ alert('Error: '+(await r.text())); return; }
  e.target.reset();
  load();
});
load();
</script>
"""
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
