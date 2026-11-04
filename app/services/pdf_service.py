"""Serviço de geração de Relatórios de Peritagem Técnica em PDF (FPDF2)."""

from dataclasses import dataclass, field
import os
from fpdf import FPDF


@dataclass
class ComponenteLaudo:
    """Representa um componente inspecionado no laudo técnico."""

    nome: str
    dimensionamento: str = ""
    avaria: str = ""
    servico: str = ""
    caminhos_fotos: list[str] = field(default_factory=list)


@dataclass
class DadosLaudo:
    """Estrutura de dados completa para geração do relatório de peritagem."""

    os_num: str
    cliente: str
    equipamento: str
    nf: str
    pedido: str
    perito: str
    data_atual: str
    componentes: list[ComponenteLaudo] = field(default_factory=list)


def sanitizar_texto_pdf(texto: str) -> str:
    """
    Normaliza caracteres especiais Unicode para equivalentes compatíveis com
    a codificação 'latin-1' utilizada pelas fontes nativas do FPDF.
    """
    if not texto:
        return ""
    substituicoes = {
        "\u2013": "-",  # en-dash
        "\u2014": "-",  # em-dash
        "\u2018": "'",  # left single quote
        "\u2019": "'",  # right single quote
        "\u201c": '"',  # left double quote
        "\u201d": '"',  # right double quote
        "\u2022": "*",  # bullet
        "\u2026": "...",  # ellipsis
        "\u2205": "Diam.",  # empty set / diameter symbol
    }
    for orig, dest in substituicoes.items():
        texto = texto.replace(orig, dest)
    return texto.encode("latin-1", errors="replace").decode("latin-1")


class ModernPDF(FPDF):
    """Template PDF institucional da KGF Hidráulicos e Pneumáticos."""

    def header(self) -> None:
        # Barra lateral azul institucional
        self.set_fill_color(0, 51, 102)
        self.rect(0, 0, 8, 297, "F")

        # --- LOGOTIPO KGF DESENHADO ---
        self.set_xy(150, 8)
        self.set_font("Arial", "B", 22)
        self.set_text_color(0, 51, 102)
        self.cell(20, 10, "KGF", ln=False)

        # Símbolo de Marca Registrada (R) Circular
        self.set_font("Arial", "B", 6)
        self.ellipse(171, 9, 4, 4)
        self.set_xy(171, 8.5)
        self.cell(4, 5, "R", align="C")

        # Subtítulo do Logo
        self.set_xy(150, 17)
        self.set_font("Arial", "", 7)
        self.set_text_color(100, 100, 100)
        self.cell(
            40,
            5,
            sanitizar_texto_pdf("HIDRÁULICOS E PNEUMÁTICOS"),
            ln=True,
        )

        # Título Principal do Relatório (alinhado à esquerda)
        self.set_xy(12, 10)
        self.set_font("Arial", "B", 14)
        self.set_text_color(0, 51, 102)
        self.cell(
            0,
            10,
            sanitizar_texto_pdf("RELATÓRIO DE PERITAGEM TÉCNICA"),
            ln=True,
        )

        # Linha decorativa
        self.set_draw_color(0, 51, 102)
        self.line(22, 25, 200, 25)
        self.ln(12)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_x(22)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(
            0,
            10,
            sanitizar_texto_pdf(f"Página {self.page_no()}/{{nb}}"),
            align="R",
        )


def gerar_pdf_laudo(dados: DadosLaudo, caminho_saida: str) -> str:
    """
    Gera o arquivo PDF do laudo técnico a partir dos dados informados.

    Args:
        dados: Objeto `DadosLaudo` contendo cabeçalho e lista de componentes.
        caminho_saida: Caminho completo onde o arquivo PDF será gravado.

    Returns:
        O caminho do arquivo PDF gerado.
    """
    pdf = ModernPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # --- RENDERIZAÇÃO DO CABEÇALHO DO CLIENTE / OS NO PDF ---
    cliente_txt = sanitizar_texto_pdf(dados.cliente.upper())
    os_txt = sanitizar_texto_pdf(dados.os_num)
    equip_txt = sanitizar_texto_pdf(dados.equipamento)
    data_txt = sanitizar_texto_pdf(dados.data_atual)
    nf_txt = sanitizar_texto_pdf(dados.nf)
    pedido_txt = sanitizar_texto_pdf(dados.pedido)
    perito_txt = sanitizar_texto_pdf(dados.perito)

    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(12)
    pdf.cell(0, 8, f" CLIENTE: {cliente_txt}", ln=True, fill=True)

    pdf.set_font("Arial", size=9)
    pdf.cell(12)
    pdf.cell(90, 7, f" OS: {os_txt} | EQUIPAMENTO: {equip_txt}", border="B")
    pdf.cell(0, 7, f" DATA: {data_txt}", border="B", ln=True, align="R")

    pdf.cell(12)
    pdf.cell(60, 7, f" NF: {nf_txt}", border="B")
    pdf.cell(60, 7, f" PEDIDO: {pedido_txt}", border="B")
    pdf.cell(0, 7, f" PERITO: {perito_txt}", border="B", ln=True)
    pdf.ln(8)

    # --- LOOP DE COMPONENTES ---
    col_texto_x = 22
    col_foto_x = 112
    larg_coluna = 85
    tam_foto = 42  # Tamanho 1:1 em mm

    for comp in dados.componentes:
        if pdf.get_y() > 225:
            pdf.add_page()

        # Título do Componente
        nome_comp = sanitizar_texto_pdf(comp.nome.upper())
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(12)
        pdf.cell(0, 8, f" COMPONENTE: {nome_comp}", ln=True, fill=True)
        pdf.ln(2)
        pdf.set_text_color(0, 0, 0)

        pagina_inicial = pdf.page_no()
        y_inicial = pdf.get_y()

        # --- TEXTOS (COLUNA ESQUERDA) ---
        pdf.set_font("Arial", "B", 9)
        pdf.set_xy(col_texto_x, y_inicial)
        pdf.cell(larg_coluna, 5, "DIMENSIONAMENTO:", ln=True)
        pdf.set_font("Arial", size=9)
        pdf.set_x(col_texto_x)
        pdf.multi_cell(
            larg_coluna, 4, sanitizar_texto_pdf(comp.dimensionamento)
        )

        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.set_x(col_texto_x)
        pdf.cell(larg_coluna, 5, "AVARIA:", ln=True)
        pdf.set_font("Arial", size=9)
        pdf.set_text_color(180, 0, 0)
        pdf.set_x(col_texto_x)
        pdf.multi_cell(larg_coluna, 4, sanitizar_texto_pdf(comp.avaria))

        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.set_text_color(0, 0, 0)
        pdf.set_x(col_texto_x)
        pdf.cell(
            larg_coluna,
            5,
            sanitizar_texto_pdf("SERVIÇO A EXECUTAR:"),
            ln=True,
        )
        pdf.set_font("Arial", size=9)
        pdf.set_x(col_texto_x)
        pdf.multi_cell(larg_coluna, 4, sanitizar_texto_pdf(comp.servico))

        pagina_final_texto = pdf.page_no()
        y_final_texto = pdf.get_y()

        # --- FOTOS (COLUNA DIREITA) ---
        # Se o texto quebrou de página, posiciona fotos a partir do topo da página atual
        if pagina_final_texto > pagina_inicial:
            y_foto_corrente = 30.0
        else:
            y_foto_corrente = y_inicial

        x_foto_corrente = col_foto_x
        fotos_na_linha = 0

        for caminho_foto in comp.caminhos_fotos:
            if not os.path.isfile(caminho_foto):
                continue

            if y_foto_corrente + tam_foto > 275:
                pdf.add_page()
                y_foto_corrente = 30.0
                x_foto_corrente = col_foto_x
                fotos_na_linha = 0

            pdf.image(
                caminho_foto,
                x=x_foto_corrente,
                y=y_foto_corrente,
                w=tam_foto,
                h=tam_foto,
            )

            fotos_na_linha += 1
            if fotos_na_linha == 1:
                x_foto_corrente += tam_foto + 2
            else:
                x_foto_corrente = col_foto_x
                y_foto_corrente += tam_foto + 2
                fotos_na_linha = 0

        pagina_final_fotos = pdf.page_no()
        y_final_fotos = y_foto_corrente + (
            tam_foto if fotos_na_linha > 0 else 0
        )

        # --- FINALIZAÇÃO DO BLOCO ---
        if pagina_final_fotos > pagina_final_texto:
            y_proximo = y_final_fotos + 8
        elif pagina_final_texto > pagina_final_fotos:
            y_proximo = y_final_texto + 8
        else:
            y_proximo = max(y_final_texto, y_final_fotos) + 8

        if y_proximo > 270:
            pdf.add_page()
        else:
            pdf.set_y(y_proximo)

        # Linha divisória fina
        pdf.set_draw_color(220, 220, 220)
        pdf.set_x(col_texto_x)
        pdf.cell(178, 0, border="T", ln=True)
        pdf.ln(4)

    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    pdf.output(caminho_saida)
    return caminho_saida

