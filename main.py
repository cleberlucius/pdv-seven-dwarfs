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
if 'show_desconto' not in st.session_state: st.session_state.show_desconto = False

# --- FUNÇÃO PARA GERAR A FICHA (ESTRUTURA ORIGINAL) ---
def gerar_ficha_imagem(sabor, id_venda, pagto):
    largura = 300
    altura_estimada = 1100 
    img = Image.new('RGB', (largura, altura_estimada), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    def get_font(size, bold=True):
        paths = ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        if not bold:
            paths = ["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        for path in paths:
            if os.path.exists(path): return ImageFont.truetype(path, size)
        return ImageFont.load_default()

    y = 30
    # Lógica do Logo
    if os.path.exists("logo.png"):
        try:
            logo = Image.open("logo.png").convert("RGBA")
            logo.thumbnail((120, 120))
            img.paste(logo, ((largura - logo.size[0]) // 2, y), logo)
            y += logo.size[1] + 20
        except: y += 10

    draw.line([(15, y), (285, y)], fill=(0,0,0), width=5)
    y += 50
    
    # Sabor com auto-ajuste
    font_size = 85
    msg_sabor = str(sabor).upper()
    while font_size > 20:
        f_temp = get_font(font_size, bold=True)
        bbox = draw.textbbox((0, 0), msg_sabor, font=f_temp)
        if (bbox[2] - bbox[0]) < 265: break
        font_size -= 5
    
    draw.text((largura/2, y), msg_sabor, fill=(0,0,0), font=get_font(font_size, bold=True), anchor="mm")
    y += 50
    draw.line([(15, y), (285, y)], fill=(0,0,0), width=5)
    y += 50

    # Informações Técnicas
    draw.text((largura/2, y), f"VENDA ID: {str(id_venda)[-5:]}", fill=(0,0,0), font=get_font(24, bold=True), anchor="mm")
    y += 35
    draw.text((largura/2, y), f"PAGAMENTO: {str(pagto).upper()}", fill=(0,0,0), font=get_font(24, bold=True), anchor="mm")
    y += 60 

    # Rodapé Completo
    f_rodape = get_font(14, bold=False)
    data_str = datetime.now().strftime("%d/%m/%Y - %H:%M")
    mensagens = [
        f"Emitido em: {data_str}",
        "Valido apenas na data de emissao",
        "Seven Dwarfs a verdadeira delicia gelada",
        "BEBA COM MODERACAO"
    ]

    for msg in mensagens:
        linhas = textwrap.wrap(msg.upper(), width=32)
        for linha in linhas:
            draw.text((largura/2, y), linha, fill=(0,0,0), font=f_rodape, anchor="mm")
            y += 20
        y += 4 

    draw.text((largura/2, y), "---------------------------", fill=(0,0,0), font=f_rodape, anchor="mm")
    return img.crop((0, 0, largura, y + 20))

st.markdown("""<style>div.stButton > button { height: 4.5em; font-size: 16px; font-weight: bold; border-radius: 10px; }</style>""", unsafe_allow_html=True)

# --- TELA DE CONFIGURAÇÃO (PRESERVANDO CARDÁPIO) ---
if st.session_state.configurado == False:
    st.title("⚙️ Gestão de Cardápio Seven Dwarfs")
    v_ini = st.number_input("Troco Inicial (R$):", min_value=0.0, value=st.session_state.caixa_inicial)
    
    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        opcoes_base = ["Pilsen", "IPA", "Black Jack", "Vinho", "Manga", "Morango"]
        selec_base = st.multiselect("Sabores Fixos:", opcoes_base)
    
    with col_cfg2:
        extras_nomes = [s for s in st.session_state.cardapio.keys() if s not in opcoes_base]
        novos_extras = st.text_area("Outros (Separe por vírgula):", value=", ".join(extras_nomes))

    lista_total = list(dict.fromkeys(selec_base + [s.strip() for s in novos_extras.split(",") if s.strip()]))
    
    st.write("---")
    if lista_total:
        st.subheader("Defina os Preços:")
        cols_p = st.columns(3)
        temp_card = {}
        for i, s in enumerate(lista_total):
            p_existente = st.session_state.cardapio.get(s, 0.0)
            temp_card[s] = cols_p[i%3].number_input(f"Preço {s}:", min_value=0.0, value=float(p_existente), key=f"cfg_{s}")
        st.session_state.cardapio = temp_card
    
    if st.button("SALVAR E ABRIR CAIXA", type="primary", use_container_width=True):
        if lista_total:
            st.session_state.caixa_inicial = v_ini
            st.session_state.configurado = True
            st.rerun()
    st.stop()

# --- INTERFACE PDV ---
st.markdown("### 🍻 PDV Seven Dwarfs")
t1, t2, t3 = st.tabs(["🛒 VENDER", "🔄 ESTORNO", "📊 FECHAMENTO"])

with t1:
    cv, cc = st.columns([1.5, 1])
    with cv:
        cols = st.columns(2)
        for i, (n, p) in enumerate(st.session_state.cardapio.items()):
            if cols[i%2].button(f"{n}\nR$ {p:.2f}", key=f"btn_v_{n}", use_container_width=True):
                if n in st.session_state.carrinho: st.session_state.carrinho[n]['qtd'] += 1
                else: st.session_state.carrinho[n] = {'preco': p, 'qtd': 1}
                st.rerun()
    with cc:
        total = sum(it['preco'] * it['qtd'] for it in st.session_state.carrinho.values())
        if not st.session_state.carrinho: st.info("Carrinho Vazio")
        else:
            for n, it in list(st.session_state.carrinho.items()):
                c_i, c_d = st.columns([4, 1])
                c_i.write(f"**{it['qtd']}x {n}**")
                if c_d.button("🗑️", key=f"del_{n}"): del st.session_state.carrinho[n]; st.rerun()
            
            st.markdown(f"## Total: R$ {total:.2f}")
            m_final = None
            cp1, cp2 = st.columns(2)
            if cp1.button("PIX", key="f_pix", use_container_width=True): m_final = "PIX"
            if cp2.button("DÉBITO", key="f_deb", use_container_width=True): m_final = "Débito"
            if cp1.button("CRÉDITO", key="f_cre", use_container_width=True): m_final = "Crédito"
            if cp2.button("DINHEIRO", key="f_din", use_container_width=True): 
                st.session_state.show_dinheiro = not st.session_
