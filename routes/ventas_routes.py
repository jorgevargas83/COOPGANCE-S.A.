from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection

ventas_bp = Blueprint("ventas", __name__)

# Costos por presentación (basados en plan de inversión COOPGANCE)
COSTOS = {
    '1L':    {'materia': 5.50, 'proceso': 0.85, 'empaque': 1.25, 'mano_obra': 1.62, 'transporte': 0.83, 'energia': 0.60, 'otros': 0.55, 'total': 11.20},
    '500ml': {'materia': 2.75, 'proceso': 0.50, 'empaque': 1.10, 'mano_obra': 0.95, 'transporte': 0.50, 'energia': 0.35, 'otros': 0.35, 'total': 6.50},
    '250ml': {'materia': 1.375,'proceso': 0.30, 'empaque': 0.95, 'mano_obra': 0.60, 'transporte': 0.32, 'energia': 0.22, 'otros': 0.22, 'total': 3.96},
}


@ventas_bp.route("/ventas", methods=["GET", "POST"])
def ventas():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()

    if request.method == "POST":
        cliente = request.form["cliente"]
        producto = request.form.get("producto", "Leche Pasteurizada")
        presentacion = request.form["presentacion"]
        cantidad = int(request.form["cantidad"])
        precio_unitario = float(request.form["precio_unitario"])
        metodo_pago = request.form["metodo_pago"]
        responsable = request.form["responsable"]
        nit_cliente = request.form.get("nit_cliente", "")
        observaciones = request.form.get("observaciones", "")
        distribucion_id = request.form.get("distribucion_id") or None

        c = COSTOS.get(presentacion, COSTOS['1L'])

        total_venta = round(cantidad * precio_unitario, 2)
        costo_materia = round(cantidad * c['materia'], 2)
        costo_proceso = round(cantidad * c['proceso'], 2)
        costo_empaque = round(cantidad * c['empaque'], 2)
        costo_mano_obra = round(cantidad * c['mano_obra'], 2)
        costo_transporte = round(cantidad * c['transporte'], 2)
        costo_energia = round(cantidad * c['energia'], 2)
        costo_otros = round(cantidad * c['otros'], 2)
        costo_unitario = c['total']
        costo_total = round(cantidad * costo_unitario, 2)
        ganancia_unitaria = round(precio_unitario - costo_unitario, 2)
        ganancia_total = round(total_venta - costo_total, 2)
        margen = round((ganancia_unitaria / precio_unitario) * 100, 2) if precio_unitario > 0 else 0

        if presentacion == '1L':
            pvl = precio_unitario
        elif presentacion == '500ml':
            pvl = precio_unitario / 0.5
        else:
            pvl = precio_unitario / 0.25

        if metodo_pago in ("Crédito 30 días", "Crédito 60 días"):
            estado = "Crédito"
        else:
            estado = "Completada"

        conn.execute("""
            INSERT INTO ventas
            (cliente, producto, presentacion, cantidad, precio_unitario, total,
             costo_materia_prima, costo_proceso, costo_empaque, costo_mano_obra,
             costo_transporte, costo_energia, costo_otros,
             costo_unitario, costo_total, precio_venta_litro,
             ganancia_unitaria, ganancia_total, margen_porcentaje,
             metodo_pago, estado, distribucion_id, fecha_venta, responsable, nit_cliente, observaciones)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),%s,%s,%s)
        """, (cliente, producto, presentacion, cantidad, precio_unitario, total_venta,
              costo_materia, costo_proceso, costo_empaque, costo_mano_obra,
              costo_transporte, costo_energia, costo_otros,
              costo_unitario, costo_total, pvl,
              ganancia_unitaria, ganancia_total, margen,
              metodo_pago, estado, distribucion_id, responsable, nit_cliente, observaciones))

        conn.commit()
        conn.close()
        flash(f"Venta registrada: Q {total_venta:,.2f} — Ganancia: Q {ganancia_total:,.2f} ({margen}%)", "success")
        return redirect(url_for("ventas.ventas"))

    # Historial
    historial = conn.execute("SELECT * FROM ventas ORDER BY fecha_venta DESC").fetchall()

    # KPIs
    totales = conn.execute("""
        SELECT
            COUNT(*) AS num_ventas,
            COALESCE(SUM(total), 0) AS ingresos,
            COALESCE(SUM(costo_total), 0) AS costos,
            COALESCE(SUM(ganancia_total), 0) AS ganancia,
            COALESCE(SUM(costo_materia_prima), 0) AS total_materia,
            COALESCE(SUM(costo_proceso), 0) AS total_proceso,
            COALESCE(SUM(costo_empaque), 0) AS total_empaque,
            COALESCE(SUM(costo_mano_obra), 0) AS total_mano_obra,
            COALESCE(SUM(costo_transporte), 0) AS total_transporte,
            COALESCE(SUM(costo_energia), 0) AS total_energia,
            COALESCE(SUM(costo_otros), 0) AS total_otros,
            COALESCE(SUM(CASE WHEN estado = 'Completada' THEN total ELSE 0 END), 0) AS cobrado,
            COALESCE(SUM(CASE WHEN estado IN ('Pendiente de pago','Crédito') THEN total ELSE 0 END), 0) AS pendiente,
            CASE WHEN SUM(total) > 0
                THEN ROUND((SUM(ganancia_total) / SUM(total)) * 100, 1)
                ELSE 0 END AS margen_global
        FROM ventas WHERE estado != 'Cancelada'
    """).fetchone()

    # Top clientes
    top_clientes = conn.execute("""
        SELECT cliente, SUM(total) AS total_ventas, SUM(ganancia_total) AS total_ganancia, COUNT(*) AS num_compras
        FROM ventas WHERE estado != 'Cancelada'
        GROUP BY cliente ORDER BY total_ventas DESC LIMIT 5
    """).fetchall()

    # Ventas por mes
    ventas_mes = conn.execute("""
        SELECT TO_CHAR(fecha_venta, 'Mon') AS mes,
               SUM(total) AS ingresos, SUM(costo_total) AS costos, SUM(ganancia_total) AS ganancia
        FROM ventas
        WHERE fecha_venta >= NOW() - INTERVAL '6 months' AND estado != 'Cancelada'
        GROUP BY DATE_TRUNC('month', fecha_venta), mes
        ORDER BY DATE_TRUNC('month', fecha_venta)
    """).fetchall()

    # Estructura de costos
    estructura_costos = conn.execute(
        "SELECT * FROM costos_produccion WHERE activo = TRUE ORDER BY costo_por_litro DESC"
    ).fetchall()

    # Distribuciones sin venta vinculada
    distribuciones = conn.execute("""
        SELECT d.id, d.cliente, d.producto, d.presentacion, d.cantidad, d.fecha_salida
        FROM distribucion d LEFT JOIN ventas v ON v.distribucion_id = d.id
        WHERE v.id IS NULL ORDER BY d.id DESC
    """).fetchall()

    conn.close()

    return render_template("ventas.html",
        historial=historial, totales=totales, top_clientes=top_clientes,
        ventas_mes=ventas_mes, distribuciones=distribuciones,
        estructura_costos=estructura_costos, costos_ref=COSTOS)


@ventas_bp.route("/marcar_pagada/<int:id>", methods=["POST"])
def marcar_pagada(id):
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))
    conn = get_db_connection()
    conn.execute("UPDATE ventas SET estado = 'Completada' WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    flash("Venta marcada como pagada.", "success")
    return redirect(url_for("ventas.ventas"))


@ventas_bp.route("/cancelar_venta/<int:id>", methods=["POST"])
def cancelar_venta(id):
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))
    conn = get_db_connection()
    conn.execute("UPDATE ventas SET estado = 'Cancelada' WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    flash("Venta cancelada.", "danger")
    return redirect(url_for("ventas.ventas"))