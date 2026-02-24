import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Seven Dwarfs - PDV", layout="wide")

st.markdown("""
    <style>
    div.stButton > button { height: 5em; font-size: 16px; font-weight: bold; border-radius: 10px; margin-bottom: 5px; white-space: pre-wrap; }
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
if 'sel_todos_estorno' not in st.session_state: st.session_state.sel_todos_estorno = False

# --- FUNÇÃO PARA GERAR A FICHA (Sabor Gigante e Negrito) ---
def gerar_ficha_imagem(sabor, id_venda, pagto):
    img = Image.new('RGB', (300, 700), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    y = 15 

    logo_file = "logo.png"
    if os.path.exists(logo_file):
        try:
            logo = Image.open(logo_file).convert("RGBA")
            largura_logo = 100
            w_percent = (largura_logo / float(logo.size[0]))
            h_size = int((float(logo.size[1]) * float(w_percent)))
            logo = logo.resize((largura_logo, h_size), Image.Resampling.LANCZOS)
            img.paste(logo, ((300 - largura_logo) // 2, y), logo)
            y += h_size + 10
        except: y += 20
    
    try:
        f_sabor = ImageFont.truetype("arialbd.ttf", 100) 
        f_info = ImageFont.truetype("arialbd.ttf", 24)
        f_pequena = ImageFont.truetype("arial.ttf", 16)
    except:
        f_sabor = f_info = f_pequena = ImageFont.load_default()

    d.line([(10, y), (290, y)], fill=(0,0,0), width=3)
    y += 85 
    d.text((150, y), sabor.upper(), fill=(0,0,0), font=f_sabor, anchor="ms")
    y += 20
    d.line([(10, y), (290, y)], fill=(0,0,0), width=3)
    y += 40

    d.text((150, y), f"VENDA: {str(id_venda)[-5:]}", fill=(0,0,0), font=f_info, anchor="ms")
    y += 30
    d.text((150, y), f"PGTO: {pagto.upper()}", fill=(0,0,0), font=f_info, anchor="ms")
    y += 50

    data_str = datetime.now().strftime("%d/%m/%Y - %H:%M")
    d.text((150, y), data_str, fill=(0,0,0), font=f_pequena, anchor="ms")
    y += 25
    d.text((150, y), "Valido apenas para o dia de hoje", fill=(0,0,0), font=f_pequena, anchor="ms")
    y += 40
    d.text((150, y), "---------------------------", fill=(0,0,0), anchor="ms")

    return img.crop((0, 0, 300, y + 20))

# --- INTERFACE ---
if st.session_state.caixa_inicial is None:
    st.title("🚀 Abertura Seven Dwarfs")
    v_ini = st.text_input("Troco Inicial (R$):", value="", placeholder="0.00")
    if st.button("CONFIGURAR CARDÁPIO"):
        try:
            st.session_state.caixa_inicial = float(v_ini.replace(',','.'))
            st.rerun()
        except: st.error("Insira o valor do troco inicial.")
    st.stop()

if not st.session_state.configurado:
    st.title("⚙️ Cardápio")
    sabores_op = ["Pilsen", "IPA", "Vinho", "Weiss", "Black", "Água", "Refrigerante"]
    selec = st.multiselect("Sabores:", sabores_op, default=["Pilsen", "IPA"])
    temp_c = {}
    for s in selec:
        p = st.text_input(f"Preço {s}:", value="", placeholder="15.00", key=f"pre_{s}")
        try: temp_c[s] = float(p.replace(',','.')) if p else 0.0
        except: temp_c[s] = 0.0
    if st.button("INICIAR VENDAS"):
        st.session_state.cardapio = temp_c
        st.session_state.configurado = True
        st.rerun()
    st.stop()

st.markdown(f"<div class='status-caixa'>🍻 SEVEN DWARFS BEER | PDV</div>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["🛒 VENDER", "🔄 ESTORNO", "📊 FECHAMENTO"])

with t1:
    cv, cc = st.columns([1.5, 1])
    with cv:
        st.write("### Cardápio")
        cols = st.columns(2)
        for i, (n, p) in enumerate(st.session_state.cardapio.items()):
            if cols[i%2].button(f"{n}\nR$ {p:.2f}", key=f"v_{n}", use_container_width=True):
                if n in st.session_state.carrinho: st.session_state.carrinho[n]['qtd'] += 1
                else: st.session_state.carrinho[n] = {'preco': p, 'qtd': 1}
                st.rerun()
    
    with cc:
        st.write("### Carrinho")
        total = 0.0
        if not st.session_state.carrinho: st.info("Carrinho vazio")
        else:
            for n, it in list(st.session_state.carrinho.items()):
                total += it['preco'] * it['qtd']
                c_c1, c_c2 = st.columns([3, 1])
                c_c1.write(f"**{it['qtd']}x {n}**")
                if c_c2.button("🗑️", key=f"del_{n}"):
                    del st.session_state.carrinho[n]
                    st.rerun()
            
            st.markdown(f"## Total: R$ {total:.2f}")
            
            m_final = None
            c_pg = st.columns(2)
            if c_pg[0].button("PIX", use_container_width=True): m_final = "PIX"
            if c_pg[1].button("DÉBITO", use_container_width=True): m_final = "Débito"
            if c_pg[0].button("CRÉDITO", use_container_width=True): m_final = "Crédito"
            if c_pg[1].button("DINHEIRO", use_container_width=True): st.session_state.show_dinheiro = True
            
            if st.session_state.show_dinheiro:
                st.divider()
                rec = st.text_input("Valor Recebido:", value="", placeholder="0.00", key=f"rec_{len(st.session_state.vendas)}")
                if rec:
                    try:
                        tr = float(rec.replace(',','.')) - total
                        if tr >= 0:
                            st.markdown(f"<div class='troco-box'>TROCO: R$ {tr:.2f}</div>", unsafe_allow_html=True)
                            if st.button("CONFIRMAR DINHEIRO", type="primary", use_container_width=True):
                                m_final = "Dinheiro"
                                st.session_state.show_dinheiro = False
                        else: st.error("Valor insuficiente")
                    except: pass

            if m_final:
                v_id = int(datetime.now().timestamp())
                for n, it in st.session_state.carrinho.items():
                    for _ in range(it['qtd']):
                        st.session_state.vendas.append({"id_venda": v_id, "Sabor": n, "Valor": it['preco'], "Tipo": m_final, "Hora": datetime.now().strftime("%H:%M")})
                        st.session_state.fichas_pendentes.append(gerar_ficha_imagem(n, v_id, m_final))
                st.session_state.carrinho = {}
                st.rerun()
        
        if st.session_state.fichas_pendentes:
            st.divider()
            if st.button("🔥 IMPRIMIR TUDO", type="primary", use_container_width=True):
                for f in st.session_state.fichas_pendentes: st.image(f)
                st.session_state.fichas_pendentes = []

with t2:
    st.write("### 🔄 Estorno por Item")
    if not st.session_state.vendas: st.info("Sem vendas.")
    else:
        df_v = pd.DataFrame(st.session_state.vendas)
        ids = df_v['id_venda'].unique()
        v_sel = st.selectbox("ID da Venda:", ids, format_func=lambda x: f"Venda {str(x)[-5:]}")
        itens_v = [v for v in st.session_state.vendas if v['id_venda'] == v_sel]
        
        c_e1, c_e2 = st.columns(2)
        if c_e1.button("Marcar Todos"): st.session_state.sel_todos_estorno = True; st.rerun()
        if c_e2.button("Desmarcar Todos"): st.session_state.sel_todos_estorno = False; st.rerun()

        remover = []
        for idx, it in enumerate(itens_v):
            if st.checkbox(f"{it['Sabor']} (R$ {it['Valor']:.2f})", value=st.session_state.sel_todos_estorno, key=f"est_{v_sel}_{idx}"):
                remover.append(it)
        
        if remover:
            if st.button(f"ESTORNAR {len(remover)} SELECIONADOS", type="primary"):
                for r in remover: st.session_state.vendas.remove(r)
                st.session_state.sel_todos_estorno = False
                st.success("Estorno concluído!")
                st.rerun()

with t3:
    st.write("### 📊 Fechamento Detalhado")
    if st.session_state.vendas:
        df_f = pd.DataFrame(st.session_state.vendas)
        v_pix = df_f[df_f['Tipo'] == 'PIX']['Valor'].sum()
        v_deb = df_f[df_f['Tipo'] == 'Débito']['Valor'].sum()
        v_cre = df_f[df_f['Tipo'] == 'Crédito']['Valor'].sum()
        v_din = df_f[df_f['Tipo'] == 'Dinheiro']['Valor'].sum()
        
        # Dashboard de Métricas
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("PIX", f"R$ {v_pix:.2f}")
        c2.metric("DÉBITO", f"R$ {v_deb:.2f}")
        c3.metric("CRÉDITO", f"R$ {v_cre:.2f}")
        c4.metric("DINHEIRO", f"R$ {st
