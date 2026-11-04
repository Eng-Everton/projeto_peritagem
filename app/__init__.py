"""Pacote principal da aplicação web de Peritagem Técnica KGF."""

import logging
import os
from flask import Flask

from app.config import Config


def create_app(config_class: type[Config] = Config) -> Flask:
    """Factory de criação e configuração da instância Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configuração básica de logs
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Garante que os diretórios locais de trabalho existam
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["LAUDO_FOLDER"], exist_ok=True)

    # Registro de rotas (Blueprint)
    from app.routes import main_bp

    app.register_blueprint(main_bp)

    return app

