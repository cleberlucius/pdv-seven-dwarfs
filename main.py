import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Seven Dwarfs - PDV", layout="wide")

# --- FUNÇÃO PARA GERAR A FICHA ---
def gerar_ficha_imagem(sabor, id_venda, pagto):
    largura = 300
    altura_estimada = 1200 
    img = Image.new('RGB', (largura, altura_estimada), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    def get_font(size, bold=True):
        if bold:
            paths = ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        else:
            paths = ["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        for path in paths:
            if os.path.exists(path): return ImageFont.truetype(path, size)
        return ImageFont.load_default()

    y = 30
    logo_file = "logo.png"
    if os.path.exists(logo_file):
        try:
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((110, 110))
            img.paste(logo, ((largura - logo.size[0]) // 2, y), logo)
            y += logo.size[1] + 20
        except: y += 10

    draw.line([(15, y), (285, y)], fill=(0,0,0), width=5)
    y += 50
    
    font_size = 85
    msg_sabor = str(sabor).upper()
    while font_size > 20:
        f_temp = get_font(font_size, bold=True)
        bbox = draw.textbbox((0, 0), msg_sabor, font=f_temp)
        if (bbox[2] - bbox[0]) < 265:
            break
        font_size -= 5
    
    draw.text((largura/2, y), msg_sabor, fill=(0,0,0), font=get_font(font_size, bold=True), anchor="mm")
    
    y += 50
    draw.line([(15, y), (285, y)], fill=(0,0,0), width=5)
    y += 50

    f_info = get_font(24, bold=True)
    draw.text((largura/2, y), f"VENDA ID: {str(id_venda)[-5:]}", fill=(0,0,0), font=f_info, anchor="mm")
    y += 35
    draw.text((largura/2, y), f"PAGAMENTO: {str(pagto).upper()}", fill=(0,0,0), font=f_info, anchor="mm")
    
    y += 60 

    f_rodape = get_font(14, bold=False)
    data_str = datetime.now().strftime("%d/%m/%Y - %H:%M")
    
    mensagens = [
        f"Emitido em: {data_str}",
        "Válido apenas na data de emissão durante o evento",
        "Seven Dwarfs a verdadeira delícia gelada",
        "BEBA COM MODERAÇÃO"
    ]

    for msg in mensagens:
        linhas = textwrap.wrap(msg.upper(), width=32)
        for linha in linhas:
            draw.text((largura/2, y), linha, fill=(0,0,0), font=f_rodape, anchor="mm")
            y += 20
        y += 4 

    draw.text((largura/2, y), "--------------------------------", fill=(0,0,0), font=f_rodape, anchor="mm")
    y += 20
    return img.crop((0, 0, largura, y + 10))

# --- INICIALIZAÇÃO DE ESTADOS ---
for key in ['vendas', 'sangrias', 'fichas_pendentes']:
    if key not in st.session_state: st.session_state[key] = []

if 'cardapio' not in st.session_state: st.session_state.cardapio = {}
if 'caixa_inicial' not in st.session_state: st.session_state.caixa_inicial = 0.0
if 'configurado' not in st.session_state: st.session_state.configurado = False
if 'carrinho' not in st.session_state: st.session_state.carrinho = {}
if 'show_dinheiro' not in st.session_state: st.session_state.show_dinheiro = False
if 'show_desconto' not in st.session_state: st.session_state.show_desconto = False

st.markdown("""<style>div.stButton > button { height: 5em; font-size: 16px; font-weight: bold; border-radius: 10px; }</style>""", unsafe_allow_html=True)

# --- TELA DE CONFIGURAÇÃO ---
if st.session_state.configurado == False:
    st.title("⚙️ Gestão de Cardápio Seven Dwarfs")
    v_ini = st.number_input("Troco Inicial (R$):", min_value=0.0, format="%.2f", value=st.session_state.caixa_inicial)
    
    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        opcoes_base = ["Pilsen", "IPA", "Black Jack", "Vinho", "Manga", "Morango"]
        default_base = [s for s in st.session_state.cardapio.keys() if s in opcoes_base]
        selec_base = st.multiselect("Sabores Fixos:", opcoes_base, default=default_base)
    
    with col_cfg2:
        extras_atuais_lista = [s for s in st.session_state.cardapio.keys() if s not in opcoes_base]
        extras_atuais_str = ", ".join(extras_atuais_lista)
        novos_extras = st.text_area("Adicionar Outros (Separe por vírgula):", 
                                   value=extras_atuais_str,
                                   placeholder="Ex: Água, Refrigerante, Suco")

    lista_extras = [s.strip() for s in novos_extras.split(",") if s.strip()]
    lista_final = selec_base + lista_extras
    
    st.write("---")
    st.subheader("Defina os Preços:")
    temp_card = {}
    
    if lista_final:
        cols_p = st.columns(3)
        for i, s in enumerate(lista_final):
            p_sugestao = st.session_state.cardapio.get(s, 0.0)
            temp_card[s] = cols_p[i%3].number_input(f"R$ {s}:", min_value=0.0, format="%.2f", key=f"p_{s}", value=p_sugestao)
    
    if st.button("SALVAR E ABRIR VENDAS", type="primary", use_container_width=True):
        if lista_final:
            st.session_state.caixa_inicial = v_ini
            st.session_state.cardapio = temp_card
            st.session_state.configurado = True
            st.rerun()
        else:
            st.error("Selecione pelo menos um item.")
    st.stop()

# --- INTERFACE PDV ---
st.markdown("### 🍻 PDV Seven Dwarfs")
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
                rec = st.number_input("Recebido:", min_value=0.0, key="rec_dinheiro")
                if rec >= total_venda:
                    st.success(f"Troco: R$ {rec-total_venda:.2f}")
                    if st.button("CONFIRMAR DINHEIRO"): m_final = "Dinheiro"; st.session_state.show_dinheiro = False
            
            if st.session_state.show_desconto:
                v_cobrado = st.number_input("VALOR FINAL:", min_value=0.0, value=total_venda)
                f_desc = st.selectbox("Forma:", ["Dinheiro", "PIX", "Débito", "Crédito"])
                if st.button("APLICAR"): m_final = f_desc; st.session_state.show_desconto = False

            if m_final:
                v_id = int(datetime.now().timestamp())
                qtd_t = sum(it['qtd'] for it in st.session_state.carrinho.values())
                v_item = (v_cobrado / qtd_t) if (m_final != "Cortesia" and qtd_t > 0) else 0.0
                for n, it in st.session_state.carrinho.items():
                    for _ in range(it['qtd']):
                        st.session_state.vendas.append({"id_venda": v_id, "Sabor": n, "Valor": v_item, "Tipo": m_final, "Hora": datetime.now().strftime("%H:%M")})
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
        v_sel = st.selectbox("ID Venda:", df_v['id_venda'].unique(), format_func=lambda x: f"Venda {str(x)[-5:]}")
        itens_v = [v for v in st.session_state.vendas if v['id_venda'] == v_sel]
        for idx, item in enumerate(itens_v):
            col_est1, col_est2 = st.columns([3, 1])
            col_est1.write(f"{item['Sabor']} - R$ {item['Valor']:.2f}")
            if col_est2.button("Estornar", key=f"est_btn_{v_sel}_{idx}"):
                st.session_state.vendas.remove(item)
                st.success("Item removido!")
                st.rerun()

with t3:
    df_f = pd.DataFrame(st.session_state.vendas) if st.session_state.vendas else pd.DataFrame(columns=['Tipo', 'Valor'])
    def sm(t): return df_f[df_f['Tipo'] == t]['Valor'].sum()
    total_sang = sum(s['valor'] for s in st.session_state.sangrias)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PIX", f"R$ {sm('PIX'):.2f}")
    c2.metric("CARTÃO", f"R$ {sm('Débito')+sm('Crédito'):.2f}")
    c3.metric("GAVETA", f"R$ {(st.session_state.caixa_inicial + sm('Dinheiro')) - total_sang:.2f}")
    c4.metric("CORTESIAS", f"{len(df_f[df_f['Tipo']=='Cortesia'])} un")

    st.divider()
    cs1, cs2 = st.columns(2)
    with cs1:
        st.write("#### 💸 Sangria")
        v_s = st.number_input("Valor Sangria:", min_value=0.0, key="val_sangria")
        m_s = st.text_input("Motivo:", key="mot_sangria")
        if st.button("REGISTRAR SANGRIA"):
            st.session_state.sangrias.append({"valor": v_s, "motivo": m_s})
            st.success("Sangria registrada!")
            st.rerun()
    with cs2:
        if st.button("EDITAR CARDÁPIO", use_container_width=True): st.session_state.configurado = False; st.rerun()
        if st.button("ZERAR TUDO", type="secondary", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
