from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection
from datetime import datetime

produccion_bp = Blueprint("produccion", __name__)


@produccion_bp.route("/produccion", methods=["GET", "POST"])
def produccion():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()

    if request.method == "POST":
        lote_id = request.form["lote_id"]
        temperatura = float(request.form["temperatura"])
        tiempo = int(request.form["tiempo"])
        responsable_produccion = request.form["responsable_produccion"]
        presentacion = request.form.get("presentacion", "1L")
        observaciones = request.form.get("observaciones", "")

        lote_data = conn.execute(
            "SELECT codigo_lote, volumen_litros FROM lotes WHERE id = %s", (lote_id,)
        ).fetchone()

        volumen = float(lote_data["volumen_litros"])

        # Campos nuevos para Power BI
        merma = round(volumen * 0.02, 2)
        litros_procesados = volumen
        rendimiento = 98.0

        # Calcular unidades según presentación
        if presentacion == "250ml":
            cantidad = int(volumen * 4)
        elif presentacion == "500ml":
            cantidad = int(volumen * 2)
        else:  # 1L
            cantidad = int(volumen)

        ubicacion = "Cámara Fría 1 - Rack A" if cantidad >= 3000 else "Cámara Fría 2 - Rack B"

        conn.execute("""
            INSERT INTO produccion
            (lote_id, temperatura_proceso, tiempo_proceso, fecha_produccion,
             estado, responsable_produccion, observaciones,
             litros_procesados, merma, rendimiento)
            VALUES (%s, %s, %s, NOW(), 'Completado', %s, %s, %s, %s, %s)
        """, (
            lote_id, temperatura, tiempo,
            responsable_produccion, observaciones,
            litros_procesados, merma, rendimiento
        ))

        conn.execute("""
            INSERT INTO inventario
            (producto, presentacion, cantidad, fecha_registro, origen, lote_id, ubicacion, estado)
            VALUES ('Leche Pasteurizada', %s, %s, NOW(), %s, %s, %s, 'En almacén')
        """, (presentacion, cantidad, f"Lote {lote_data['codigo_lote']}", lote_id, ubicacion))

        conn.execute(
            "UPDATE lotes SET estado_lote = 'Procesado' WHERE id = %s", (lote_id,)
        )

        conn.commit()
        conn.close()

        flash(f"Producción registrada. {cantidad} unidades ({presentacion}) enviadas a inventario.", "success")
        return redirect(url_for("produccion.produccion"))

    lotes_aprobados = conn.execute(
        "SELECT * FROM lotes WHERE estado_lote = 'Aprobado' ORDER BY id DESC"
    ).fetchall()

    historial = conn.execute("""
        SELECT p.*, l.codigo_lote
        FROM produccion p
        INNER JOIN lotes l ON p.lote_id = l.id
        ORDER BY p.id DESC
    """).fetchall()

    conn.close()
    return render_template("produccion.html", lotes_aprobados=lotes_aprobados, historial=historial)