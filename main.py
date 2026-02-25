import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PDV Seven Dwarfs", layout="wide")

# --- BANCO DE DADOS (PERSISTÊNCIA) ---
ARQUIVO_VENDAS = "vendas_consolidado.csv"

if 'vendas' not in st.session_state:
    if os.path.exists(ARQUIVO_VENDAS):
        st.session_state.vendas = pd.read_csv(ARQUIVO_VENDAS).to_dict('records')
    else:
        st.session_state.vendas = []

# --- INTERFACE ---
st.title("🍺 Chopp Seven Dwarfs - PDV")

# Sidebar para o Cardápio Fixo
st.sidebar.header("Tabela de Preços")
cardapio = {
    "Pilsen": 10.00, "IPA": 15.00, "Black Jack": 15.00, 
    "Vinho": 12.00, "Manga": 13.00
}
for item, preco in cardapio.items():
    st.sidebar.write(f"**{item}:** R$ {preco:.2f}")

# --- ÁREA DE VENDAS ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🛒 Novo Pedido")
    selecao = st.selectbox("Escolha a Bebida", list(cardapio.keys()) + ["Manual"])
    
    if selecao == "Manual":
        item_nome = st.text_input("Nome do Item")
        preco_unit = st.number_input("Preço Unitário", min_value=0.0, format="%.2f")
    else:
        item_nome = selecao
        preco_unit = cardapio[selecao]

    qtd = st.number_input("Quantidade", min_value=1, value=1)
    
    if st.button("Adicionar ao Carrinho"):
        novo_item = {
            "item": item_nome,
            "qtd": qtd,
            "preco_unit": preco_unit,
            "subtotal": preco_unit * qtd
        }
        if 'carrinho' not in st.session_state:
            st.session_state.carrinho = []
        st.session_state.carrinho.append(novo_item)
        st.success(f"{item_nome} adicionado!")

with col2:
    st.subheader("📋 Carrinho")
    if 'carrinho' in st.session_state and st.session_state.carrinho:
        df_carrinho = pd.DataFrame(st.session_state.carrinho)
        st.table(df_carrinho[['item', 'qtd', 'subtotal']])
        
        total = df_carrinho['subtotal'].sum()
        st.write(f"### TOTAL: R$ {total:.2f}")
        
        # Pagamento
        metodo = st.selectbox("Forma de Pagamento", ["PIX", "DEBITO", "CREDITO", "DINHEIRO", "CORTESIA", "CONTA"])
        
        if metodo == "DINHEIRO":
            recebido = st.number_input("Valor Recebido", min_value=total)
            st.write(f"**Troco: R$ {recebido - total:.2f}**")
            
        if st.button("Finalizar Venda"):
            # Lógica de salvar
            venda_id = len(st.session_state.vendas) + 1
            dados_venda = {
                "id": venda_id,
                "total": total,
                "metodo": metodo,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            st.session_state.vendas.append(dados_venda)
            pd.DataFrame(st.session_state.vendas).to_csv(ARQUIVO_VENDAS, index=False)
            
            st.balloons()
            st.success("Venda Finalizada!")
            st.session_state.carrinho = [] # Limpa carrinho
    else:
        st.info("Carrinho vazio")

# --- RELATÓRIO RÁPIDO ---
st.divider()
st.subheader("📊 Resumo do Dia")
if st.session_state.vendas:
    st.dataframe(pd.DataFrame(st.session_state.vendas))
