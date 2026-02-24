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
    .carrinho-row { display: flex; align-items: center; justify-content: space-between; padding: 8px; border-bottom: 1px solid #eee; background-color: white; border-radius: 5px; margin-bottom: 5px; }
    .item-info { flex-grow: 1; margin-left: 10px; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS ---
if 'vendas' not in st.session_state: st.session_state.vendas = []
if 'sangrias' not in st.session_state: st.session_state.sangrias = []
if 'devolucoes' not in st.session_state: st.session_state.devolucoes = []
if 'caixa_inicial' not in st.session_state: st.session_state.caixa_inicial = None
if 'cardapio' not in st.session_state: st.session_state.cardapio = {}
if 'configurado' not in st.session_state: st.session_state.configurado = False
if 'fichas_pendentes' not in st.session_state: st.session_state.fichas_pendentes = []
if 'carrinho' not in st.session_state: st.session_state.carrinho = {}

# --- FUNÇÃO PARA GERAR A FICHA ---
def gerar_ficha_imagem(sabor, id_venda, pagto):
    img = Image.new('RGB', (300, 650), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    y_offset = 20
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            background = Image.new("RGB", logo.size, (255, 255, 255))
            background.paste(logo, mask=logo.split()[3])
            logo = background.convert("L")
            largura_logo = 260
            w_percent = (largura_logo / float(logo.size[0]))
            h_size = int((float(logo.size[1]) * float(w_percent)))
            logo = logo.resize((largura_logo, h_size), Image.Resampling.LANCZOS)
            img.paste(logo, ((300 - largura_logo) // 2, y_offset))
            y_offset += h_size + 30
        except: y_offset = 80
    else: y_offset = 80

    try:
        font_sabor = ImageFont.truetype("arialbd.ttf", 90)
        font_info = ImageFont.truetype("arialbd.ttf", 24)
        font_rodape = ImageFont.truetype("arial.ttf", 16)
    except: font_sabor = font_info = font_rodape = ImageFont.load_default()

    d.line([(10, y_offset), (290, y_offset)], fill=(0,0,0), width=4)
    d.text((150, y_offset + 100), sabor.upper(), fill=(0,0,0), font=font_sabor, anchor="ms")
    d.line([(10, y_offset + 180), (290, y_offset + 180)], fill=(0,0,0), width=4)
    d.text((20, y_offset + 220), f"VENDA ID: {id_venda:04d}", fill=(0,0,0), font=font_info)
    d.text((20, y_offset + 255), f"FORMA PGTO: {pagto.upper()}", fill=(0,0,0), font=font_info)
    data_str = datetime.now().strftime("%d/%m/%Y - %H:%M")
    d.text((150, y_offset + 340), f"Emitido em: {data_str}", fill=(0,0,0), font=font_rodape, anchor="ms")
    return img

# --- INTERFACE ---
if st.session_state.caixa_inicial is None:
    st.title("🚀 Abertura Seven Dwarfs")
    v_ini = st.number_input("Troco Inicial (R$):", min_value=0.0, step=10.0, value=0.0)
    if st.button("DEFINIR CARDÁPIO", use_container_width=True):
        st.session_state.caixa_inicial = v_ini
        st.rerun()
    st.stop()

if not st.session_state.configurado:
    st.title("⚙️ Cardápio")
    lista_opcoes = ["Pilsen", "IPA", "Black Jack", "Vinho", "Manga", "Weiss", "Red Ale", "Sour", "Água", "Refrigerante"]
    selecionados = st.multiselect("Sabores de hoje:", lista_opcoes, default=["Pilsen", "IPA"])
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
        st.write("### 1. Cardápio")
        c_prod = st.columns(2)
        for i, (nome, preco) in enumerate(st.session_state.cardapio.items()):
            if c_prod[i % 2].button(f"{nome}\nR$ {preco:.2f}", key=f"btn_{nome}", use_container_width=True):
                if nome in st.session_state.carrinho:
                    st.session_state.carrinho[nome]['qtd'] += 1
                else:
                    st.session_state.carrinho[nome] = {'preco': preco, 'qtd': 1}
                st.rerun()

    with col_c:
        st.write("### 2. Resumo da Venda")
        total_venda = 0.0
        
        if not st.session_state.carrinho:
            st.info("Carrinho vazio")
        else:
            # Lista editável de produtos
            for nome in list(st.session_state.carrinho.keys()):
                item = st.session_state.carrinho[nome]
                subtotal = item['preco'] * item['qtd']
                total_venda += subtotal
                
                # Linha de resumo com botões + - e Lixo
                col_btn_m, col_qtd, col_btn_p, col_txt, col_lixo = st.columns([0.6, 0.6, 0.6, 3, 0.8])
                
                if col_btn_m.button("➖", key=f"min_{nome}"):
                    if item['qtd'] > 1: st.session_state.carrinho[nome]['qtd'] -= 1
                    else: del st.session_state.carrinho[nome]
                    st.rerun()
                
                col_qtd.markdown(f"<div style='text-align:center; padding-top:10px;'>{item['qtd']}</div>", unsafe_allow_html=True)
                
                if col_btn_p.button("➕", key=f"plus_{nome}"):
                    st.session_state.carrinho[nome]['qtd'] += 1
                    st.rerun()
                
                col_txt.markdown(f"<div style='padding-top:10px;'><b>{nome}</b><br><small>R$ {subtotal:.2f}</small></div>", unsafe_allow_html=True)
                
                if col_lixo.button("🗑️", key=f"del_{nome}"):
                    del st.session_state.carrinho[nome]
                    st.rerun()
            
            st.markdown(f"## TOTAL: R$ {total_venda:.2f}")
            
            # Formas de Pagamento
            metodo = None
            f_pgto = st.columns(2)
            if f_pgto[0].button("PIX", use_container_width=True): metodo = "PIX"
            if f_pgto[1].button("DÉBITO", use_container_width=True): metodo = "Débito"
            if f_pgto[0].button("CRÉDITO", use_container_width=True): metodo = "Crédito"
            if f_pgto[1].button("DINHEIRO", use_container_width=True): metodo = "Dinheiro"
            
            if metodo:
                proximo_id = len(st.session_state.vendas) + len(st.session_state.devolucoes) + 1
                for n, i in st.session_state.carrinho.items():
                    st.session_state.vendas.append({
                        "id": proximo_id, "Sabor": n, "Qtd": i['qtd'], 
                        "Total": i['preco'] * i['qtd'], "Tipo": metodo, "Hora": datetime.now().strftime("%H:%M")
                    })
                    for _ in range(i['qtd']):
                        st.session_state.fichas_pendentes.append(gerar_ficha_imagem(n, proximo_id, metodo))
                st.session_state.carrinho = {}
                st.success("Venda Finalizada!")
                st.rerun()

        st.divider()
        st.write("### 🖨️ Fichas Pendentes")
        if st.session_state.fichas_pendentes:
            if st.button("IMPRIMIR TUDO", use_container_width=True, type="primary"):
                for img in st.session_state.fichas_pendentes: st.image(img)
                st.session_state.fichas_pendentes = []

# ABAS DE SUPORTE
with t2:
    val_s = st.number_input("Valor Retirado:", min_value=0.0)
    mot = st.text_input("Finalidade:")
    if st.button("Registrar Sangria"):
        if val_s > 0: st.session_state.sangrias.append({"Hora": datetime.now().strftime("%H:%M"), "Motivo": mot, "Valor": val_s})

with t3:
    if not df_v.empty:
        id_est = st.selectbox("ID da venda para cancelar:", df_v['id'].unique())
        if st.button("Confirmar Estorno"):
            st.session_state.vendas = [v for v in st.session_state.vendas if v['id'] != id_est]
            st.rerun()

with t4:
    df_s = pd.DataFrame(st.session_state.sangrias)
    v_din = df_v[df_v['Tipo'] == 'Dinheiro']['Total'].sum() if not df_v.empty else 0
    s_tot = df_s['Valor'].sum() if not df_s.empty else 0
    caixa_fisico = st.session_state.caixa_inicial + v_din - s_tot
    st.metric("DINHEIRO EM ESPÉCIE NO CAIXA", f"R$ {caixa_fisico:.2f}")
    if st.button("ENCERRAR EVENTO E LIMPAR"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
