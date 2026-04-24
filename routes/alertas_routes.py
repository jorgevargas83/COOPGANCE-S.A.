from flask import Blueprint, render_template, redirect, url_for, session
from database import get_db_connection

alertas_bp = Blueprint("alertas", __name__)


@alertas_bp.route("/alertas")
def alertas():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()

    lista_alertas = conn.execute("""
        SELECT a.*, l.codigo_lote
        FROM alertas a
        LEFT JOIN lotes l ON a.lote_id = l.id
        ORDER BY a.id DESC
    """).fetchall()

    conn.close()

    return render_template("alertas.html", lista_alertas=lista_alertas)