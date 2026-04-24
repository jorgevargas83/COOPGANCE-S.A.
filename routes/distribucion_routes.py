from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection
from datetime import datetime

distribucion_bp = Blueprint("distribucion", __name__)


@distribucion_bp.route("/distribucion", methods=["GET", "POST"])
def distribucion():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()

    if request.method == "POST":
        inventario_id = request.form["inventario_id"]
        cliente = request.form["cliente"]
        cantidad = int(request.form["cantidad"])
        responsable = request.form["responsable"]

        producto = conn.execute("""
            SELECT * FROM inventario WHERE id = ?
        """, (inventario_id,)).fetchone()

        if not producto:
            flash("Producto no encontrado en inventario.", "danger")
            return redirect(url_for("distribucion.distribucion"))

        if cantidad > producto["cantidad"]:
            flash("La cantidad solicitada supera el inventario disponible.", "danger")
            return redirect(url_for("distribucion.distribucion"))

        conn.execute("""
            INSERT INTO distribucion (cliente, producto, cantidad, fecha_salida, responsable)
            VALUES (?, ?, ?, ?, ?)
        """, (
            cliente,
            producto["producto"],
            cantidad,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            responsable
        ))

        nueva_cantidad = producto["cantidad"] - cantidad

        conn.execute("""
            UPDATE inventario
            SET cantidad = ?
            WHERE id = ?
        """, (nueva_cantidad, inventario_id))

        conn.commit()
        conn.close()

        flash("Despacho registrado correctamente.", "success")
        return redirect(url_for("distribucion.distribucion"))

    inventario_lista = conn.execute("""
        SELECT * FROM inventario
        WHERE cantidad > 0
        ORDER BY id DESC
    """).fetchall()

    historial = conn.execute("""
        SELECT * FROM distribucion
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "distribucion.html",
        inventario_lista=inventario_lista,
        historial=historial
    )