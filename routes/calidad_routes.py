from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection
from datetime import datetime

calidad_bp = Blueprint("calidad", __name__)


def crear_alerta(lote_id, tipo_alerta, descripcion):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO alertas (lote_id, tipo_alerta, descripcion, fecha_alerta, estado)
        VALUES (?, ?, ?, ?, ?)
    """, (
        lote_id,
        tipo_alerta,
        descripcion,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Activa"
    ))
    conn.commit()
    conn.close()


@calidad_bp.route("/calidad", methods=["GET", "POST"])
def calidad():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()

    if request.method == "POST":
        lote_id = request.form["lote_id"]
        temperatura = float(request.form["temperatura"])
        olor = request.form["olor"]
        color = request.form["color"]
        acidez = float(request.form["acidez"])
        densidad = float(request.form["densidad"])
        prueba_alcohol = request.form["prueba_alcohol"]

        aprobado = True

        if not (2 <= temperatura <= 6):
            aprobado = False
        if olor != "Normal":
            aprobado = False
        if color != "Blanco uniforme":
            aprobado = False
        if not (0.13 <= acidez <= 0.17):
            aprobado = False
        if not (1.028 <= densidad <= 1.034):
            aprobado = False
        if prueba_alcohol != "Negativa":
            aprobado = False

        resultado = "Aprobado" if aprobado else "Rechazado"

        conn.execute("""
            INSERT INTO analisis_calidad
            (lote_id, temperatura, olor, color, acidez, densidad, prueba_alcohol, resultado, fecha_analisis)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lote_id,
            temperatura,
            olor,
            color,
            acidez,
            densidad,
            prueba_alcohol,
            resultado,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.execute("""
            UPDATE lotes
            SET estado_lote = ?
            WHERE id = ?
        """, (resultado, lote_id))

        conn.commit()
        conn.close()

        if resultado == "Rechazado":
            crear_alerta(
                lote_id,
                "Lote rechazado",
                "El lote no cumplió con los parámetros establecidos en el análisis de calidad."
            )

        flash(f"Análisis registrado correctamente. Resultado: {resultado}", "success")
        return redirect(url_for("calidad.calidad"))

    lotes_pendientes = conn.execute("""
        SELECT * FROM lotes
        WHERE estado_lote = 'Pendiente de análisis'
        ORDER BY id DESC
    """).fetchall()

    historial = conn.execute("""
        SELECT a.*, l.codigo_lote
        FROM analisis_calidad a
        INNER JOIN lotes l ON a.lote_id = l.id
        ORDER BY a.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "calidad.html",
        lotes_pendientes=lotes_pendientes,
        historial=historial
    )