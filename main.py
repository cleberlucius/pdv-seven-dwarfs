import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Seven Dwarfs PDV", layout="wide")

# --- 1. INICIALIZAÇÃO DE ESTADOS (SESSION STATE) ---
if 'vendas' not in st.session_state: st.session_state.vendas = []
if 'contas_vip' not in st.session_state: st.session_state.contas_vip = {}
if 'carrinho' not in st.session_state: st.session_state.carrinho = {}
if 'cardapio' not in st.session_state: st.session_state.cardapio = {}
if 'configurado' not in st.session_state: st.session_state.configurado = False
if 'caixa_inicial' not in st.session_state: st.session_state.caixa_inicial = 0.0
if 'fichas_pendentes' not in st.session_state: st.session_state.fichas_pendentes = []
if 'show_dinheiro' not in st.session_state: st.session_state.show_dinheiro = False
if 'show_vip' not in st.session_state: st.session_state.show_vip = False

# --- 2. PERSISTÊNCIA EM CSV (SEGURANÇA) ---
def salvar_dados():
    try:
        df_vendas = pd.DataFrame(st.session_state.vendas)
        df_vendas.to_csv("vendas_backup.csv", index=False)
        
        vips_lista = [{"nome": k, "valor": v} for k, v in st.session_state.contas_vip.items()]
        df_vip = pd.DataFrame(vips_lista)
        df_vip.to_csv("vips_backup.csv", index=False)
    except:
        pass

def carregar_dados():
    if os.path.exists("vendas_backup.csv"):
        try:
            st.session_state.vendas = pd.read_csv("vendas_backup.csv").to_dict('records')
        except: pass
    if os.path.exists("vips_backup.csv"):
        try:
            vips = pd.read_csv("vips_backup.csv")
            st.session_state.contas_vip = dict(zip(vips.nome, vips.valor))
        except: pass

# Tenta carregar backups ao iniciar
if not st.session_state.vendas and not st.session_state.contas_vip:
    carregar_dados()

# --- 3. FUNÇÃO DE GERAÇÃO DE FICHA ---
def gerar_ficha_imagem(sabor, id_venda, pagto):
    largura = 300
    img = Image.new('RGB', (largura, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    def get_f(s, b=True):
        p = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
        try: return ImageFont.truetype(p, s)
        except: return ImageFont.load_default()

    y = 20
    if os.path.exists("logo.png"):
        try:
            logo = Image.open("logo.png").convert("RGBA")
            logo.thumbnail((100, 100))
            img.paste(logo, ((largura - logo.size[0]) // 2, y), logo)
            y += logo.size[1] + 10
        except: y += 10

    draw.text((largura/2, y), str(sabor).upper(), fill=(0,0,0), font=get_f(40), anchor="mm")
    y += 50
    draw.text((largura/2, y), f"ID: {str(id_venda)[-5:]} | {str(pagto).upper()}", fill=(0,0,0), font=get_f(18), anchor="mm")
    y += 40
    
    frases = [
        "VALIDO APENAS NA DATA DE EMISSAO",
        "DURANTE A DURACAO DO EVENTO",
        "SEVEN DWARFS A VERDADEIRA DELICIA GELADA",
        "BEBA COM MODERACAO"
    ]
    for f in frases:
        linhas = textwrap.wrap(f, width=30)
        for l in linhas:
            draw.text((largura/2, y), l, fill=(0,0,0), font=get_f(12, False), anchor="mm")
            y += 15
        y += 4
    return img.crop((0, 0, largura, y + 20))

# --- 4. TELA DE CONFIGURAÇÃO (ETAPA 1) ---
if not st.session_state.configurado:
    st.title("⚙️ Configuração do Evento")
    v_ini = st.number_input("Troco Inicial (R$):", min_value=0.0, value=st.session_state.caixa_inicial)
    
    c1, c2 = st.columns(2)
    with c1:
        fixos = st.multiselect("Sabores Fixos:", ["Pilsen", "IPA", "Black Jack", "Vinho", "Manga", "Morango"])
    with c2:
        extras = st.text_area("Sazonais (separados por vírgula):", placeholder="Ex: Porter, Weiss")
    
    lista_itens = list(dict.fromkeys(fixos + [s.strip() for s in extras.split(",") if s.strip()]))
    
    if lista_itens:
        st.subheader("Defina os Preços")
        cp = st.columns(3)
        temp_card = {}
        for i, item in enumerate(lista_itens):
            p_ex = st.session_state.cardapio.get(item, 0.0)
            temp_card[item] = cp[i%3].number_input(f"R$ {item}:", min_value=0.0, value=float(p_ex), key=f"cfg_{item}")
        
        if st.button("ABRIR CAIXA", type="primary", use_container_width=True):
            st.session_state.cardapio = temp_card
            st.session_state.caixa_inicial = v_ini
            st.session_state.configurado = True
            st.rerun()
    st.stop()

# --- 5. INTERFACE PRINCIPAL (TABS) ---
t1, t2, t3 = st.tabs(["🛒 VENDAS", "🔄 ESTORNO", "📊 FECHAMENTO"])

with t1:
    col_menu, col_carrinho = st.columns([1.5, 1])
    
    with col_menu:
        st.subheader("Sabores")
        c_btns = st.columns(2)
        for i, (nome, preco) in enumerate(st.session_state.cardapio.items()):
            if c_btns[i%2].button(f"{nome}\nR$ {preco:.2f}", key=f"btn_{nome}", use_container_width=True):
                if nome in st.session_state.carrinho: st.session_state.carrinho[nome]['qtd'] += 1
                else: st.session_state.carrinho[nome] = {'preco': preco, 'qtd': 1}
                st.rerun()
        
        if st.session_state.contas_vip:
            st.write("---")
            st.subheader("Contas VIP Abertas")
            for nv, tv in st.session_state.contas_vip.items():
                st.info(f"👤 {nv}: R$ {tv:.2f}")

    with col_carrinho:
        st.subheader("Carrinho")
        total_v = 0.0
        if not st.session_state.carrinho:
            st.write("Vazio")
        else:
            for n, it in list(st.session_state.carrinho.items()):
                total_v += it['preco'] * it['qtd']
                c_n, c_q, c_d = st.columns([2, 1.5, 0.5])
                c_n.write(f"**{n}**")
                
                # Botoes + e -
                cq1, cq2, cq3 = c_q.columns(3)
                if cq1.button("-", key=f"m_{n}"):
                    st.session_state.carrinho[n]['qtd'] -= 1
                    if st.session_state.carrinho[n]['qtd'] <= 0: del st.session_state.carrinho[n]
                    st.rerun()
                cq2.write(it['qtd'])
                if cq3.button("+", key=f"p_{n}"):
                    st.session_state.carrinho[n]['qtd'] += 1
                    st.rerun()
                if c_d.button("🗑️", key=f"del_{n}"): del st.session_state.carrinho[n]; st.rerun()
            
            st.divider()
            st.markdown(f"### TOTAL: R$ {total_v:.2f}")
            
            # Pagamentos
            metodo = None
            p1, p2
