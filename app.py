from flask import Flask, render_template, request, send_file
import os
from fpdf import FPDF
from datetime import datetime
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
LAUDO_FOLDER = 'laudos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LAUDO_FOLDER, exist_ok=True)

def tratar_imagem_quadrada(caminho_origem, tamanho=600):
    """Corta a imagem em 1:1 centralizado e redimensiona."""
    try:
        img = Image.open(caminho_origem)
        # Converte para RGB caso seja PNG/outro
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        largura, altura = img.size
        novo_lado = min(largura, altura)
        
        esquerda = (largura - novo_lado) / 2
        topo = (altura - novo_lado) / 2
        direita = (largura + novo_lado) / 2
        base = (altura + novo_lado) / 2
        
        img = img.crop((esquerda, topo, direita, base))
        img = img.resize((tamanho, tamanho), Image.LANCZOS)
        img.save(caminho_origem, "JPEG", quality=85)
    except Exception as e:
        print(f"Erro ao processar imagem {caminho_origem}: {e}")

class ModernPDF(FPDF):
    def header(self):
        # Barra lateral azul
        self.set_fill_color(0, 51, 102)
        self.rect(0, 0, 8, 297, 'F') 
        
        # --- LOGOTIPO KGF DESENHADO ---
        self.set_xy(150, 8) # Posiciona o logo no canto superior direito
        self.set_font('Arial', 'B', 22)
        self.set_text_color(0, 51, 102)
        self.cell(20, 10, 'KGF', ln=False)
        
        # Símbolo de Marca Registrada (R) Circular
        self.set_font('Arial', 'B', 6)
        # Desenha o círculo (x, y, largura, altura)
        self.ellipse(171, 9, 4, 4) 
        self.set_xy(171, 8.5)
        self.cell(4, 5, 'R', align='C')
        
        # Subtítulo do Logo
        self.set_xy(150, 17)
        self.set_font('Arial', '', 7)
        self.set_text_color(100, 100, 100)
        self.cell(40, 5, 'HIDRÁULICOS E PNEUMÁTICOS', ln=True)

        # Título Principal do Relatório (alinhado à esquerda)
        self.set_xy(12, 10)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, 'RELATÓRIO DE PERITAGEM TÉCNICA', ln=True)
        
        # Linha decorativa
        self.set_draw_color(0, 51, 102)
        self.line(22, 25, 200, 25)
        self.ln(12)

@app.route('/')
def index():
    return render_template('formulario.html')

@app.route('/salvar', methods=['POST'])
def salvar_laudo():
    try:
        # Coleta de dados do cabeçalho
        os_num = request.form.get('os')
        cliente = request.form.get('cliente', '')
        equipamento = request.form.get('descricao', '')
        nf = request.form.get('nf', '')
        pedido = request.form.get('pedido_compra', '')
        perito = request.form.get('perito', '')
        data_atual = datetime.now().strftime("%d/%m/%Y")

        # Coleta de listas
        nomes = request.form.getlist('comp_nome[]')
        dimensoes = request.form.getlist('comp_dim[]')
        avarias = request.form.getlist('comp_avaria[]')
        servicos = request.form.getlist('comp_servico[]')

        pdf = ModernPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        
        # --- RENDERIZAÇÃO DO CABEÇALHO NO PDF ---
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(12)
        pdf.cell(0, 8, f" CLIENTE: {cliente.upper()}", ln=True, fill=True)
        
        pdf.set_font("Arial", size=9)
        pdf.cell(12)
        pdf.cell(90, 7, f" OS: {os_num} | EQUIPAMENTO: {equipamento}", border='B')
        pdf.cell(0, 7, f" DATA: {data_atual}", border='B', ln=True, align='R')
        
        pdf.cell(12)
        pdf.cell(60, 7, f" NF: {nf}", border='B')
        pdf.cell(60, 7, f" PEDIDO: {pedido}", border='B')
        pdf.cell(0, 7, f" PERITO: {perito}", border='B', ln=True)
        pdf.ln(8)

        # --- LOOP DE COMPONENTES ---
        for i in range(len(nomes)):
            # Verifica espaço para novo componente
            if pdf.get_y() > 230:
                pdf.add_page()

            # Título do Componente
            pdf.set_font("Arial", 'B', 11)
            pdf.set_fill_color(0, 51, 102)
            pdf.set_text_color(255)
            pdf.cell(12)
            pdf.cell(0, 8, f" COMPONENTE: {nomes[i].upper()}", ln=True, fill=True)
            pdf.ln(2)
            pdf.set_text_color(0)

            y_inicial = pdf.get_y()
            col_texto_x = 22
            col_foto_x = 112
            larg_coluna = 85
            tam_foto = 42 # Tamanho 1:1

            # --- TEXTOS (ESQUERDA) ---
            pdf.set_font("Arial", 'B', 9)
            pdf.set_xy(col_texto_x, y_inicial)
            pdf.cell(larg_coluna, 5, "DIMENSIONAMENTO:", ln=True)
            pdf.set_font("Arial", size=9)
            pdf.set_x(col_texto_x)
            pdf.multi_cell(larg_coluna, 4, dimensoes[i])
            
            pdf.ln(2)
            pdf.set_font("Arial", 'B', 9)
            pdf.set_x(col_texto_x)
            pdf.cell(larg_coluna, 5, "AVARIA:", ln=True)
            pdf.set_font("Arial", size=9); pdf.set_text_color(180, 0, 0)
            pdf.set_x(col_texto_x)
            pdf.multi_cell(larg_coluna, 4, avarias[i])
            
            pdf.ln(2)
            pdf.set_font("Arial", 'B', 9); pdf.set_text_color(0)
            pdf.set_x(col_texto_x)
            pdf.cell(larg_coluna, 5, "SERVIÇO A EXECUTAR:", ln=True)
            pdf.set_font("Arial", size=9)
            pdf.set_x(col_texto_x)
            pdf.multi_cell(larg_coluna, 4, servicos[i])
            
            y_final_texto = pdf.get_y()

            # --- FOTOS (DIREITA) ---
            fotos_enviadas = request.files.getlist(f'comp_foto_{i+1}[]')
            y_foto_corrente = y_inicial
            x_foto_corrente = col_foto_x
            fotos_na_linha = 0
            
            for idx_f, foto in enumerate(fotos_enviadas):
                if foto and foto.filename != '':
                    nome_foto = f"img_{os_num}_{i}_{idx_f}.jpg"
                    caminho = os.path.join(UPLOAD_FOLDER, nome_foto)
                    foto.save(caminho)
                    tratar_imagem_quadrada(caminho)

                    # Quebra de página para foto
                    if y_foto_corrente > 250:
                        pdf.add_page()
                        y_foto_corrente = 30
                        x_foto_corrente = col_foto_x

                    pdf.image(caminho, x=x_foto_corrente, y=y_foto_corrente, w=tam_foto, h=tam_foto)
                    
                    fotos_na_linha += 1
                    if fotos_na_linha == 1:
                        x_foto_corrente += tam_foto + 2 # Lado a lado
                    else:
                        x_foto_corrente = col_foto_x
                        y_foto_corrente += tam_foto + 2 # Próxima linha de fotos
                        fotos_na_linha = 0

            y_final_fotos = y_foto_corrente + (tam_foto if fotos_na_linha > 0 else 0)
            
            # --- FINALIZAÇÃO DO BLOCO ---
            y_proximo = max(y_final_texto, y_final_fotos) + 10
            pdf.set_y(y_proximo)
            
            # Linha divisória fina
            pdf.set_draw_color(220, 220, 220)
            pdf.set_x(22)
            pdf.cell(178, 0, border='T', ln=True)
            pdf.ln(4)

        # Gerar arquivo
        nome_pdf = f"Laudo_OS_{os_num}.pdf"
        caminho_pdf = os.path.join(LAUDO_FOLDER, nome_pdf)
        pdf.output(caminho_pdf)
        return send_file(caminho_pdf)

    except Exception as e:
        return f"Erro Crítico: {str(e)}"

if __name__ == '__main__':
    # Rodar em 0.0.0.0 permite acesso pelo IP da máquina no Wi-Fi
    app.run(host='0.0.0.0', port=5000, debug=True)