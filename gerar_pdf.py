# -*- coding: utf-8 -*-


from pathlib import Path
import sys
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image, KeepTogether
)
from reportlab.lib.utils import ImageReader

# Dados do trabalho
ALUNO = "Giovana Alice"
RU = "4536546"
CLIENTE_NOME = "GiovanaAlice4536546"
CLIENTE_ID = 2
PRODUTO_NOME = "Baozi de Carne"
PRODUTO_PRECO = "8.50"
PRODUTO_ID = 1
PEDIDO_ID = 1
QUANTIDADE = 3
DATA_CADASTRO = "2020-01-11"  

BASE_DIR = Path(__file__).resolve().parent
PASTA_PRINTS = BASE_DIR / "prints"
REPO = sys.argv[1] if len(sys.argv) > 1 else ""
SAIDA = BASE_DIR / f"Trabalho_Baozi_Store_GiovanaAlice_{RU}.pdf"

AZUL = colors.HexColor("#0B2A5B")
DOURADO = colors.HexColor("#E0A526")
CINZA = colors.HexColor("#F3F5FA")
VERMELHO = colors.HexColor("#B42318")

styles = getSampleStyleSheet()
TITULO = ParagraphStyle(
    "TituloCustom", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=19, leading=24, textColor=AZUL, spaceAfter=8
)
H1 = ParagraphStyle(
    "SecaoCustom", parent=styles["Heading1"], fontName="Helvetica-Bold",
    fontSize=15, leading=19, textColor=AZUL, spaceBefore=5, spaceAfter=8
)
H2 = ParagraphStyle(
    "SubsecaoCustom", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=11, leading=14, textColor=AZUL, spaceBefore=7, spaceAfter=4
)
BODY = ParagraphStyle(
    "CorpoCustom", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=9.5, leading=14, alignment=TA_LEFT, spaceAfter=5
)
SMALL = ParagraphStyle(
    "PequenoCustom", parent=BODY, fontSize=8.5, leading=11,
    textColor=colors.HexColor("#444444")
)
CELL = ParagraphStyle("CelulaCustom", parent=BODY, fontSize=8.5, leading=11)
CELL_HEAD = ParagraphStyle(
    "CelulaCabecalho", parent=CELL, fontName="Helvetica-Bold",
    textColor=colors.white
)

def para(text, style=BODY):
    return Paragraph(text, style)

def tabela(data, widths):
    rows = []
    for r, row in enumerate(data):
        rows.append([
            Paragraph(str(value), CELL_HEAD if r == 0 else CELL)
            for value in row
        ])
    table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8B8B8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CINZA]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table

PRINTS = [
    ("POST /clientes", "Cadastro do cliente."),
    ("POST /produtos", "Cadastro do produto."),
    ("POST /pedidos", "Cadastro do pedido relacionado ao cliente e ao produto."),
    ("GET /clientes", "Lista os clientes cadastrados."),
    ("GET /produtos", "Lista os produtos cadastrados."),
    ("GET /pedidos", "Lista os pedidos cadastrados."),
    (f"GET /clientes/{CLIENTE_ID}", "Consulta o cliente pelo ID."),
    (f"GET /produtos/{PRODUTO_ID}", "Consulta o produto pelo ID."),
    (f"GET /pedidos/{PEDIDO_ID}", "Consulta o pedido pelo ID."),
    (f"DELETE /pedidos/{PEDIDO_ID}", "Exclusão do pedido."),
    (f"DELETE /clientes/{CLIENTE_ID}", "Exclusão do cliente."),
    (f"DELETE /produtos/{PRODUTO_ID}", "Exclusão do produto."),
]

def rodape(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(DOURADO)
    canvas.setLineWidth(1.5)
    canvas.line(2 * cm, 1.55 * cm, A4[0] - 2 * cm, 1.55 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawString(2 * cm, 1.05 * cm, "Desenvolvimento Web Back-End — Baozi Store")
    canvas.drawRightString(A4[0] - 2 * cm, 1.05 * cm, f"{ALUNO} — RU {RU} — pág. {doc.page}")
    canvas.restoreState()

def get_images():
    if not PASTA_PRINTS.exists():
        return []
    extensions = {".png", ".jpg", ".jpeg", ".webp"}
    return sorted(
        [p for p in PASTA_PRINTS.iterdir() if p.is_file() and p.suffix.lower() in extensions],
        key=lambda p: p.name.lower()
    )

def add_screenshot(story, index, title, caption, image_path):
    content = [para(f"{index:02d}. {escape(title)}", H2), para(escape(caption), SMALL)]
    if image_path:
        iw, ih = ImageReader(str(image_path)).getSize()
        max_w, max_h = 16 * cm, 11 * cm
        scale = min(max_w / iw, max_h / ih)
        content.append(Image(str(image_path), width=iw * scale, height=ih * scale))
        content.append(Spacer(1, 8))
    else:
        warning = Table([[para(
            f"<b>PRINT NÃO ENCONTRADO</b><br/>Esperado o print da requisição {index:02d}. "
            "Coloque a imagem na pasta prints/ e gere o PDF novamente.", CELL
        )]], colWidths=[16 * cm], rowHeights=[2.2 * cm])
        warning.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, VERMELHO),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF3F3")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        content.extend([warning, Spacer(1, 8)])
    story.append(KeepTogether(content))

def montar():
    doc = SimpleDocTemplate(
        str(SAIDA), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.8 * cm, bottomMargin=2 * cm,
        title=f"Trabalho Baozi Store — {ALUNO}", author=ALUNO
    )
    story = []
    story.append(para("TRABALHO DE DESENVOLVIMENTO WEB BACK-END", TITULO))
    story.append(para("API REST — Baozi Store", ParagraphStyle(
        "Subtitulo", parent=BODY, fontSize=13, leading=17,
        textColor=DOURADO, fontName="Helvetica-Bold"
    )))
    story.append(Spacer(1, 8))
    story.append(tabela([
        ["Campo", "Informação"],
        ["Aluna", ALUNO],
        ["RU", RU],
        ["Disciplina", "Desenvolvimento Web Back-End"],
        ["Tecnologias", "Java, Spring Boot, Spring Data JPA, banco H2 e Postman"],
    ], [4 * cm, 13 * cm]))
    story.append(Spacer(1, 12))

    story.append(para("1. Descrição da situação fictícia", H1))
    story.append(para(
        f"A <b>Baozi Store</b> é uma loja fictícia que comercializa pão chinês. "
        f"Para organizar as operações, a API REST permite cadastrar e consultar clientes, "
        f"produtos e pedidos, além de excluir registros."
    ))
    story.append(para(
        f"Nos testes realizados, foi utilizado o cliente <b>{escape(CLIENTE_NOME)}</b>, "
        f"o produto <b>{escape(PRODUTO_NOME)}</b>, com preço de R$ {PRODUTO_PRECO}, "
        f"e um pedido de <b>{QUANTIDADE} unidades</b>."
    ))
    story.append(tabela([
        ["Elemento", "Dados utilizados"],
        ["Cliente", f"Nome: {CLIENTE_NOME}; ID atual: {CLIENTE_ID}; data retornada pela API: {DATA_CADASTRO}"],
        ["Produto", f"Nome: {PRODUTO_NOME}; ID: {PRODUTO_ID}; preço: R$ {PRODUTO_PRECO}; estoque: true"],
        ["Pedido", f"ID: {PEDIDO_ID}; cliente ID {CLIENTE_ID}; produto ID {PRODUTO_ID}; quantidade: {QUANTIDADE}"],
    ], [3.5 * cm, 13.5 * cm]))

    story.append(PageBreak())
    story.append(para("2. Diagrama de casos de uso", H1))
    story.append(para(
        "O usuário interage com a API para cadastrar, listar, consultar por identificador e excluir "
        "clientes, produtos e pedidos. Essas operações correspondem às funções CRUD disponibilizadas "
        "pelos endpoints REST."
    ))
    story.append(tabela([
        ["Recurso", "Operações"],
        ["Cliente", "POST /clientes; GET /clientes; GET /clientes/{id}; DELETE /clientes/{id}"],
        ["Produto", "POST /produtos; GET /produtos; GET /produtos/{id}; DELETE /produtos/{id}"],
        ["Pedido", "POST /pedidos; GET /pedidos; GET /pedidos/{id}; DELETE /pedidos/{id}"],
    ], [3 * cm, 14 * cm]))

    story.append(PageBreak())
    story.append(para("3. Especificação da API", H1))
    story.append(para("3.1 Recursos e campos utilizados", H2))
    story.append(tabela([
        ["Recurso", "Campos principais"],
        ["Cliente", "id (identificador), nome, clienteDesde (data de cadastro)"],
        ["Produto", "id (identificador), nome, preco, estoque"],
        ["Pedido", "id (identificador), cliente, produto, quantidade"],
    ], [3.5 * cm, 13.5 * cm]))
    story.append(Spacer(1, 8))
    story.append(para("3.2 Endpoints testados", H2))
    endpoint_rows = [["Método", "Endpoint", "Finalidade"]]
    for title, caption in PRINTS:
        endpoint_rows.append([title.split(" ")[0], title.split(" ", 1)[1], caption])
    story.append(tabela(endpoint_rows, [2.2 * cm, 5.5 * cm, 9.3 * cm]))
    story.append(Spacer(1, 8))
    story.append(para("3.3 Exemplos de requisições POST", H2))
    story.append(tabela([
        ["Endpoint", "Corpo JSON"],
        ["POST /clientes", f'{{ "nome": "{CLIENTE_NOME}", "clienteDesde": "{DATA_CADASTRO}" }}'],
        ["POST /produtos", f'{{ "nome": "{PRODUTO_NOME}", "preco": {PRODUTO_PRECO}, "estoque": true }}'],
        ["POST /pedidos", f'{{ "cliente": {{ "id": {CLIENTE_ID} }}, "produto": {{ "id": {PRODUTO_ID} }}, "quantidade": {QUANTIDADE} }}'],
    ], [3.5 * cm, 13.5 * cm]))

    story.append(PageBreak())
    story.append(para("4. Evidências dos testes no Postman", H1))
    story.append(para(
        
    ))
    images = get_images()
    for i, (title, caption) in enumerate(PRINTS, start=1):
        img = images[i - 1] if i <= len(images) else None
        add_screenshot(story, i, title, caption, img)

    story.append(PageBreak())
    story.append(para("5. Repositório do código-fonte", H1))
    if REPO:
        safe_repo = escape(REPO)
        story.append(para(f'<link href="{safe_repo}" color="blue">{safe_repo}</link>', BODY))
    else:
        story.append(para("Link do repositório não informado.", BODY))

    doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
    print(f"PDF gerado: {SAIDA}")
    print(f"Imagens encontradas: {len(images)} de 12")
    if len(images) < 12:
        print("Atenção: coloque menos de 12 imagens.")
    elif len(images) > 12:
        print("Atenção:mais de 12 imagens.")

if __name__ == "__main__":
    montar()
