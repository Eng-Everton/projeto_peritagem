"""Rotas HTTP da aplicação de Peritagem Técnica KGF."""

from datetime import datetime
import logging
import os
import uuid
from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
    send_file,
)

from app.services.image_service import tratar_imagem_quadrada
from app.services.pdf_service import (
    ComponenteLaudo,
    DadosLaudo,
    gerar_pdf_laudo,
)
from app.services.storage_service import (
    sanitizar_identificador_os,
    salvar_pdf_no_servidor,
)

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET"])
def index():
    """Exibe o formulário web para preenchimento do laudo de peritagem."""
    return render_template("formulario.html")


@main_bp.route("/health", methods=["GET"])
def health():
    """Endpoint de verificação de saúde para monitoramento e Docker healthcheck."""
    return jsonify({"status": "ok"}), 200


@main_bp.route("/salvar", methods=["POST"])
def salvar_laudo():
    """
    Recebe os dados do formulário e fotos dos componentes, gera o relatório PDF,
    salva localmente em `laudos/`, copia para a pasta da OS em `/mnt/fotos-servidor`
    (se encontrada) e retorna o PDF ao navegador.
    """
    arquivos_temporarios: list[str] = []

    try:
        os_bruta = request.form.get("os", "").strip()
        os_segura = sanitizar_identificador_os(os_bruta) or "SEM_OS"

        cliente = request.form.get("cliente", "").strip()
        equipamento = request.form.get("descricao", "").strip()
        nf = request.form.get("nf", "").strip()
        pedido = request.form.get("pedido_compra", "").strip()
        perito = request.form.get("perito", "").strip()
        data_atual = datetime.now().strftime("%d/%m/%Y")

        nomes = request.form.getlist("comp_nome[]")
        dimensoes = request.form.getlist("comp_dim[]")
        avarias = request.form.getlist("comp_avaria[]")
        servicos = request.form.getlist("comp_servico[]")

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        laudo_folder = current_app.config["LAUDO_FOLDER"]
        fotos_servidor_dir = current_app.config["FOTOS_SERVIDOR_DIR"]
        tamanho_img = current_app.config.get("IMAGE_TARGET_SIZE", 600)
        qualidade_img = current_app.config.get("IMAGE_JPEG_QUALITY", 85)

        os.makedirs(upload_folder, exist_ok=True)
        os.makedirs(laudo_folder, exist_ok=True)

        req_uid = uuid.uuid4().hex[:8]
        componentes: list[ComponenteLaudo] = []

        for i, nome_comp in enumerate(nomes):
            dim_comp = dimensoes[i] if i < len(dimensoes) else ""
            avaria_comp = avarias[i] if i < len(avarias) else ""
            servico_comp = servicos[i] if i < len(servicos) else ""

            fotos_enviadas = request.files.getlist(f"comp_foto_{i + 1}[]")
            caminhos_fotos_comp: list[str] = []

            for idx_f, foto in enumerate(fotos_enviadas):
                if foto and foto.filename and foto.filename.strip() != "":
                    nome_foto = f"img_{os_segura}_{req_uid}_{i}_{idx_f}.jpg"
                    caminho_foto = os.path.join(upload_folder, nome_foto)
                    foto.save(caminho_foto)
                    arquivos_temporarios.append(caminho_foto)

                    if tratar_imagem_quadrada(
                        caminho_foto,
                        tamanho=tamanho_img,
                        qualidade=qualidade_img,
                    ):
                        caminhos_fotos_comp.append(caminho_foto)

            componentes.append(
                ComponenteLaudo(
                    nome=nome_comp,
                    dimensionamento=dim_comp,
                    avaria=avaria_comp,
                    servico=servico_comp,
                    caminhos_fotos=caminhos_fotos_comp,
                )
            )

        dados_laudo = DadosLaudo(
            os_num=os_bruta or os_segura,
            cliente=cliente,
            equipamento=equipamento,
            nf=nf,
            pedido=pedido,
            perito=perito,
            data_atual=data_atual,
            componentes=componentes,
        )

        nome_pdf = f"Laudo_OS_{os_segura}.pdf"
        caminho_pdf = os.path.join(laudo_folder, nome_pdf)

        gerar_pdf_laudo(dados_laudo, caminho_pdf)

        # Salva cópia do PDF na pasta correspondente da OS em /mnt/fotos-servidor
        caminho_servidor = salvar_pdf_no_servidor(
            caminho_pdf_local=caminho_pdf,
            os_num=os_bruta or os_segura,
            base_dir=fotos_servidor_dir,
        )
        if caminho_servidor:
            logger.info("Laudo arquivado no servidor: %s", caminho_servidor)

        return send_file(
            caminho_pdf,
            mimetype="application/pdf",
            as_attachment=False,
            download_name=nome_pdf,
        )

    except Exception as exc:
        logger.exception("Erro crítico ao gerar o laudo de peritagem")
        return f"Erro Crítico ao gerar laudo: {str(exc)}", 500

    finally:
        # Remove apenas os arquivos temporários de upload da requisição atual
        for temp_path in arquivos_temporarios:
            try:
                if os.path.isfile(temp_path):
                    os.remove(temp_path)
            except OSError as err:
                logger.warning(
                    "Não foi possível remover arquivo temporário '%s': %s",
                    temp_path,
                    err,
                )

