from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from database import get_db_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.before_app_request
def load_alertas_count():
    """Inyecta el conteo de alertas activas en todas las vistas."""
    if "usuario_id" in session:
        try:
            conn = get_db_connection()
            result = conn.execute(
                "SELECT COUNT(*) AS total FROM alertas WHERE estado = 'Activa'"
            ).fetchone()
            conn.close()
            g.alertas_count = result["total"] if result else 0
        except Exception:
            g.alertas_count = 0
    else:
        g.alertas_count = 0


@auth_bp.context_processor
def inject_alertas():
    return {"alertas_count": getattr(g, "alertas_count", 0)}


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM usuarios WHERE usuario = %s AND password = %s AND estado = 'Activo'",
            (usuario, password)
        ).fetchone()
        conn.close()

        if user:
            session["usuario_id"] = user["id"]
            session["nombre"] = user["nombre"]
            session["rol"] = user["rol"]
            return redirect(url_for("auth.dashboard"))
        else:
            flash("Usuario o contraseña incorrectos", "danger")

    return render_template("login.html")


@auth_bp.route("/dashboard")
def dashboard():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()

    total_lotes = conn.execute("SELECT COUNT(*) AS total FROM lotes").fetchone()["total"]
    aprobados = conn.execute("SELECT COUNT(*) AS total FROM lotes WHERE estado_lote = 'Aprobado'").fetchone()["total"]
    rechazados = conn.execute("SELECT COUNT(*) AS total FROM lotes WHERE estado_lote = 'Rechazado'").fetchone()["total"]
    procesados = conn.execute("SELECT COUNT(*) AS total FROM lotes WHERE estado_lote = 'Procesado'").fetchone()["total"]
    alertas_activas = conn.execute("SELECT COUNT(*) AS total FROM alertas WHERE estado = 'Activa'").fetchone()["total"]
    inventario_total = conn.execute("SELECT COALESCE(SUM(cantidad),0) AS total FROM inventario").fetchone()["total"]
    volumen_total = conn.execute("SELECT COALESCE(SUM(volumen_litros),0) AS total FROM lotes").fetchone()["total"]

    # Volumen por mes (últimos 6 meses)
    volumen_meses = conn.execute("""
        SELECT TO_CHAR(fecha_registro::date, 'Mon') AS mes,
               SUM(volumen_litros) AS total
        FROM lotes
        WHERE fecha_registro >= NOW() - INTERVAL '6 months'
        GROUP BY DATE_TRUNC('month', fecha_registro::date), mes
        ORDER BY DATE_TRUNC('month', fecha_registro::date)
        LIMIT 6
    """).fetchall()

    # Top clientes
    top_clientes = conn.execute("""
        SELECT cliente, SUM(cantidad) AS total
        FROM distribucion
        GROUP BY cliente
        ORDER BY total DESC
        LIMIT 5
    """).fetchall()

    # Últimas alertas
    ultimas_alertas = conn.execute("""
        SELECT * FROM alertas ORDER BY fecha_alerta DESC LIMIT 5
    """).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_lotes=total_lotes,
        aprobados=aprobados,
        rechazados=rechazados,
        procesados=procesados,
        alertas=alertas_activas,
        inventario_total=inventario_total,
        volumen_total=volumen_total,
        volumen_meses=volumen_meses,
        top_clientes=top_clientes,
        ultimas_alertas=ultimas_alertas,
    )


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
