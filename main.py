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
    .troco-box { background-color: #e8f5e9; padding: 15px; border-radius: 10px; border: 2px solid #2e7d32; color: #1b5e20; font-size: 28px; font-weight: bold; text-align: center; margin-top: 10px; }
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
    img = Image.new('RGB', (300, 800), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    y = 20 

    logo_file = "logo.png"
    if os.path.exists(logo_file):
        try:
            logo = Image.open(logo_file).convert("RGBA")
            canvas = Image.new("RGBA", logo.size, (255, 255, 255))
            canvas.paste(logo, mask=logo.split()[3])
            logo = canvas.convert("L") 
            largura_logo = 150
            w_percent = (largura_logo / float(logo.size[0]))
            h_size = int((float(logo.size[1]) * float(w_percent)))
            logo = logo.resize((largura_logo, h_size), Image.Resampling.LANCZOS)
            img.paste(logo, ((300 - largura_logo) // 2, y))
            y += h_size + 20
        except: y += 40
    
    try:
        f_sabor = ImageFont.truetype("arialbd.ttf", 85)
        f_media = ImageFont.truetype("arialbd.ttf", 22)
        f_pequena = ImageFont.truetype("arial.ttf", 16)
    except:
        f_sabor = f_media = f_pequena = ImageFont.load_default()

    d.line([(10, y), (290, y)], fill=(0,0,0), width=4)
    y += 90
    d.text((150, y), sabor.upper(), fill=(0,0,0), font=f_sabor, anchor="ms")
    y += 30
    d.line([(10, y), (290, y)], fill=(0,0,0), width=4)
    y += 60

    d.text((150, y), f"VENDA ID: {id_venda:04d}", fill=(0,0,0), font=f_media, anchor="ms")
    y += 35
    d.text((150, y), f"PAGAMENTO: {pagto.upper()}", fill=(0,0,0), font=f_media, anchor="ms")
    y += 80

    data_str = datetime.now().strftime("%d/%m/%Y - %H:%M")
    d.text((150, y), f"Emitido em: {data_str}", fill=(0,0,0), font=f_pequena, anchor="ms")
    y += 25
    d.text((150, y), "Válido apenas na data de emissão durante o evento", fill=(0,0,0), font=f_pequena, anchor="ms")
    y += 25
    d.text((150, y), "Chopp Seven Dwarfs a verdadeira delicia gelada", fill=(0,0,0), font=f_pequena, anchor="ms")
    y += 25
    d.text((150, y), "BEBA COM MODERACAO", fill=(0,0,0), font=f_pequena, anchor="ms")
    y += 40
    d.text((150, y), "---------------------------", fill=(0,0,0), anchor="ms")

    return img.crop((0, 0, 300, y + 20))

# --- INTERFACE ---
if st.session_state.caixa_inicial is None:
    st.title("🚀 Abertura Seven Dwarfs")
    v_ini_str = st.text_input("Troco Inicial (R$):", value="", placeholder="Digite o valor...")
    if st.button("DEFINIR CARDÁPIO", use_container_width=True):
        try:
            st.session_state.caixa_inicial = float(v_ini_str.replace(',', '.'))
            st.rerun()
        except: st.error("Por favor, digite um valor numérico.")
    st.stop()

if not st.session_state.configurado:
    st.title("⚙️ Cardápio")
    lista_opcoes = ["Pilsen", "IPA", "Black Jack", "Vinho", "Manga", "Weiss", "Red Ale", "Sour", "Água", "Refrigerante"]
    selecionados = st.multiselect("Sabores de hoje:", lista_opcoes, default=["Pilsen", "IPA"])
    temp_card = {}
    c_p = st.columns(2)
    for i, s in enumerate(selecionados):
        p_str = c_p[i % 2].text_input(f"Preço {s} (R$):", value="", placeholder="Ex: 15.00", key=f"conf_{s}")
        try: temp_card[s] = float(p_str.replace(',', '.')) if p_str else 0.0
        except: temp_card[s] = 0.0
            
    if st.button("ABRIR VENDAS", use_container_width=True, type="primary"):
        if any(v > 0 for v in temp_card.values()):
            st.session_state.cardapio = temp_card
            st.session_state.configurado = True
            st.rerun()
    st.stop()

st.markdown(f"<div class='status-caixa'>🍻 SEVEN DWARFS BEER | PDV</div>", unsafe_allow_html=True)
t1, t2, t3, t4 = st.tabs(["🛒 VENDER", "💸 SANGRIA", "🔄 ESTORNO", "📊 FECHAMENTO"])

# --- ABA DE VENDAS ---
with t1:
    col_v, col_c = st.columns([1.7, 1.3])
    with col_v:
        st.write("### 1. Cardápio")
        c_prod = st.columns(2)
        for i, (nome, preco) in enumerate(st.session_state.cardapio.items()):
            if c_prod[i % 2].button(f"{nome}\nR$ {preco:.2f}", key=f"btn_{nome}", use_container_width=True):
                if nome in st.session_state.carrinho: st.session_state.carrinho[nome]['qtd'] += 1
                else: st.session_state.carrinho[nome] = {'preco': preco, 'qtd': 1}
                st.rerun()

    with col_c:
        st.write("### 2. Resumo")
        total_venda = 0.0
        if not st.session_state.carrinho: st.info("Carrinho vazio")
        else:
            for nome in list(st.session_state.carrinho.keys()):
                item = st.session_state.carrinho[nome]
                total_venda += item['preco'] * item['qtd']
                c1, c2, c3, c4, c5 = st.columns([0.5, 0.5, 0.5, 3, 0.8])
                if c1.button("➖", key=f"min_{nome}"):
                    if item['qtd'] > 1: st.session_state.carrinho[nome]['qtd'] -= 1
                    else: del st.session_state.carrinho[nome]
                    st.rerun()
                c2.markdown(f"<div style='padding-top:10px;'>{item['qtd']}</div>", unsafe_allow_html=True)
                if c3.button("➕", key=f"plus_{nome}"):
                    st.session_state.carrinho[nome]['qtd'] += 1
                    st.rerun()
                c4.markdown(f"<div style='padding-top:10px;'><b>{nome}</b></div>", unsafe_allow_html=True)
                if c5.button("🗑️", key=f"del_{nome}"):
                    del st.session_state.carrinho[nome]
                    st.rerun()
            
            st.markdown(f"## TOTAL: R$ {total_venda:.2f}")
            f_pgto = st.columns(2)
            metodo_final = None
            if f_pgto[0].button("PIX", use_container_width=True): metodo_final = "PIX"
            if f_pgto[1].button("DÉBITO", use_container_width=True): metodo_final = "Débito"
            if f_pgto[0].button("CRÉDITO", use_container_width=True): metodo_final = "Crédito"
            if f_pgto[1].button("DINHEIRO", use_container_width=True): st.session_state.show_dinheiro = True

            if st.session_state.show_dinheiro:
                st.divider()
                # CAMPO VAZIO PARA DIGITAÇÃO RÁPIDA DO TROCO
                recebido_str = st.text_input("Valor Recebido (R$):", value="", placeholder="Digite quanto o cliente deu...", key=f"money_{len(st.session_state.vendas)}")
                if recebido_str:
                    try:
                        val_recebido = float(recebido_str.replace(',', '.'))
                        troco = val_recebido - total_venda
                        if troco >= 0:
                            st.markdown(f"<div class='troco-box'>TROCO: R$ {troco:.2f}</div>", unsafe_allow_html=True)
                            if st.button("CONFIRMAR DINHEIRO", type="primary", use_container_width=True):
                                metodo_final = "Dinheiro"
                                st.session_state.show_dinheiro = False
                        else: st.error("Valor abaixo do total!")
                    except: pass

            if metodo_final:
                pid = int(datetime.now().timestamp()) # ID único baseado no tempo
                for n, i in st.session_state.carrinho.items():
                    for _ in range(i['qtd']):
                        # Cada item é uma linha para permitir estorno individual
                        st.session_state.vendas.append({"id_venda": pid, "Sabor": n, "Valor": i['preco'], "Tipo": metodo_final, "Hora": datetime.now().strftime("%H:%M")})
                        st.session_state.fichas_pendentes.append(gerar_ficha_imagem(n, pid, metodo_final))
                st.session_state.carrinho = {}
                st.rerun()

        st.divider()
        if st.session_state.fichas_pendentes:
            if st.button("IMPRIMIR TUDO", use_container_width=True, type="primary"):
                for img in st.session_state.fichas_pendentes: st.image(img)
                st.session_state.fichas_pendentes = []

# --- ABA DE ESTORNO POR ITEM (NOVO) ---
with t3:
    st.write("### 🔄 Estorno por Item")
    if not st.session_state.vendas:
        st.info("Nenhuma venda realizada.")
    else:
        df_e = pd.DataFrame(st.session_state.vendas)
        vendas_lista = df_e['id_venda'].unique()
        sel_venda = st.selectbox("Selecione o ID da Venda:", vendas_lista, format_func=lambda x: f"Venda {str(x)[-4:]}")
        
        # Filtrar itens desta venda
        itens_venda = [v for v in st.session_state.vendas if v['id_venda'] == sel_venda]
        st.write("#### Selecione os itens para remover:")
        
        indices_para_remover = []
        for idx, item in enumerate(itens_venda):
            if st.checkbox(f"{item['Sabor']} - R$ {item['Valor']:.2f} ({item['Hora']})", key=f"est_{sel_venda}_{idx}"):
                indices_para_remover.append(item)
        
        if indices_para_remover:
            if st.button("ESTORNAR ITENS SELECIONADOS", type="primary"):
                for p in indices_para_remover:
                    st.session_state.vendas.remove(p)
                st.success("Itens estornados!")
                st.rerun()

# --- ABA DE SANGRIA E FECHAMENTO ---
with t2:
    v_s_str = st.text_input("Valor Retirada (R$):", value="", placeholder="0.00")
    m_s = st.text_input("Motivo:")
    if st.button("Salvar Sangria"):
        try:
            val_s = float(v_s_str.replace(',', '.'))
            st.session_state.sangrias.append({"Hora": datetime.now().strftime("%H:%M"), "Motivo": m_s, "Valor": val_s})
            st.success("Registrado!")
            st.rerun()
        except: st.error("Valor inválido.")

with t4:
    if st.session_state.vendas:
        df_f = pd.DataFrame(st.session_state.vendas)
        v_pix = df_f[df_f['Tipo'] == 'PIX']['Valor'].sum()
        v_cartao = df_f[df_f['Tipo'].isin(['Débito', 'Crédito'])]['Valor'].sum()
        v_din = df_f[df_f['Tipo'] == 'Dinheiro']['Valor'].sum()
        s_tot = sum(s['Valor'] for s in st.session_state.sangrias)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("PIX", f"R$ {v_pix:.2f}")
        c2.metric("CARTÕES", f"R$ {v_cartao:.2f}")
        c3.metric("DINHEIRO NO CAIXA", f"R$ {st.session_state.caixa_inicial + v_din - s_tot:.2f}")
        
        st.write("---")
        st.write("#### Itens Vendidos (Fichas Entregues)")
        st.table(df_f.groupby('Sabor').size().reset_index(name='Quantidade'))
    
    if st.button("FECHAR EVENTO (ZERAR TUDO)"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
