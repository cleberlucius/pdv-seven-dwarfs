import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Seven Dwarfs - PDV Profissional", layout="wide")

st.markdown("""
    <style>
    div.stButton > button { height: 5em; font-size: 16px; font-weight: bold; border-radius: 10px; margin-bottom: 5px; white-space: pre-wrap; }
    .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 10px; border: 1px solid #ddd; }
    .status-caixa { padding: 10px; border-radius: 8px; background-color: #fff3e0; color: #e65100; font-weight: bold; margin-bottom: 15px; border: 1px solid #ffe0b2; text-align: center; font-size: 18px; }
    .troco-box { background-color: #e8f5e9; padding: 15px; border-radius: 10px; border: 2px solid #2e7d32; color: #1b5e20; font-size: 20px; font-weight: bold; text-align: center; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS ---
if 'vendas' not in st.session_state: st.session_state.vendas = []
if 'sangrias' not in st.session_state: st.session_state.sangrias = []
if 'caixa_inicial' not in st.session_state: st.session_state.caixa_inicial = None
if 'cardapio' not in st.session_state: st.session_state.cardapio = {}
if 'configurado' not in st.session_state: st.session_state.configurado = False
if 'fichas_pendentes' not in st.session_state: st.session_state.fichas_pendentes = []
if 'carrinho' not in st.session_state: st.session_state.carrinho = {}
if 'show_dinheiro' not in st.session_state: st.session_state.show_dinheiro = False

# --- FUNÇÃO PARA GERAR A FICHA ---
def gerar_ficha_imagem(sabor, id_venda, pagto):
    img = Image.new('RGB', (300, 850), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    y = 30 

    # 1. Tentar carregar a Logo
    logo_file = "logo.png"
    if os.path.exists(logo_file):
        try:
            logo = Image.open(logo_file).convert("RGBA")
            canvas = Image.new("RGBA", logo.size, (255, 255, 255))
            canvas.paste(logo, mask=logo.split()[3])
            logo = canvas.convert("L") 
            largura_max = 240
            w_percent = (largura_max / float(logo.size[0]))
            h_size = int((float(logo.size[1]) * float(w_percent)))
            logo = logo.resize((largura_max, h_size), Image.Resampling.LANCZOS)
            img.paste(logo, ((300 - largura_max) // 2, y))
            y += h_size + 30
        except:
            d.text((150, y), "SEVEN DWARFS BEER", fill=(0,0,0), anchor="ms")
            y += 40
    else:
        y += 40
        d.text((150, y), "SEVEN DWARFS BEER", fill=(0,0,0), anchor="ms")
        y += 40

    try:
        f_grande = ImageFont.truetype("arialbd.ttf", 70)
        f_media = ImageFont.truetype("arialbd.ttf", 22)
        f_pequena = ImageFont.truetype("arial.ttf", 16)
    except:
        f_grande = f_media = f_pequena = ImageFont.load_default()

    d.line([(20, y), (280, y)], fill=(0,0,0), width=3)
    y += 80
    d.text((150, y), sabor.upper(), fill=(0,0,0), font=f_grande, anchor="ms")
    y += 40
    d.line([(20, y), (280, y)], fill=(0,0,0), width=3)
    y += 50
    d.text((150, y), f"VENDA ID: {id_venda:04d}", fill=(0,0,0), font=f_media, anchor="ms")
    y += 30
    d.text((150, y), f"PAGAMENTO: {pagto.upper()}", fill=(0,0,0), font=f_media, anchor="ms")
    y += 80

    # Rodapé Final Atualizado
    data_str = datetime.now().strftime("%d/%m/%Y - %H:%M")
    d.text((150, y), f"Emitido em: {data_str}", fill=(0,0,0), font=f_pequena, anchor="ms")
    y += 25
    # NOVA FRASE DE VALIDADE SOLICITADA:
    d.text((150, y), "Válido apenas na data de emissão durante o evento", fill=(0,0,0), font=f_pequena, anchor="ms")
    y += 25
    d.text((150, y), "Chopp Seven Dwarfs a verdadeira delícia gelada", fill=(0,0,0), font=f_pequena, anchor="ms")
    y += 25
    d.text((150, y), "BEBA COM MODERAÇÃO", fill=(0,0,0), font=f_pequena, anchor="ms")
    y += 40
    d.text((150, y), "- - - - - - - - - - - - - - -", fill=(0,0,0), anchor="ms")

    return img.crop((0, 0, 300, y + 20))

# --- INTERFACE DO PDV (MANTIDA) ---
if st.session_state.caixa_inicial is None:
    st.title("🚀 Abertura Seven Dwarfs")
    v_ini = st.number_input("Troco Inicial (R$):", min_value=0.0, step=10.0, value=0.0)
    if st.button("DEFINIR CARDÁPIO", use_container_width=True):
        st.session_state.caixa_inicial = v_ini
        st.rerun()
    st.stop()

if not st.session_state.configurado:
    st.title("⚙️ Configurar Cardápio")
    lista_opcoes = ["Pilsen", "IPA", "Black Jack", "Vinho", "Manga", "Weiss", "Red Ale", "Sour", "Água", "Refrigerante"]
    selecionados = st.multiselect("Sabores disponíveis:", lista_opcoes, default=["Pilsen", "IPA"])
    temp_card = {}
    c_p = st.columns(2)
    for i, s in enumerate(selecionados):
        preco = c_p[i % 2].number_input(f"Preço {s}:", min_value=1.0, value=15.0, key=f"p_{s}")
        temp_card[s] = preco
    if st.button("ABRIR VENDAS", use_container_width=True, type="primary"):
        if temp_card:
            st.session_state.cardapio = temp_card
            st.session_state.configurado = True
            st.rerun()
    st.stop()

st.markdown(f"<div class='status-caixa'>🍻 SEVEN DWARFS BEER | PDV</div>", unsafe_allow_html=True)
t1, t2, t3, t4 = st.tabs(["🛒 VENDER", "💸 SANGRIA", "🔄 ESTORNO", "📊 FECHAMENTO"])

df_v = pd.DataFrame(st.session_state.vendas)

with t1:
    col_v, col_c = st.columns([1.7, 1.3])
    with col_v:
        st.write("### 1. Selecionar")
        c_prod = st.columns(2)
        for i, (nome, preco) in enumerate(st.session_state.cardapio.items()):
            if c_prod[i % 2].button(f"{nome}\nR$ {preco:.2f}", key=f"btn_{nome}", use_container_width=True):
                if nome in st.session_state.carrinho: st.session_state.carrinho[nome]['qtd'] += 1
                else: st.session_state.carrinho[nome] = {'preco': preco, 'qtd': 1}
                st.rerun()

    with col_c:
        st.write("### 2. Resumo")
        total_v = 0.0
        if not st.session_state.carrinho: st.info("Carrinho vazio")
        else:
            for nome in list(st.session_state.carrinho.keys()):
                item = st.session_state.carrinho[nome]
                sub = item['preco'] * item['qtd']
                total_v += sub
                c1, c2, c3, c4, c5 = st.columns([0.6, 0.6, 0.6, 3, 0.8])
                if c1.button("➖", key=f"m_{nome}"):
                    if item['qtd'] > 1: st.session_state.carrinho[nome]['qtd'] -= 1
                    else: del st.session_state.carrinho[nome]
                    st.rerun()
                c2.markdown(f"<div style='padding-top:10px;'>{item['qtd']}</div>", unsafe_allow_html=True)
                if c3.button("➕", key=f"p_{nome}"):
                    st.session_state.carrinho[nome]['qtd'] += 1
                    st.rerun()
                c4.markdown(f"<div style='padding-top:10px;'><b>{nome}</b></div>", unsafe_allow_html=True)
                if c5.button("🗑️", key=f"d_{nome}"):
                    del st.session_state.carrinho[nome]
                    st.rerun()
            st.markdown(f"## TOTAL: R$ {total_v:.2f}")
            f_pgto = st.columns(2)
            metodo_f = None
            if f_pgto[0].button("PIX", use_container_width=True): metodo_f = "PIX"
            if f_pgto[1].button("DÉBITO", use_container_width=True): metodo_f = "Débito"
            if f_pgto[0].button("CRÉDITO", use_container_width=True): metodo_f = "Crédito"
            if f_pgto[1].button("DINHEIRO", use_container_width=True): st.session_state.show_dinheiro = True

            if st.session_state.show_dinheiro:
                receb = st.number_input("Valor Recebido:", min_value=float(total_v), value=float(total_v))
                st.markdown(f"<div class='troco-box'>TROCO: R$ {receb - total_v:.2f}</div>", unsafe_allow_html=True)
                if st.button("CONFIRMAR DINHEIRO", type="primary", use_container_width=True):
                    metodo_f = "Dinheiro"
                    st.session_state.show_dinheiro = False
            
            if metodo_f:
                v_id = len(st.session_state.vendas) + 1
                for n, i in st.session_state.carrinho.items():
                    st.session_state.vendas.append({"id": v_id, "Sabor": n, "Qtd": i['qtd'], "Total": i['preco']*i['qtd'], "Tipo": metodo_f, "Hora": datetime.now().strftime("%H:%M")})
                    for _ in range(i['qtd']): st.session_state.fichas_pendentes.append(gerar_ficha_imagem(n, v_id, metodo_f))
                st.session_state.carrinho = {}
                st.rerun()

        st.divider()
        if st.session_state.fichas_pendentes:
            if st.button("IMPRIMIR TUDO", use_container_width=True, type="primary"):
                for img in st.session_state.fichas_pendentes: st.image(img)
                st.session_state.fichas_pendentes = []

# ABAS DE SUPORTE
with t2:
    v_s = st.number_input("Valor Retirada:", min_value=0.0)
    m_s = st.text_input("Motivo:")
    if st.button("Salvar Sangria"):
        if v_s > 0: st.session_state.sangrias.append({"Hora": datetime.now().strftime("%H:%M"), "Motivo": m_s, "Valor": v_s})
with t3:
    if not df_v.empty:
        id_e = st.selectbox("ID para cancelar:", df_v['id'].unique())
        if st.button("Confirmar Estorno"):
            st.session_state.vendas = [v for v in st.session_state.vendas if v['id'] != id_e]
            st.rerun()
with t4:
    df_s = pd.DataFrame(st.session_state.sangrias)
    v_din = df_v[df_v['Tipo'] == 'Dinheiro']['Total'].sum() if not df_v.empty else 0
    s_tot = df_s['Valor'].sum() if not df_s.empty else 0
    st.metric("DINHEIRO EM CAIXA", f"R$ {st.session_state.caixa_inicial + v_din - s_tot:.2f}")
    if st.button("ZERAR SISTEMA"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
