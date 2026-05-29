from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection

calidad_bp = Blueprint("calidad", __name__)


def crear_alerta(conn, lote_id, tipo_alerta, descripcion):
    conn.execute("""
        INSERT INTO alertas (lote_id, tipo_alerta, descripcion, fecha_alerta, estado)
        VALUES (%s, %s, %s, NOW(), 'Activa')
    """, (lote_id, tipo_alerta, descripcion))


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
        responsable_calidad = request.form["responsable_calidad"]
        observaciones = request.form.get("observaciones", "")

        # Tomamos centro_acopio del formulario si existe.
        # Si no existe, queda vacío para evitar error.
        centro_acopio = request.form.get("centro_acopio", "")

        aprobado = (
            2 <= temperatura <= 6 and
            olor == "Normal" and
            color == "Blanco uniforme" and
            0.13 <= acidez <= 0.17 and
            1.028 <= densidad <= 1.034 and
            prueba_alcohol == "Negativa"
        )

        resultado = "Aprobado" if aprobado else "Rechazado"

        motivo = ""

        if not aprobado:
            motivos = []

            if not (2 <= temperatura <= 6):
                motivos.append(f"Temp {temperatura}C fuera de rango")

            if acidez < 0.13 or acidez > 0.17:
                motivos.append(f"Acidez {acidez} fuera de rango")

            if densidad < 1.028 or densidad > 1.034:
                motivos.append(f"Densidad {densidad} fuera de rango")

            if prueba_alcohol != "Negativa":
                motivos.append("Alcohol positivo")

            if olor != "Normal":
                motivos.append("Olor anormal")

            if color != "Blanco uniforme":
                motivos.append("Color alterado")

            motivo = ". ".join(motivos)

        conn.execute("""
            INSERT INTO analisis_calidad
            (lote_id, temperatura, olor, color, acidez, densidad, prueba_alcohol,
             resultado, fecha_analisis, responsable_calidad, observaciones,
             motivo_rechazo, centro_acopio)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s)
        """, (
            lote_id, temperatura, olor, color, acidez, densidad,
            prueba_alcohol, resultado, responsable_calidad, observaciones,
            motivo, centro_acopio
        ))

        conn.execute(
            "UPDATE lotes SET estado_lote = %s WHERE id = %s", (resultado, lote_id)
        )

        if resultado == "Rechazado":
            lote = conn.execute(
                "SELECT codigo_lote FROM lotes WHERE id = %s", (lote_id,)
            ).fetchone()

            crear_alerta(
                conn,
                lote_id,
                "Lote rechazado",
                f"Lote {lote['codigo_lote']} rechazado: {motivo}."
            )

        conn.commit()
        conn.close()

        flash(f"Análisis registrado. Resultado: {resultado}", "success" if aprobado else "danger")
        return redirect(url_for("calidad.calidad"))

    lotes_pendientes = conn.execute(
        "SELECT * FROM lotes WHERE estado_lote = 'Pendiente de análisis' ORDER BY id DESC"
    ).fetchall()

    historial = conn.execute("""
        SELECT a.*, l.codigo_lote
        FROM analisis_calidad a
        INNER JOIN lotes l ON a.lote_id = l.id
        ORDER BY a.id DESC
    """).fetchall()

    conn.close()
    return render_template("calidad.html", lotes_pendientes=lotes_pendientes, historial=historial)