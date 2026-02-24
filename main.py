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

# --- FUNÇÃO PARA GERAR A FICHA (AJUSTE DE TAMANHO) ---
def gerar_ficha_imagem(sabor, id_venda, pagto):
    img = Image.new('RGB', (300, 800), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    y = 20 

    # 1. Logo MENOR (Reduzido para 180px de largura)
    logo_file = "logo.png"
    if os.path.exists(logo_file):
        try:
            logo = Image.open(logo_file).convert("RGBA")
            canvas = Image.new("RGBA", logo.size, (255, 255, 255))
            canvas.paste(logo, mask=logo.split()[3])
            logo = canvas.convert("L") 
            largura_logo = 160 # Logo menor para dar espaço ao sabor
            w_percent = (largura_logo / float(logo.size[0]))
            h_size = int((float(logo.size[1]) * float(w_percent)))
            logo = logo.resize((largura_logo, h_size), Image.Resampling.LANCZOS)
            img.paste(logo, ((300 - largura_logo) // 2, y))
            y += h_size + 20
        except:
            y += 40
    
    # Fontes
    try:
        f_sabor = ImageFont.truetype("arialbd.ttf", 85) # SABOR MUITO GRANDE
        f_media = ImageFont.truetype("arialbd.ttf", 22)
        f_pequena = ImageFont.truetype("arial.ttf", 16)
    except:
        f_sabor = f_media = f_pequena = ImageFont.load_default()

    # Sabor em DESTAQUE
    d.line([(10, y), (290, y)], fill=(0,0,0), width=4)
    y += 90
    d.text((150, y), sabor.upper(), fill=(0,0,0), font=f_sabor, anchor="ms")
    y += 30
    d.line([(10, y), (290, y)], fill=(0,0,0), width=4)
    y += 60

    # Infos da Venda
    d.text((150, y), f"VENDA ID: {id_venda:04d}", fill=(0,0,0), font=f_media, anchor="ms")
    y += 35
    d.text((150, y), f"PAGAMENTO: {pagto.upper()}", fill=(0,0,0), font=f_media, anchor="ms")
    y += 80

    # Rodapé corrigido
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

# --- INTERFACE PDV ---
if st.session_state.caixa_inicial is None:
    st.title("🚀 Abertura Seven Dwarfs")
    v_ini_str = st.text_input("Troco Inicial (R$):", value="0.00")
    if st.button("DEFINIR CARDÁPIO", use_container_width=True):
        try:
            st.session_state.caixa_inicial = float(v_ini_str.replace(',', '.'))
            st.rerun()
        except: st.error("Valor inválido.")
    st.stop()

if not st.session_state.configurado:
    st.title("⚙️ Cardápio")
    lista_opcoes = ["Pilsen", "IPA", "Black Jack", "Vinho", "Manga", "Weiss", "Red Ale", "Sour", "Água", "Refrigerante"]
    selecionados = st.multiselect("Sabores de hoje:", lista_opcoes, default=["Pilsen", "IPA"])
    temp_card = {}
    c_p = st.columns(2)
    for i, s in enumerate(selecionados):
        p_str = c_p[i % 2].text_input(f"Preço {s} (R$):", value="15.00", key=f"preco_input_{s}")
        try: temp_card[s] = float(p_str.replace(',', '.'))
        except: temp_card[s] = 0.0
            
    if st.button("ABRIR VENDAS", use_container_width=True, type="primary"):
        if temp_card:
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
                subtotal = item['preco'] * item['qtd']
                total_venda += subtotal
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
                # KEY DINAMICA PARA LIMPEZA AUTOMÁTICA
                recebido_str = st.text_input("Valor Recebido (R$):", value=str(total_venda), key=f"dinheiro_{len(st.session_state.vendas)}")
                try:
                    val_recebido = float(recebido_str.replace(',', '.'))
                    troco = val_recebido - total_venda
                    if troco >= 0:
                        st.markdown(f"<div class='troco-box'>TROCO: R$ {troco:.2f}</div>", unsafe_allow_html=True)
                        if st.button("CONFIRMAR E IMPRIMIR", type="primary", use_container_width=True):
                            metodo_final = "Dinheiro"
                            st.session_state.show_dinheiro = False
                    else: st.error("Valor insuficiente!")
                except: pass

            if metodo_final:
                pid = len(st.session_state.vendas) + 1
                for n, i in st.session_state.carrinho.items():
                    st.session_state.vendas.append({"id": pid, "Sabor": n, "Qtd": i['qtd'], "Total": i['preco']*i['qtd'], "Tipo": metodo_final, "Hora": datetime.now().strftime("%H:%M")})
                    for _ in range(i['qtd']): st.session_state.fichas_pendentes.append(gerar_ficha_imagem(n, pid, metodo_final))
                st.session_state.carrinho = {}
                st.rerun()

        st.divider()
        if st.session_state.fichas_pendentes:
            if st.button("IMPRIMIR TUDO", use_container_width=True, type="primary"):
                for img in st.session_state.fichas_pendentes: st.image(img)
                st.session_state.fichas_pendentes = []

# --- ABA DE ESTORNO (CORRIGIDA) ---
with t3:
    st.write("### Cancelar Venda")
    if not st.session_state.vendas:
        st.info("Nenhuma venda realizada ainda.")
    else:
        df_estorno = pd.DataFrame(st.session_state.vendas)
        # Mostra apenas as IDs únicas para não repetir
        vendas_unicas = df_estorno.drop_duplicates(subset=['id'])
        id_selecionada = st.selectbox("Selecione a Venda pelo ID:", vendas_unicas['id'], format_func=lambda x: f"Venda {x:04d}")
        
        if st.button("Confirmar Estorno desta Venda", type="primary"):
            st.session_state.vendas = [v for v in st.session_state.vendas if v['id'] != id_selecionada]
            st.success(f"Venda {id_selecionada:04d} estornada com sucesso!")
            st.rerun()

# --- ABA DE SANGRIA E FECHAMENTO ---
with t2:
    v_s_str = st.text_input("Valor Retirada (R$):", value="0.00", key="sangria_val")
    m_s = st.text_input("Motivo:")
    if st.button("Salvar Sangria"):
        try:
            val_s = float(v_s_str.replace(',', '.'))
            if val_s > 0: 
                st.session_state.sangrias.append({"Hora": datetime.now().strftime("%H:%M"), "Motivo": m_s, "Valor": val_s})
                st.success("Sangria realizada!")
                st.rerun()
        except: st.error("Valor inválido.")

with t4:
    st.write("### Resumo do Período")
    if st.session_state.vendas:
        df_f = pd.DataFrame(st.session_state.vendas)
        v_pix = df_f[df_f['Tipo'] == 'PIX']['Total'].sum()
        v_deb = df_f[df_f['Tipo'] == 'Débito']['Total'].sum()
        v_cre = df_f[df_f['Tipo'] == 'Crédito']['Total'].sum()
        v_din = df_f[df_f['Tipo'] == 'Dinheiro']['Total'].sum()
        s_tot = sum(s['Valor'] for s in st.session_state.sangrias)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("PIX", f"R$ {v_pix:.2f}")
        c2.metric("CARTÕES", f"R$ {v_deb + v_cre:.2f}")
        c3.metric("DINHEIRO EM MÃO", f"R$ {st.session_state.caixa_inicial + v_din - s_tot:.2f}")
        
        st.write("---")
        st.write("#### Detalhamento por Sabor")
        st.table(df_f.groupby('Sabor')['Qtd'].sum())
    
    if st.button("FECHAR EVENTO (ZERAR TUDO)"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
