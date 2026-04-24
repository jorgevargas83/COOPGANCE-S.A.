from flask import Flask, redirect, url_for, session
from database import init_db

from routes.auth_routes import auth_bp
from routes.lotes_routes import lotes_bp
from routes.calidad_routes import calidad_bp
from routes.produccion_routes import produccion_bp
from routes.inventario_routes import inventario_bp
from routes.distribucion_routes import distribucion_bp
from routes.alertas_routes import alertas_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = "coopgance_secret_key"

    init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(lotes_bp)
    app.register_blueprint(calidad_bp)
    app.register_blueprint(produccion_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(distribucion_bp)
    app.register_blueprint(alertas_bp)

    @app.route("/")
    def index():
        if "usuario_id" in session:
            return redirect(url_for("auth.dashboard"))
        return redirect(url_for("auth.login"))

    return app


app = create_app()

# Necesario para Vercel
application = app

if __name__ == "__main__":
    app.run(debug=True)