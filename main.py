import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Seven Dwarfs - PDV", layout="wide")

# --- FUNÇÃO PARA GERAR A FICHA (AJUSTADA) ---
def gerar_ficha_imagem(sabor, id_venda, pagto):
    img = Image.new('RGB', (300, 900), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    y = 20 

    logo_file = "logo.png"
    if os.path.exists(logo_file):
        try:
            logo = Image.open(logo_file).convert("RGBA")
            largura_logo = 100
            w_percent = (largura_logo / float(logo.size[0]))
            h_size = int((float(logo.size[1]) * float(w_percent)))
            logo = logo.resize((largura_logo, h_size), Image.Resampling.LANCZOS)
            img.paste(logo, ((300 - largura_logo) // 2, y), logo)
            y += h_size + 20
        except: y += 20
    
    def get_font(size):
        font_paths = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
        ]
        for path in font_paths:
            if os.path.exists(path): return ImageFont.truetype(path, size)
        try: return ImageFont.truetype("LiberationSans-Bold.ttf", size)
        except: return ImageFont.load_default()

    f_sabor = get_font(95)
    f_info = get_font(24)
    f_peq = get_font(16)

    d.line([(10, y), (290, y)], fill=(0,0,0), width=6)
    y += 100 
    d.text((150, y), sabor.upper(), fill=(0,0,0), font=f_sabor, anchor="ms")
    y += 20
    d.line([(10, y), (290, y)], fill=(0,0,0), width=6)
    
    y += 60
    d.text((150, y), f"VENDA ID: {str(id_venda)[-5:]}", fill=(0,0,0), font=f_info, anchor="ms")
    y += 40
    d.text((150, y), f"PAGAMENTO: {pagto.upper()}", fill=(0,0,0), font=f_info, anchor="ms")
    
    y += 70
    data_str = datetime.now().strftime("%d/%m/%Y - %H:%M")
    d.text((150, y), f"Emitido em: {data_str}", fill=(0,0,0), font=f_peq, anchor="ms")
    y += 30
    d.text((150, y), "Válido apenas na data de emissão", fill=(0,0,0), font=f_peq, anchor="ms")
    y += 20
    d.text((150, y), "durante o evento", fill=(0,0,0), font=f_peq, anchor="ms")
    y += 30
    d.text((150, y), "Seven Dwarfs a verdadeira delícia gelada", fill=(0,0,0), font=f_peq, anchor="ms")
    y += 30
    d.text((150, y), "BEBA COM MODERAÇÃO", fill=(0,0,0), font=f_peq, anchor="ms")
    y += 40
    d.text((150, y), "---------------------------", fill=(0,0,0), anchor="ms")

    return img.crop((0, 0, 300, y + 20))

# --- INICIALIZAÇÃO ---
if 'vendas' not in st.session_state: st.session_state.vendas = []
if 'caixa_inicial' not in st.session_state: st.session_state.caixa_inicial = None
if 'cardapio' not in st.session_state: st.session_state.cardapio = {}
if 'configurado' not in st.session_state: st.session_state.configurado = False
if 'fichas_pendentes' not in st.session_state: st.session_state.fichas_pendentes = []
if 'carrinho' not in st.session_state: st.session_state.carrinho = {}
if 'show_dinheiro' not in st.session_state: st.session_state.show_dinheiro = False
if 'show_desconto' not in st.session_state: st.session_state.show_desconto = False
if 'sel_todos_estorno' not in st.session_state: st.session_state.sel_todos_estorno = False

st.markdown("""<style>div.stButton > button { height: 5em; font-size: 16px; font-weight: bold; border-radius: 10px; margin-bottom: 5px; white-space: pre-wrap; }</style>""", unsafe_allow_html=True)

# --- ABERTURA ---
if st.session_state.caixa_inicial is None:
    st.title("🚀 Abertura Seven Dwarfs")
    v_ini = st.number_input("Troco Inicial (R$):", min_value=0.0, step=1.0, format="%.2f")
    if st.button("CONFIRMAR E IR PARA CARDÁPIO", use_container_width=True):
        st.session_state.caixa_inicial = v_ini; st.rerun()
    st.stop()

if not st.session_state.configurado:
    st.title("⚙️ Configurar Preços")
    opcoes = ["Pilsen", "IPA", "Vinho", "Weiss", "Black", "Água", "Refrigerante"]
    selecionados = st.multiselect("Sabores de Hoje:", opcoes, default=["Pilsen", "IPA"])
    temp_card = {}
    for s in selecionados:
        temp_card[s] = st.number_input(f"Preço {s}:", min_value=0.0, step=0.5, format="%.2f", key=f"pre_{s}")
    if st.button("INICIAR VENDAS", type="primary", use_container_width=True):
        st.session_state.cardapio = temp_card; st.session_state.configurado = True; st.rerun()
    st.stop()

# --- INTERFACE ---
st.markdown(f"### 🍻 SEVEN DWARFS BEER | PDV")
t1, t2, t3 = st.tabs(["🛒 VENDER", "🔄 ESTORNO", "📊 FECHAMENTO"])

with t1:
    cv, cc = st.columns([1.5, 1])
    with cv:
        cols = st.columns(2)
        for i, (n, p) in enumerate(st.session_state.cardapio.items()):
            if cols[i%2].button(f"{n}\nR$ {p:.2f}", key=f"v_{n}", use_container_width=True):
                if n in st.session_state.carrinho: st.session_state.carrinho[n]['qtd'] += 1
                else: st.session_state.carrinho[n] = {'preco': p, 'qtd': 1}
                st.rerun()
    
    with cc:
        st.write("### Carrinho")
        total_venda = sum(it['preco'] * it['qtd'] for it in st.session_state.carrinho.values())
        if not st.session_state.carrinho: st.info("Vazio")
        else:
            for n, it in list(st.session_state.carrinho.items()):
                c_item, c_del = st.columns([4, 1])
                c_item.write(f"**{it['qtd']}x {n}**")
                if c_del.button("🗑️", key=f"del_{n}"): del st.session_state.carrinho[n]; st.rerun()
            
            st.markdown(f"## Total Original: R$ {total_venda:.2f}")
            m_final = None
            v_cobrado = total_venda
            
            c_pg = st.columns(2)
            if c_pg[0].button("PIX", use_container_width=True): m_final = "PIX"
            if c_pg[1].button("DÉBITO", use_container_width=True): m_final = "Débito"
            if c_pg[0].button("CRÉDITO", use_container_width=True): m_final = "Crédito"
            if c_pg[1].button("DINHEIRO", use_container_width=True): st.session_state.show_dinheiro = True
            
            c_extra = st.columns(2)
            if c_extra[0].button("🎁 CORTESIA", use_container_width=True): m_final = "Cortesia"
            if c_extra[1].button("🏷️ DESCONTO", use_container_width=True): st.session_state.show_desconto = True

            # Opção de Dinheiro com Troco
            if st.session_state.show_dinheiro:
                rec_val = st.number_input("Valor Recebido:", min_value=0.0, key="rec_din")
                if rec_val >= total_venda:
                    st.success(f"Troco: R$ {rec_val - total_venda:.2f}")
                    if st.button("CONFIRMAR DINHEIRO", use_container_width=True): 
                        m_final = "Dinheiro"; st.session_state.show_dinheiro = False
            
            # Opção de Desconto com Valor Manual
            if st.session_state.show_desconto:
                st.divider()
                v_cobrado = st.number_input("VALOR FINAL A COBRAR (R$):", min_value=0.0, max_value=total_venda, value=total_venda, key="desc_val")
                metodo_desc = st.selectbox("Forma de Pagto (com desconto):", ["Dinheiro", "PIX", "Débito", "Crédito"])
                if st.button("CONFIRMAR VALOR COM DESCONTO", type="primary", use_container_width=True):
                    m_final = metodo_desc; st.session_state.show_desconto = False

            if m_final:
                v_id = int(datetime.now().timestamp())
                total_itens = sum(it['qtd'] for it in st.session_state.carrinho.values())
                # Se for desconto, o valor de cada item é o valor cobrado dividido pelo total de itens
                valor_por_item = v_cobrado / total_itens if m_final != "Cortesia" else 0.0
                
                for n, it in st.session_state.carrinho.items():
                    for _ in range(it['qtd']):
                        st.session_state.vendas.append({
                            "id_venda": v_id, "Sabor": n, "Valor": valor_por_item, 
                            "Tipo": m_final, "Hora": datetime.now().strftime("%H:%M")
                        })
                        st.session_state.fichas_pendentes.append(gerar_ficha_imagem(n, v_id, m_final))
                st.session_state.carrinho = {}; st.rerun()
        
        if st.session_state.fichas_pendentes:
            if st.button("🔥 IMPRIMIR TUDO", type="primary", use_container_width=True):
                for f in st.session_state.fichas_pendentes: st.image(f)
                st.session_state.fichas_pendentes = []

with t2:
    if not st.session_state.vendas: st.info("Sem vendas.")
    else:
        df_v = pd.DataFrame(st.session_state.vendas)
        v_sel = st.selectbox("Venda ID:", df_v['id_venda'].unique(), format_func=lambda x: f"ID {str(x)[-5:]}")
        if st.button("ESTORNAR VENDA SELECIONADA"):
            st.session_state.vendas = [v for v in st.session_state.vendas if v['id_venda'] != v_sel]
            st.success("Estornado!"); st.rerun()

with t3:
    if st.session_state.vendas:
        df_f = pd.DataFrame(st.session_state.vendas)
        resumo = df_f.groupby('Tipo')['Valor'].sum()
        st.write("### Resumo Financeiro")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("PIX", f"R$ {resumo.get('PIX', 0):.2f}")
        c2.metric("DÉBITO", f"R$ {resumo.get('Débito', 0):.2f}")
        c3.metric("CRÉDITO", f"R$ {resumo.get('Crédito', 0):.2f}")
        c4.metric("DINHEIRO", f"R$ {st.session_state.caixa_inicial + resumo.get('Dinheiro', 0):.2f}")
        st.write(f"**Cortesias:** {len(df_f[df_f['Tipo']=='Cortesia'])} unidades")
    if st.button("ZERAR TUDO"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
