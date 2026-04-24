from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM usuarios WHERE usuario = ? AND password = ? AND estado = 'Activo'",
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

    conn.close()

    return render_template(
        "dashboard.html",
        total_lotes=total_lotes,
        aprobados=aprobados,
        rechazados=rechazados,
        procesados=procesados,
        alertas=alertas_activas,
        inventario_total=inventario_total
    )


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))