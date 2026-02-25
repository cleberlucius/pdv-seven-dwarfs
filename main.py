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

# --- FUNÇÃO PARA GERAR A FICHA ---
def gerar_ficha_imagem(sabor, id_venda, pagto):
    largura = 300
    altura_estimada = 800 
    img = Image.new('RGB', (largura, altura_estimada), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    def get_font(size):
        try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        except: return ImageFont.load_default()

    y = 30
    draw.line([(15, y), (285, y)], fill=(0,0,0), width=5)
    y += 50
    draw.text((largura/2, y), str(sabor).upper(), fill=(0,0,0), font=get_font(60), anchor="mm")
    y += 60
    draw.text((largura/2, y), f"PAGTO: {str(pagto).upper()}", fill=(0,0,0), font=get_font(25), anchor="mm")
    y += 40
    draw.text((largura/2, y), f"ID: {str(id_venda)[-5:]}", fill=(0,0,0), font=get_font(20), anchor="mm")
    y += 50
    draw.text((largura/2, y), datetime.now().strftime("%d/%m/%Y %H:%M"), fill=(0,0,0), font=get_font(15), anchor="mm")
    
    return img.crop((0, 0, largura, y + 40))

# --- TELA DE CONFIGURAÇÃO ---
if st.session_state.configurado == False:
    st.title("⚙️ Configuração Cardápio")
    v_ini = st.number_input("Troco Inicial (R$):", min_value=0.0, value=st.session_state.caixa_inicial)
    
    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        opcoes_base = ["Pilsen", "IPA", "Black Jack", "Vinho", "Manga", "Morango"]
        selec_base = st.multiselect("Sabores Fixos:", opcoes_base)
    
    with col_cfg2:
        novos_extras = st.text_area("Adicionar Outros (Ex: Água, Suco):", placeholder="Separe por vírgula")

    # Unifica e remove duplicados
    lista_final = list(dict.fromkeys(selec_base + [s.strip() for s in novos_extras.split(",") if s.strip()]))
    
    st.write("---")
    temp_card = {}
    if lista_final:
        st.subheader("Defina os Preços:")
        cols_p = st.columns(3)
        for i, sabor in enumerate(lista_final):
            temp_card[sabor] = cols_p[i%3].number_input(f"Preço {sabor}:", min_value=0.0, key=f"pre_{sabor}")
    
    if st.button("SALVAR E ABRIR VENDAS", type="primary", use_container_width=True):
        if lista_final:
            st.session_state.caixa_inicial = v_ini
            st.session_state.cardapio = temp_card
            st.session_state.configurado = True
            st.rerun()
    st.stop()

# --- INTERFACE PDV ---
st.markdown("### 🍻 PDV Seven Dwarfs")
t1, t2, t3 = st.tabs(["🛒 VENDER", "🔄 ESTORNO", "📊 FECHAMENTO"])

with t1:
    cv, cc = st.columns([1.5, 1])
    with cv:
        cols_v = st.columns(2)
        for i, (n, p) in enumerate(st.session_state.cardapio.items()):
            if cols_v[i%2].button(f"{n}\nR$ {p:.2f}", key=f"btn_{n}", use_container_width=True):
                if n in st.session_state.carrinho: st.session_state.carrinho[n]['qtd'] += 1
                else: st.session_state.carrinho[n] = {'preco': p, 'qtd': 1}
                st.rerun()
    with cc:
        total_venda = sum(it['preco'] * it['qtd'] for it in st.session_state.carrinho.values())
        if not st.session_state.carrinho: st.info("Carrinho Vazio")
        else:
            for n, it in list(st.session_state.carrinho.items()):
                c_i, c_d = st.columns([4, 1])
                c_i.write(f"**{it['qtd']}x {n}**")
                if c_d.button("🗑️", key=f"del_{n}"): 
                    del st.session_state.carrinho[n]
                    st.rerun()
            
            st.markdown(f"## Total: R$ {total_venda:.2f}")
            m_final = None
            
            cp1, cp2 = st.columns(2)
            if cp1.button("PIX", use_container_width=True): m_final = "PIX"
            if cp2.button("DÉBITO", use_container_width=True): m_final = "Débito"
            if cp1.button("CRÉDITO", use_container_width=True): m_final = "Crédito"
            if cp2.button("DINHEIRO", use_container_width=True): 
                st.session_state.show_dinheiro = not st.session_state.show_dinheiro
                st.rerun()

            if st.session_state.show_dinheiro:
                rec = st.number_input("Recebido:", min_value=0.0)
                if rec >= total_venda:
                    st.success(f"Troco: R$ {rec-total_venda:.2f}")
                    if st.button("CONFIRMAR DINHEIRO"): m_final = "Dinheiro"; st.session_state.show_dinheiro = False

            if m_final:
                v_id = int(datetime.now().timestamp())
                for n, it in st.session_state
                
