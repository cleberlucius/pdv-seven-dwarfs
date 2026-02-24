import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Seven Dwarfs - PDV", layout="wide")

# --- FUNÇÃO PARA GERAR A FICHA (LAYOUT BLINDADO) ---
def gerar_ficha_imagem(sabor, id_venda, pagto):
    largura = 300
    altura_estimada = 1000
    img = Image.new('RGB', (largura, altura_estimada), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    def get_font(size):
        font_paths = ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 
                      "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 
                      "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"]
        for path in font_paths:
            if os.path.exists(path): return ImageFont.truetype(path, size)
        return ImageFont.load_default()

    y = 30
    # 1. Logo
    logo_file = "logo.png"
    if os.path.exists(logo_file):
        try:
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((110, 110))
            img.paste(logo, ((largura - logo.size[0]) // 2, y), logo)
            y += logo.size[1] + 20
        except: y += 10

    # 2. Sabor com Redução Automática para caber em 1 linha
    draw.line([(15, y), (285, y)], fill=(0,0,0), width=5)
    y += 50
    
    # Lógica de redução: começa em 90 e desce até caber na largura de 280px
    font_size = 90
    msg_sabor = sabor.upper()
    while font_size > 20:
        f_temp = get_font(font_size)
        bbox = draw.textbbox((0, 0), msg_sabor, font=f_temp)
        if (bbox[2] - bbox[0]) < 270: # Margem de segurança
            break
        font_size -= 5
    
    f_sabor = get_font(font_size)
    draw.text((largura/2, y), msg_sabor, fill=(0,0,0), font=f_sabor, anchor="mm")
    
    y += 50
    draw.line([(15, y), (285, y)], fill=(0,0,0), width=5)
    y += 50

    # 3. Informações de Venda
    f_info = get_font(26)
    draw.text((largura/2, y), f"VENDA ID: {str(id_venda)[-5:]}", fill=(0,0,0), font=f_info, anchor="mm")
    y += 35
    draw.text((largura/2, y), f"PAGTO: {pagto.upper()}", fill=(0,0,0), font=f_info, anchor="mm")
    
    y += 70 # Espaço maior antes do rodapé

    # 4. Rodapé Fixo (Tamanho 14 para garantir que não quebre linha)
    f_rodape = get_font(14)
    data_str = datetime.now().strftime("%d/%m/%Y - %H:%M")
    
    linhas_rodape = [
        f"Emitido em: {data_str}",
        "Válido apenas na data de emissão",
        "Seven Dwarfs: A verdadeira delícia gelada",
        "BEBA COM MODERAÇÃO",
        "------------------------------------------"
    ]

    for linha in linhas_rodape:
        draw.text((largura/2, y), linha.upper(), fill=(0,0,0), font=f_rodape, anchor="mm")
        y += 22

    # Corta a imagem no ponto exato
    return img.crop((0, 0, largura, y + 20))

# --- INICIALIZAÇÃO ---
if 'vendas' not in st.session_state: st.session_state.vendas = []
if 'sangrias' not in st.session_state: st.session_state.sangrias = []
if 'cardapio' not in st.session_state: st.session_state.cardapio = {}
if 'caixa_inicial' not in st.session_state: st.session_state.caixa_inicial = 0.0
if 'configurado' not in st.session_state: st.session_state.configurado = False
if 'fichas_pendentes' not in st.session_state: st.session_state.fichas_pendentes = []
if 'carrinho' not in st.session_state: st.session_state.carrinho = {}
if 'show_dinheiro' not in st.session_state: st.session_state.show_dinheiro = False
if 'show_desconto' not in st.session_state: st.session_state.show_desconto = False

st.markdown("""<style>div.stButton > button { height: 5em; font-size: 16px; font-weight: bold; border-radius: 10px; }</style>""", unsafe_allow_html=True)

# --- TELA CONFIG / EDIÇÃO ---
if not st.session_state.configurado:
    st.title("⚙️ Configuração Cardápio")
    v_ini = st.number_input("Troco Inicial (R$):", min_value=0.0, format="%.2f", value=st.session_state.caixa_inicial if st.session_state.caixa_inicial > 0 else None, placeholder="0.00")
    opcoes = ["Pilsen", "IPA", "Vinho", "Weiss", "Black", "Água", "Refrigerante"]
    selec = st.multiselect("Sabores Ativos:", opcoes, default=list(st.session_state.cardapio.keys()) if st.session_state.cardapio else ["Pilsen", "IPA"])
    temp_card = {}
    for s in selec:
        p_val = st.session_state.cardapio.get(s, None)
        temp_card[s] = st.number_input(f"Preço {s}:", min_value=0.0, format="%.2f", key=f"p_{s}", value=p_val, placeholder="0.00")
    
    if st.button("SALVAR E ABRIR VENDAS", type="primary", use_container_width=True):
        if selec:
            st.session_state.caixa_inicial = v_ini if v_ini else 0.0
            st.session_state.cardapio = {k: (v if v else 0.0) for k, v in temp_card.items()}
            st.session_state.configurado = True
            st.rerun()
        else: st.error("Escolha um sabor.")
    st.stop()

# --- INTERFACE PDV ---
st.markdown(f"### 🍻 PDV Seven Dwarfs")
t1, t2, t3 = st.tabs(["🛒 VENDER", "🔄 ESTORNO", "📊 FECHAMENTO"])

with t1:
    cv, cc = st.columns([1.5, 1])
    with cv:
        cols = st.columns(2)
        for i, (n, p) in enumerate(st.session_state.cardapio.items()):
            if cols[i%2].button(f"{n}\nR$ {p:.2f}",
