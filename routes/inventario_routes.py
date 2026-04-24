from flask import Blueprint, render_template, redirect, url_for, session
from database import get_db_connection

inventario_bp = Blueprint("inventario", __name__)


@inventario_bp.route("/inventario")
def inventario():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()

    inventario_lista = conn.execute("""
        SELECT *
        FROM inventario
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "inventario.html",
        inventario_lista=inventario_lista
    )