# Sistema de Peritagem Técnica — KGF Hidráulicos e Pneumáticos

Aplicação web desenvolvida em **Python (Flask)** para geração automatizada de **Relatórios (Laudos) de Peritagem Técnica em PDF** da **KGF Hidráulicos e Pneumáticos**.

O sistema permite que peritos preencham os dados da Ordem de Serviço (OS) pelo computador ou celular, adicionem múltiplos componentes inspecionados com fotos (direto da câmera ou galeria) e gerem um documento PDF padronizado, que é baixado imediatamente e **arquivado automaticamente na pasta correspondente da OS em `/mnt/fotos-servidor`**.

---

## Sumário

1. [Funcionalidades Principais](#funcionalidades-principais)
2. [Arquitetura e Estrutura de Diretórios](#arquitetura-e-estrutura-de-diretórios)
3. [Integração com `/mnt/fotos-servidor`](#integração-com-mntfotos-servidor)
4. [Execução com Docker (Recomendado)](#execução-com-docker-recomendado)
5. [Execução Local (Desenvolvimento)](#execução-local-desenvolvimento)
6. [Variáveis de Ambiente](#variáveis-de-ambiente)
7. [Endpoints da Aplicação](#endpoints-da-aplicação)

---

## Funcionalidades Principais

- **Formulário Dinâmico e Responsivo**:
  - Cadastro de metadados da peritagem: *Cliente*, *Equipamento*, *Ordem de Serviço (OS)*, *Nota Fiscal (NF)*, *Pedido de Compra* e *Perito Responsável*.
  - Adição e remoção dinâmica de múltiplos componentes (*Nome*, *Dimensionamento*, *Avaria*, *Serviço a Executar* e múltiplas *Fotos*).
- **Padronização Automática de Imagens (`Pillow`)**:
  - Correção automática de rotação EXIF de fotos tiradas por dispositivos móveis.
  - Recorte centralizado na proporção quadrada (`1:1`), redimensionamento para `600x600px` (`LANCZOS`) e compressão otimizada em JPEG.
  - Limpeza automática das imagens temporárias (`uploads/`) após a geração do PDF.
- **Geração de PDF Institucional (`fpdf2`)**:
  - Layout com identidade visual KGF®, cabeçalho técnico, blocos em duas colunas (descrições técnicas à esquerda e grade de fotos 2xN à direita) e paginação automática.
- **Arquivamento Automático no Servidor de Fotos (`/mnt/fotos-servidor`)**:
  - Localiza a pasta da OS dentro das pastas anuais (`Fotos 2026/<OS>`, `Fotos 2025/<OS>`, etc.) e copia automaticamente o PDF gerado (`Laudo_OS_<OS>.pdf`).

---

## Arquitetura e Estrutura de Diretórios

```text
/opt/projeto_peritagem/
├── app/
│   ├── __init__.py            # Application Factory (create_app)
│   ├── config.py              # Configurações centralizadas e variáveis de ambiente
│   ├── routes.py              # Rotas HTTP (Blueprint) e fluxo de requisição
│   ├── services/
│   │   ├── image_service.py   # Tratamento, EXIF e crop 1:1 de imagens (Pillow)
│   │   ├── pdf_service.py     # Template ModernPDF e geração do relatório (fpdf2)
│   │   └── storage_service.py # Busca O(1) da pasta da OS e cópia segura para /mnt/fotos-servidor
│   ├── static/
│   │   ├── css/style.css      # Folha de estilos da interface
│   │   └── js/form.js         # Manipulação dinâmica de componentes e fotos no DOM
│   └── templates/
│       └── formulario.html    # Template HTML principal
├── laudos/                    # Cópia local dos PDFs gerados (persistido via volume)
├── uploads/                   # Diretório temporário para processamento de fotos
├── app.py                     # Ponto de entrada WSGI (Gunicorn / Flask)
├── Dockerfile                 # Definição da imagem Docker (Python 3.12-slim + Gunicorn)
├── docker-compose.yml         # Orquestração do container e mapeamento de volumes
└── requirements.txt           # Dependências Python do projeto
```

---

## Integração com `/mnt/fotos-servidor`

O serviço `app/services/storage_service.py` localiza a pasta da Ordem de Serviço informada no campo **OS** do formulário seguindo estas regras:

1. **Busca Direta O(1) por Ano**:
   - Identifica as pastas anuais no nível superior de `/mnt/fotos-servidor` (ex.: `Fotos 2026`, `Fotos 2025`, `Fotos 2024`), ordenadas do ano mais recente para o mais antigo.
   - Verifica diretamente se existe o diretório `/mnt/fotos-servidor/Fotos <ANO>/<OS>` sem varrer subpastas desnecessariamente via rede CIFS/SMB.
2. **Operação Estritamente Não-Destrutiva**:
   - O sistema **nunca** exclui, move ou renomeia pastas ou arquivos existentes em `/mnt/fotos-servidor`.
   - Apenas copia o arquivo `Laudo_OS_<OS>.pdf` para dentro da pasta da OS encontrada.
   - Caso a pasta da OS ainda não exista no servidor de fotos, o PDF continua sendo salvo localmente em `./laudos/` e enviado normalmente ao navegador do perito.

---

## Execução com Docker (Recomendado)

### Pré-requisitos
- **Docker** e **Docker Compose** instalados.
- Compartilhamento `/mnt/fotos-servidor` montado no host.

### Subir o container em segundo plano
```bash
cd /opt/projeto_peritagem
docker compose up -d --build
```

### Verificar status e logs
```bash
docker compose ps
docker compose logs -f peritagem-web
```

A aplicação estará disponível em:
- **URL Local**: `http://localhost:5000`
- **Na Rede Local**: `http://<IP-DO-SERVIDOR>:5000`

### Parar o container
```bash
docker compose down
```

---

## Execução Local (Desenvolvimento)

Caso deseje executar fora do Docker em um ambiente virtual Python:

```bash
cd /opt/projeto_peritagem
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
FLASK_DEBUG=true python app.py
```

---

## Variáveis de Ambiente

| Variável | Padrão | Descrição |
| :--- | :--- | :--- |
| `FOTOS_SERVIDOR_DIR` | `/mnt/fotos-servidor` | Caminho onde as pastas anuais de OS estão montadas |
| `LAUDO_FOLDER` | `/app/laudos` (ou `./laudos`) | Diretório local de armazenamento dos PDFs gerados |
| `UPLOAD_FOLDER` | `/app/uploads` (ou `./uploads`) | Diretório temporário para recorte das fotos enviadas |
| `MAX_CONTENT_LENGTH` | `33554432` (32 MB) | Tamanho máximo permitido por envio de formulário |
| `IMAGE_TARGET_SIZE` | `600` | Resolução final (`px`) do recorte quadrado (`1:1`) das fotos |
| `IMAGE_JPEG_QUALITY` | `85` | Qualidade JPEG (`1-100`) das fotos processadas |

---

## Endpoints da Aplicação

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/` | Renderiza o formulário web de peritagem técnica |
| `POST` | `/salvar` | Processa os dados e imagens, gera o PDF, arquiva em `/mnt/fotos-servidor` e retorna o arquivo |
| `GET` | `/health` | Retorna `{"status": "ok"}` (HTTP 200) para monitoramento do container |

