from flask import Blueprint, render_template, redirect, url_for, session, request, flash
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
        WHERE cantidad > 0
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "inventario.html",
        inventario_lista=inventario_lista
    )


@inventario_bp.route("/mover_inventario/<int:id>", methods=["POST"])
def mover_inventario(id):
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    nueva_ubicacion = request.form["ubicacion"]

    if "Despacho" in nueva_ubicacion:
        nuevo_estado = "En despacho"
    else:
        nuevo_estado = "En almacén"

    conn = get_db_connection()

    conn.execute("""
        UPDATE inventario
        SET ubicacion = ?, estado = ?
        WHERE id = ?
    """, (nueva_ubicacion, nuevo_estado, id))

    conn.commit()
    conn.close()

    flash("Ubicación actualizada correctamente.", "success")
    return redirect(url_for("inventario.inventario"))