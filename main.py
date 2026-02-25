import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Seven Dwarfs - PDV", layout="wide")

# --- 1. INICIALIZAÇÃO DE ESTADOS (Sempre no topo) ---
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
        "Seven Dwarfs a verdadeira delícia gelada
