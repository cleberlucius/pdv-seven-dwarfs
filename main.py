import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Seven Dwarfs - PDV", layout="wide")

# --- FUNÇÕES DE BACKUP ---
CSV_FILE = "vendas_backup.csv"

def salvar_venda_csv(venda_dict):
    df = pd.DataFrame([venda_dict])
    if not os.path.isfile(CSV_FILE):
        df.to_csv(CSV_FILE, index=False)
    else:
        df.to_csv(CSV_FILE, mode='a', header=False, index=False)

def carregar_backup():
    if os.path.exists(CSV_FILE):
        try:
            return pd.read_csv(CSV_FILE).to_dict('records')
        except:
            return []
    return []

# --- FUNÇÃO PARA GERAR A FICHA ---
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
        font_paths = ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"]
        for path in font_paths:
            if os.path.exists(path): return ImageFont.truetype(path, size)
        try: return ImageFont.truetype("LiberationSans-Bold.ttf", size)
        except: return ImageFont.load_default()

    f_sabor = get_font(95); f_info = get_font(24); f_peq = get_font(16)
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
    d.text((150, y), "Válido apenas na data de emissão durante o evento", fill=(0,0,0), font=f_peq, anchor="ms")
    y += 30
    d.text((150, y), "Seven Dwarfs a verdadeira delícia gelada", fill=(0,0,0), font=f_peq, anchor="ms")
    y += 30
    d.text((150, y), "BEBA COM MODERAÇÃO", fill=(0,0,0), font=f_peq, anchor="ms")
    y += 40
    d.text((150, y), "---------------------------", fill=(0,0,0), anchor="ms")
    return img.crop((0, 0, 300, y + 20))

# --- INICIALIZAÇÃO ---
if 'vendas' not in st.session_state: 
    st.session_state.vendas = carregar_backup()
if 'caixa_inicial' not in st.session_state: st.session_state.caixa_inicial = 0.0
if 'cardapio' not in st.session_state: st.session_state.cardapio = {}
if 'configurado' not in st.session_state: st.session_state.configurado = False
if 'fichas_pendentes' not in st.session_state: st.session_state.fichas_pendentes = []
if 'carrinho' not in st.session_state: st.session_state.carrinho = {}
if 'show_dinheiro' not in st.session_state: st.session_state.show_dinheiro = False
if 'show_desconto' not in st.session_state: st.session_state.show_desconto = False

st.markdown("""<style>div.stButton > button { height: 5em; font-size: 16px; font-weight: bold; border-radius: 10px; margin-bottom: 5px; white-space: pre-wrap; }</style>""", unsafe_allow_html=True)

# --- ABERTURA ---
if not st.session_state.configurado:
    st.title("🚀 Abertura Seven Dwarfs")
    v_ini = st.number_input("Troco Inicial (R$):", min_value=0.0, step=1.0, format="%.2f", value=0.0)
    st.divider()
    opcoes = ["Pilsen", "IPA", "Vinho", "Weiss", "Black", "Água", "Refrigerante"]
    selec = st.multiselect("Sabores de Hoje:", opcoes, default=["Pilsen", "IPA"])
    temp_card = {}
    for s in selec: 
        temp_card[s] = st.number_input(f"Preço {s}:", min_value=0.0, step=0.5, format="%.2f", key=f"p_{s}", value=0.0)
    
    if st.button("ABRIR CAIXA E INICIAR", type="primary", use_container_width=True):
        st.session_state.caixa_inicial = v_ini
        st.session_state.cardapio = temp_card
        st.session_state.configurado = True
        st.rerun()
    st.stop()

# --- INTERFACE PDV ---
st.markdown("### 🍻 SEVEN DWARFS BEER")
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
        total_venda = sum(it['preco'] * it['qtd'] for it in st.session_state.carrinho.values())
        if not st.session_state.carrinho: st.info("Carrinho Vazio")
        else:
            for n, it in list(st.session_state.carrinho.items()):
                c_i, c_d = st.columns([4, 1])
                c_i.write(f"**{it['qtd']}x {n}**")
                if c_d.button("🗑️", key=f"del_{n}"): del st.session_state.carrinho[n]; st.rerun()
            st.markdown(f"## Total: R$ {total_venda:.2f}")
            m_final = None; v_cobrado = total_venda
            
            c_pg = st.columns(2)
            if c_pg[0].button("PIX", use_container_width=True): m_final = "PIX"
            if c_pg[1].button("DÉBITO", use_container_width=True): m_final = "Débito"
            if c_pg[0].button("CRÉDITO", use_container_width=True): m_final = "Crédito"
            if c_pg[1].button("DINHEIRO", use_container_width=True): st.session_state.show_dinheiro = True
            
            c_ex = st.columns(2)
            if c_ex[0].button("🎁 CORTESIA", use_container_width=True): m_final = "Cortesia"
            if c_ex[1].button("🏷️ DESCONTO", use_container_width=True): st.session_state.show_desconto = True

            if st.session_state.show_dinheiro:
                rec = st.number_input("Valor Recebido:", min_value=0.0, key="din_rec", value=0.0)
                if rec >= total_venda:
                    st.success(f"Troco: R$ {rec-total_venda:.2f}")
                    if st.button("CONFIRMAR DINHEIRO"): m_final = "Dinheiro"; st.session_state.show_dinheiro = False
            
            if st.session_state.show_desconto:
                v_cobrado = st.number_input("VALOR FINAL COM DESCONTO:", min_value=0.0, value=total_venda)
                f_desc = st.selectbox("Forma Pagto:", ["Dinheiro", "PIX", "Débito", "Crédito"])
                if st.button("APLICAR DESCONTO"): m_final = f_desc; st.session_state.show_desconto = False

            if m_final:
                v_id = int(datetime.now().timestamp())
                qtd_total = sum(it['qtd'] for it in st.session_state.carrinho.values())
                valor_final_item = (v_cobrado / qtd_total) if m_final != "Cortesia" else 0.0
                for n, it in st.session_state.carrinho.items():
                    for _ in range(it['qtd']):
                        nova_venda = {"id_venda": v_id, "Sabor": n, "Valor": valor_final_item, "Tipo": m_final, "Hora": datetime.now().strftime("%H:%M")}
                        st.session_state.vendas.append(nova_venda)
                        salvar_venda_csv(nova_venda) # SALVA NO BACKUP
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
            # Atualiza o arquivo CSV após estorno
            df_atualizado = pd.DataFrame(st.session_state.vendas)
            df_atualizado.to_csv(CSV_FILE, index=False)
            st.success("Estorno realizado no backup!"); st.rerun()

with t3:
    if st.session_state.vendas:
        df_f = pd.DataFrame(st.session_state.vendas)
        def soma_tipo(t): return df_f[df_f['Tipo'] == t]['Valor'].sum()
        
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("PIX", f"R$ {soma_tipo('PIX'):.2f}")
        c2.metric("DÉBITO", f"R$ {soma_tipo('Débito'):.2f}")
        c3.metric("CRÉDITO", f"R$ {soma_tipo('Crédito'):.2f}")
        c4.metric("DINHEIRO", f"R$ {(st.session_state.caixa_inicial + soma_tipo('Dinheiro')):.2f}")
        c5.metric("CORTESIAS", f"{len(df_f[df_f['Tipo']=='Cortesia'])} Copos")
        
        st.divider()
        st.write("#### Quantidade por Sabor")
        st.table(df_f.groupby('Sabor').size().reset_index(name='Qtd'))
        
        # Botão para baixar o relatório em Excel/CSV se quiser
        st.download_button("Baixar Relatório Completo (CSV)", df_f.to_csv(index=False), "vendas_evento.csv", "text/csv")

    if st.button("ZERAR EVENTO (Limpa Backup)"):
        if os.path.exists(CSV_FILE): os.remove(CSV_FILE)
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
