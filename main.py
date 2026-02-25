import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Seven Dwarfs PDV", layout="wide", initial_sidebar_state="collapsed")

# --- FUNÇÕES DE PERSISTÊNCIA (CSV) ---
def salvar_dados():
    df_vendas = pd.DataFrame(st.session_state.vendas)
    df_vendas.to_csv("vendas_backup.csv", index=False)
    
    df_vip = pd.DataFrame([{"nome": k, "valor": v} for k, v in st.session_state.contas_vip.items()])
    df_vip.to_csv("vips_backup.csv", index=False)

def carregar_dados():
    if os.path.exists("vendas_backup.csv"):
        st.session_state.vendas = pd.read_csv("vendas_backup.csv").to_dict('records')
    if os.path.exists("vips_backup.csv"):
        vips = pd.read_csv("vips_backup.csv")
        st.session_state.contas_vip = dict(zip(vips.nome, vips.valor))

# --- INICIALIZAÇÃO DE ESTADOS ---
if 'vendas' not in st.session_state: st.session_state.vendas = []
if 'contas_vip' not in st.session_state: st.session_state.contas_vip = {}
if 'carrinho' not in st.session_state: st.session_state.carrinho = {}
if 'cardapio' not in st.session_state: st.session_state.cardapio = {}
if 'configurado' not in st.session_state: st.session_state.configurado = False
if 'caixa_inicial' not in st.session_state: st.session_state.caixa_inicial = 0.0
if 'fichas_pendentes' not in st.session_state: st.session_state.fichas_pendentes = []

# Tenta recuperar dados ao iniciar
if not st.session_state.vendas:
    carregar_dados()

# --- FUNÇÃO GERAR FICHA (ETAPA 3) ---
def gerar_ficha_imagem(sabor, id_venda, pagto):
    largura = 300
    img = Image.new('RGB', (largura, 1000), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    def get_f(s, b=True):
        p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if b else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        try: return ImageFont.truetype(p, s)
        except: return ImageFont.load_default()

    y = 20
    if os.path.exists("logo.png"):
        logo = Image.open("logo.png").convert("RGBA")
        logo.thumbnail((120, 120))
        img.paste(logo, ((largura - logo.size[0]) // 2, y), logo)
        y += logo.size[1] + 10

    draw.text((largura/2, y), str(sabor).upper(), fill=(0,0,0), font=get_f(55), anchor="mm")
    y += 60
    draw.text((largura/2, y), f"ID: {str(id_venda)[-5:]} | {str(pagto).upper()}", fill=(0,0,0), font=get_f(20), anchor="mm")
    y += 50
    
    frases = [
        "VALIDO APENAS NA DATA DE EMISSAO",
        "DURANTE A DURACAO DO EVENTO",
        "SEVEN DWARFS A VERDADEIRA DELICIA GELADA",
        "BEBA COM MODERACAO"
    ]
    for f in frases:
        for linha in textwrap.wrap(f, width=28):
            draw.text((largura/2, y), linha, fill=(0,0,0), font=get_f(14, False), anchor="mm")
            y += 18
        y += 5

    return img.crop((0, 0, largura, y + 20))

# --- ETAPA 1: CONFIGURAÇÃO ---
if not st.session_state.configurado:
    st.title("⚙️ Abertura de Caixa - Seven Dwarfs")
    v_ini = st.number_input("Troco Inicial (R$):", min_value=0.0, value=st.session_state.caixa_inicial)
    
    col1, col2 = st.columns(2)
    with col1:
        fixos = st.multiselect("Sabores Fixos:", ["Pilsen", "IPA", "Black Jack", "Vinho", "Manga", "Morango"])
    with col2:
        extras = st.text_area("Sazonais (separados por vírgula):")
    
    lista_itens = list(dict.fromkeys(fixos + [s.strip() for s in extras.split(",") if s.strip()]))
    
    if lista_itens:
        st.subheader("Preços")
        c_precos = st.columns(3)
        temp_card = {}
        for i, item in enumerate(lista_itens):
            p_ex = st.session_state.cardapio.get(item, 0.0)
            temp_card[item] = c_precos[i%3].number_input(f"{item}:", min_value=0.0, value=float(p_ex), key=f"p_{item}")
        
        if st.button("ABRIR CAIXA", type="primary", use_container_width=True):
            st.session_state.cardapio = temp_card
            st.session_state.caixa_inicial = v_ini
            st.session_state.configurado = True
            st.rerun()
    st.stop()

# --- ETAPA 2: VENDAS ---
t1, t2, t3 = st.tabs(["🛒 PDV", "🔄 ESTORNO", "📊 FECHAMENTO"])

with t1:
    col_menu, col_carrinho = st.columns([1.6, 1])
    
    with col_menu:
        st.subheader("Sabores")
        c_btns = st.columns(2)
        for i, (nome, preco) in enumerate(st.session_state.cardapio.items()):
            if c_btns[i%2].button(f"{nome}\nR$ {preco:.2f}", key=f"btn_{nome}", use_container_width=True):
                if nome in st.session_state.carrinho: st.session_state.carrinho[nome]['qtd'] += 1
                else: st.session_state.carrinho[nome] = {'preco': preco, 'qtd': 1}
                st.rerun()
        
        st.write("---")
        st.subheader("Contas VIP")
