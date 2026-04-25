from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection
from datetime import datetime

lotes_bp = Blueprint("lotes", __name__)


def generar_codigo_lote():
    conn = get_db_connection()
    total = conn.execute("SELECT COUNT(*) AS total FROM lotes").fetchone()["total"] + 1
    conn.close()
    return f"LP-2026-{total:04d}"


@lotes_bp.route("/lotes", methods=["GET", "POST"])
def lotes():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()

    if request.method == "POST":
        productor_id = request.form["productor_id"]
        centro_id = request.form["centro_id"]
        volumen_litros = request.form["volumen_litros"]
        responsable_recepcion = request.form["responsable_recepcion"]

        codigo_lote = generar_codigo_lote()
        fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        estado_lote = "Pendiente de análisis"

        conn.execute("""
            INSERT INTO lotes
            (codigo_lote, fecha_registro, volumen_litros, estado_lote, productor_id, centro_id, responsable_recepcion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            codigo_lote,
            fecha_registro,
            volumen_litros,
            estado_lote,
            productor_id,
            centro_id,
            responsable_recepcion
        ))

        conn.commit()
        conn.close()

        flash(f"Lote {codigo_lote} registrado correctamente.", "success")
        return redirect(url_for("lotes.lotes"))

    productores = conn.execute("""
        SELECT *
        FROM productores
        WHERE estado = 'Activo'
        ORDER BY nombre
    """).fetchall()

    centros = conn.execute("""
        SELECT *
        FROM centros_acopio
        WHERE estado = 'Activo'
        ORDER BY nombre
    """).fetchall()

    lista_lotes = conn.execute("""
        SELECT l.id, l.codigo_lote, l.fecha_registro, l.volumen_litros, 
               l.estado_lote, l.responsable_recepcion,
               p.nombre AS productor, c.nombre AS centro
        FROM lotes l
        INNER JOIN productores p ON l.productor_id = p.id
        INNER JOIN centros_acopio c ON l.centro_id = c.id
        ORDER BY l.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "lotes.html",
        productores=productores,
        centros=centros,
        lista_lotes=lista_lotes
    )


@lotes_bp.route("/trazabilidad", methods=["GET", "POST"])
def trazabilidad():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()

    lotes = conn.execute("""
        SELECT id, codigo_lote
        FROM lotes
        ORDER BY id DESC
    """).fetchall()

    lote_info = None
    calidad_info = None
    produccion_info = None
    inventario_info = None
    distribucion_info = []
    alertas_info = []

    if request.method == "POST":
        lote_id = request.form["lote_id"]

        lote_info = conn.execute("""
            SELECT l.*, p.nombre AS productor, c.nombre AS centro
            FROM lotes l
            INNER JOIN productores p ON l.productor_id = p.id
            INNER JOIN centros_acopio c ON l.centro_id = c.id
            WHERE l.id = ?
        """, (lote_id,)).fetchone()

        calidad_info = conn.execute("""
            SELECT *
            FROM analisis_calidad
            WHERE lote_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (lote_id,)).fetchone()

        produccion_info = conn.execute("""
            SELECT *
            FROM produccion
            WHERE lote_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (lote_id,)).fetchone()

        alertas_info = conn.execute("""
            SELECT *
            FROM alertas
            WHERE lote_id = ?
            ORDER BY id DESC
        """, (lote_id,)).fetchall()

        codigo_lote = lote_info["codigo_lote"] if lote_info else None

        if codigo_lote:
            origen_lote = f"Lote {codigo_lote}"

            inventario_info = conn.execute("""
                SELECT *
                FROM inventario
                WHERE origen = ?
                ORDER BY id DESC
                LIMIT 1
            """, (origen_lote,)).fetchone()

            distribucion_info = conn.execute("""
                SELECT *
                FROM distribucion
                WHERE origen_lote = ?
                ORDER BY id DESC
            """, (origen_lote,)).fetchall()

    conn.close()

    return render_template(
        "trazabilidad.html",
        lotes=lotes,
        lote_info=lote_info,
        calidad_info=calidad_info,
        produccion_info=produccion_info,
        inventario_info=inventario_info,
        distribucion_info=distribucion_info,
        alertas_info=alertas_info
    )