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

        estado = "Procesado"

        # guardar producción
        conn.execute("""
            INSERT INTO produccion (lote_id, temperatura_proceso, tiempo_proceso, fecha_produccion, estado)
            VALUES (?, ?, ?, ?, ?)
        """, (
            lote_id,
            temperatura,
            tiempo,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            estado
        ))

        # obtener volumen del lote
        lote = conn.execute("SELECT volumen_litros FROM lotes WHERE id = ?", (lote_id,)).fetchone()

        # convertir litros → botellas de 1L
        cantidad_botellas = int(lote["volumen_litros"])

        # guardar en inventario
        conn.execute("""
            INSERT INTO inventario (producto, cantidad, fecha_registro, origen)
            VALUES (?, ?, ?, ?)
        """, (
            "Leche Pasteurizada 1L",
            cantidad_botellas,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Producción"
        ))

        # actualizar estado del lote
        conn.execute("""
            UPDATE lotes
            SET estado_lote = 'Procesado'
            WHERE id = ?
        """, (lote_id,))

        conn.commit()
        conn.close()

        flash("Producción registrada y enviada a inventario.", "success")
        return redirect(url_for("produccion.produccion"))

    # SOLO LOTES APROBADOS
    lotes_aprobados = conn.execute("""
        SELECT * FROM lotes
        WHERE estado_lote = 'Aprobado'
        ORDER BY id DESC
    """).fetchall()

    historial = conn.execute("""
        SELECT p.*, l.codigo_lote
        FROM produccion p
        INNER JOIN lotes l ON p.lote_id = l.id
        ORDER BY p.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "produccion.html",
        lotes_aprobados=lotes_aprobados,
        historial=historial
    )