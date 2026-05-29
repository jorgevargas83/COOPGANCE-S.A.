from flask import Blueprint, render_template, redirect, url_for, session, flash
from database import get_db_connection

alertas_bp = Blueprint("alertas", __name__)


@alertas_bp.route("/alertas")
def alertas():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    lista_alertas = conn.execute("""
        SELECT a.*, l.codigo_lote
        FROM alertas a
        LEFT JOIN lotes l ON a.lote_id = l.id
        ORDER BY 
            CASE a.estado WHEN 'Activa' THEN 0 WHEN 'En revisión' THEN 1 ELSE 2 END,
            a.fecha_alerta DESC
    """).fetchall()
    conn.close()

    return render_template("alertas.html", lista_alertas=lista_alertas)


@alertas_bp.route("/resolver_alerta/<int:id>", methods=["POST"])
def resolver_alerta(id):
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    conn.execute("UPDATE alertas SET estado = 'Resuelta' WHERE id = %s", (id,))
    conn.commit()
    conn.close()

    flash("Alerta marcada como resuelta.", "success")
    return redirect(url_for("alertas.alertas"))
