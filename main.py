import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Seven Dwarfs - PDV", layout="wide")

# --- 1. INICIALIZAÇÃO DE ESTADOS ---
if 'vendas' not in st.session_state: st.session_state.vendas = []
if 'sangrias' not in st.session_state: st.session_state.sangrias = []
if 'fichas_pendentes' not in st.session_state: st.session_state.fichas_pendentes = []
if 'cardapio' not in st.session_state: st.session_state.cardapio = {}
if 'caixa_inicial' not in st.session_state: st.session_state.caixa_inicial = 0.0
if 'configurado' not in st.session_state: st.session_state.configurado = False
if 'carrinho' not in st.session_state: st.session_state.carrinho = {}
if 'show_dinheiro' not in st.session_state: st.session_state.show_dinheiro = False
if 'show_desconto' not in st.session_state: st.session_state.show_desconto = False

# --- FUNÇÃO PARA GERAR A FICHA ---
def gerar_ficha_imagem(sabor, id_venda, pagto):
    largura = 300
    altura_estimada = 1200 
    img = Image.new('RGB', (largura, altura_estimada), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    def get_font(size, bold=True):
        if bold:
            paths = ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        else:
            paths = ["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        for path in paths:
            if os.path.exists(path): return ImageFont.truetype(path, size)
        return ImageFont.load_default()

    y = 30
    logo_file = "logo.png"
    if os.path.exists(logo_file):
        try:
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((110, 110))
            img.paste(logo, ((largura - logo.size[0]) // 2, y), logo)
            y += logo.size[1] + 20
        except: y += 10

    draw.line([(15, y), (285, y)], fill=(0,0,0), width=5)
    y += 50
    
    font_size = 85
    msg_sabor = str(sabor).upper()
    while font_size > 20:
        f_temp = get_font(font_size, bold=True)
        bbox = draw.textbbox((0, 0), msg_sabor, font=f_temp)
        if (bbox[2] - bbox[0]) < 265:
            break
        font_size -= 5
    
    draw.text((largura/2, y), msg_sabor, fill=(0,0,0), font=get_font(font_size, bold=True), anchor="mm")
    
    y += 50
    draw.line([(15, y), (285, y)], fill=(0,0,0), width=5)
    y += 50

    f_info = get_font(24, bold=True)
    draw.text((largura/2, y), f"VENDA ID: {str(id_venda)[-5:]}", fill=(0,0,0), font=f_info, anchor="mm")
    y += 35
    draw.text((largura/2, y), f"PAGAMENTO: {str(pagto).upper()}", fill=(0,0,0), font=f_info, anchor="mm")
    
    y += 60 

    f_rodape = get_font(14, bold=False)
    data_str = datetime.now().strftime("%d/%m/%Y - %H:%M")
    
    mensagens = [
        f"Emitido em: {data_str}",
        "Válido apenas na data de emissão durante o evento",
        "Seven Dwarfs a verdadeira delícia gelada",
        "BEBA COM MODERAÇÃO"
    ]

    for msg in mensagens:
        linhas = textwrap.wrap(msg.upper(), width=32)
        for linha in linhas:
            draw.text((largura/2, y), linha, fill=(0,0,0), font=f_rodape, anchor="mm")
            y += 20
        y += 4 

    draw.text((largura/2, y), "--------------------------------", fill=(0,0,0), font=f_rodape, anchor="mm")
    y += 20
    return img.crop((0, 0, largura, y + 10))

st.markdown("""<style>div.stButton > button { height: 5em; font-size: 16px; font-weight: bold; border-radius: 10px; }</style>""", unsafe_allow_html=True)

# --- TELA DE CONFIGURAÇÃO ---
if st.session_state.configurado == False:
    st.title("⚙️ Gestão de Cardápio Seven Dwarfs")
    v_ini = st.number_input("Troco Inicial (R$):", min_value=0.0, format="%.2f", value=st.session_state.caixa_inicial)
    
    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        opcoes_base = ["Pilsen", "IPA", "Black Jack", "Vinho", "Manga", "Morango"]
        default_base = [s for s in st.session_state.cardapio.keys() if s in opcoes_base]
        selec_base = st.multiselect("Sabores Fixos:", opcoes_base, default=default_base)
    
    with col_cfg2:
        extras_atuais_lista = [s for s in st.session_state.cardapio.keys() if s not in opcoes_base]
        extras_atuais_str = ", ".join(extras_atuais_lista)
        novos_extras = st.text_area("Adicionar Outros (Separe por vírgula):", 
                                   value=extras_atuais_str,
                                   placeholder="Ex: Água, Refrigerante, Suco")

    lista_extras = [s.strip() for s in novos_extras.split(",") if s.strip()]
    lista_total_config = []
    for item in (selec_base + lista_extras):
        if item not in lista_total_config:
            lista_total_config.append(item)
    
    st.write("---")
    st.subheader("Defina os Preços:")
    temp_card = {}
    
    if lista_total_config:
        cols_p = st.columns(3)
        for i, s in enumerate(lista_total_config):
            p_sugestao = st.session_state.cardapio.get(s, 0.0)
            temp_card[s] = cols
