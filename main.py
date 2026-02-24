import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Seven Dwarfs - PDV Profissional", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    div.stButton > button { height: 5.5em; font-size: 16px; font-weight: bold; border-radius: 12px; margin-bottom: 10px; white-space: pre-wrap; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #ddd; }
    .status-caixa { padding: 15px; border-radius: 8px; background-color: #fff3e0; color: #e65100; font-weight: bold; margin-bottom: 20px; border: 1px solid #ffe0b2; text-align: center; font-size: 20px; }
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

# --- FUNÇÃO PARA GERAR A FICHA ---
def gerar_ficha_imagem(sabor, id_venda, pagto):
    img = Image.new('RGB', (300, 580), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    y_offset = 20
    
    try:
        logo = Image.open("logo.png").convert("L")
        largura_logo = 220
        w_percent = (largura_logo / float(logo.size[0]))
        h_size = int((float(logo.size[1]) * float(w_percent)))
        logo = logo.resize((largura_logo, h_size), Image.Resampling.LANCZOS)
        img.paste(logo, ((300 - largura_logo) // 2, y_offset))
        y_offset += h_size + 20
    except:
        y_offset = 60
        d.text((150, y_offset), "SEVEN DWARFS BEER", fill=(0,0,0), anchor="ms")
        y_offset += 40

    try:
        font_sabor = ImageFont.truetype("arialbd.ttf", 75)
        font_info = ImageFont.truetype("arialbd.ttf", 20)
        font_rodape = ImageFont.truetype("arial.ttf", 15)
    except:
        font_sabor = font_info = font_rodape = ImageFont.load_default()

    d.line([(20, y_offset), (280, y_offset)], fill=(0,0,0), width=3)
    d.text((150, y_offset + 90), sabor.upper(), fill=(0,0,0), font=font_sabor, anchor="ms")
    d.line([(20, y_offset + 170), (280, y_offset + 170)], fill=(0,0,0), width=3)

    d.text((30, y_offset + 200), f"ID Venda: {id_venda:04d}", fill=(0,0,0), font=font_info)
    d.text((30, y_offset + 235), f"PGTO: {pagto.upper()}", fill=(0,0,0), font=font_info)

    data_str = datetime.now().strftime("%d/%m/%Y - %H:%M")
    d.text((150, y_offset + 300), f"Emitido em: {data_str}", fill=(0,0,0), font=font_rodape, anchor="ms")
    d.text((150, y_offset + 330), "VALIDO APENAS PARA ESTE EVENTO", fill=(0,0,0), font=font_rodape, anchor="ms")
    
    return img

# --- FLUXO DE TELAS ---

if st.session_state.caixa_inicial is None:
    st.title("🚀 Abertura Seven Dwarfs")
    v_ini = st.number_input("Troco Inicial (R$):", min_value=0.0, step=10.0, value=0.0)
    if st.button("DEFINIR CARDÁPIO", use_container_width=True):
        st.session_state.caixa_inicial = v_ini
        st.rerun()
    st.stop()

if not st.session_state.configurado:
    st.title("⚙️ Cardápio do Dia")
    lista_opcoes = ["Pilsen", "IPA", "Black Jack", "Vinho", "Manga", "Weiss", "Red Ale", "Sour", "Água", "Refrigerante"]
    selecionados = st.multiselect("Selecione os sabores de hoje:", lista_opcoes, default=["Pilsen", "IPA"])
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

# OPERAÇÃO
st.markdown(f"<div class='status-caixa'>🍻 SEVEN DWARFS BEER | CAIXA ABERTO</div>", unsafe_allow_html=True)
t1, t2, t3, t4 = st.tabs(["🛒 VENDER", "💸 SANGRIA", "🔄 ESTORNO", "📊 FECHAMENTO"])

df_v = pd.DataFrame(st.session_state.vendas)

with t1:
    col_v, col_i = st.columns([2, 1])
    with col_v:
        st.write("### 1. Novo Pedido")
        qtd = st.number_input("Quantidade:", min_value=1, value=1)
        contagem = df_v.groupby('Sabor')['Qtd'].sum().to_dict() if not df_v.empty else {}
        c_prod = st.columns(2)
        for i, (nome, preco) in enumerate(st.session_state.cardapio.items()):
            vendidos = contagem.get(nome, 0)
            btn_label = f"{nome}\nR$ {preco:.2f}\n(Vendidos: {int(vendidos)})"
            if c_prod[i % 2].button(btn_label, key=f"btn_{nome}", use_container_width=True):
                st.session_state.venda_confirm = {"sabor": nome, "preco": preco, "qtd": qtd}

        if 'venda_confirm' in st.session_state:
            vc = st.session_state.venda_confirm
            total_v = vc['preco'] * vc['qtd']
            st.warning(f"**CONFIRMAR: {vc['qtd']}x {vc['sabor']} | R$ {total_v:.2f}**")
            cp = st.columns(4)
            metodo = None
            if cp[0].button("PIX"): metodo = "PIX"
            if cp[1].button("DÉB"): metodo = "Débito"
            if cp[2].button("CRÉ"): metodo = "Crédito"
            if cp[3].button("DIN"): metodo = "Dinheiro"
            if metodo:
                proximo_id = len(st.session_state.vendas) + len(st.session_state.devolucoes) + 1
                st.session_state.vendas.append({"id": proximo_id, "Sabor": vc['sabor'], "Qtd": vc['qtd'], "Total": total_v, "Tipo": metodo, "Hora": datetime.now().strftime("%H:%M")})
                for _ in range(vc['qtd']):
                    st.session_state.fichas_pendentes.append(gerar_ficha_imagem(vc['sabor'], proximo_id, metodo))
                del st.session_state.venda_confirm
                st.rerun()
            if st.button("❌ Cancelar", use_container_width=True):
                del st.session_state.venda_confirm
                st.rerun()

    with col_i:
        st.write("### 🖨️ Fichas")
        if st.session_state.fichas_pendentes:
            if st.button("IMPRIMIR FICHAS", use_container_width=True):
                for img in st.session_state.fichas_pendentes: st.image(img)
                st.session_state.fichas_pendentes = []
        else: st.write("Aguardando...")

with t2: # Sangria
    mot = st.text_input("Motivo Sangria:")
    val_s = st.number_input("Valor (R$):", min_value=0.0)
    if st.button("Confirmar Sangria"):
        if mot and val_s > 0:
            st.session_state.sangrias.append({"Hora": datetime.now().strftime("%H:%M"), "Motivo": mot, "Valor": val_s})
            st.rerun()

with t3: # Estorno
    if not df_v.empty:
        id_est = st.selectbox("ID da venda:", df_v['id'].unique())
        if st.button("PROCESSAR ESTORNO", type="primary"):
            item = df_v[df_v['id'] == id_est].iloc[0]
            st.session_state.devolucoes.append({"Sabor": item['Sabor'], "Valor": item['Total'], "Tipo": item['Tipo']})
            st.session_state.vendas = [v for v in st.session_state.vendas if v['id'] != id_est]
            st.rerun()

with t4: # Fechamento
    df_s = pd.DataFrame(st.session_state.sangrias)
    df_d = pd.DataFrame(st.session_state.devolucoes)
    v_din = df_v[df_v['Tipo'] == 'Dinheiro']['Total'].sum() if not df_v.empty else 0
    s_tot = df_s['Valor'].sum() if not df_s.empty else 0
    d_din = df_d[df_d['Tipo'] == 'Dinheiro']['Valor'].sum() if not df_d.empty else 0
    caixa_fisico = st.session_state.caixa_inicial + v_din - s_tot - d_din
    st.metric("DINHEIRO EM MÃO", f"R$ {caixa_fisico:.2f}")
    if not df_v.empty:
        st.write("### Resumo por Sabor")
        st.table(df_v.groupby('Sabor')['Qtd'].sum())
    if st.button("ZERAR TUDO"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
