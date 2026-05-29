from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection

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

        producto = conn.execute(
            "SELECT * FROM inventario WHERE id = %s", (inventario_id,)
        ).fetchone()

        if not producto:
            flash("Producto no encontrado en inventario.", "danger")
            conn.close()
            return redirect(url_for("distribucion.distribucion"))

        if cantidad > producto["cantidad"]:
            flash(f"Cantidad ({cantidad}) supera el stock disponible ({producto['cantidad']}).", "danger")
            conn.close()
            return redirect(url_for("distribucion.distribucion"))

        conn.execute("""
            INSERT INTO distribucion
            (cliente, producto, presentacion, cantidad, fecha_salida, responsable, inventario_id, origen_lote, estado)
            VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s, 'Entregado')
        """, (cliente, producto["producto"], producto["presentacion"], cantidad,
              responsable, inventario_id, producto["origen"]))

        nueva_cantidad = producto["cantidad"] - cantidad
        nuevo_estado = "Agotado" if nueva_cantidad == 0 else "En almacén"

        conn.execute(
            "UPDATE inventario SET cantidad = %s, estado = %s WHERE id = %s",
            (nueva_cantidad, nuevo_estado, inventario_id)
        )

        # Marcar lote como distribuido si inventario agotado
        if nueva_cantidad == 0 and producto["lote_id"]:
            conn.execute(
                "UPDATE lotes SET estado_lote = 'Distribuido' WHERE id = %s AND estado_lote = 'Procesado'",
                (producto["lote_id"],)
            )

        conn.commit()
        conn.close()

        flash("Despacho registrado correctamente.", "success")
        return redirect(url_for("distribucion.distribucion"))

    inventario_lista = conn.execute(
        "SELECT * FROM inventario WHERE cantidad > 0 AND estado != 'Agotado' ORDER BY producto, presentacion"
    ).fetchall()

    historial = conn.execute(
        "SELECT * FROM distribucion ORDER BY id DESC"
    ).fetchall()

    conn.close()
    return render_template("distribucion.html", inventario_lista=inventario_lista, historial=historial)
