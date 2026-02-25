import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json

# --- 1. CONFIGURAÇÃO E ESTADO DO APP ---
st.set_page_config(page_title="PDV Seven Dwarfs", layout="wide")

# Inicializar variáveis de memória (evita que o app resete ao clicar em botões)
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'vendas_realizadas' not in st.session_state: st.session_state.vendas_realizadas = []
if 'contas_abertas' not in st.session_state: st.session_state.contas_abertas = {}

# --- 2. CARREGAR DADOS EXISTENTES ---
ARQUIVO_VENDAS = "vendas_seven_dwarfs.csv"
if os.path.exists(ARQUIVO_VENDAS) and not st.session_state.vendas_realizadas:
    st.session_state.vendas_realizadas = pd.read_csv(ARQUIVO_VENDAS).to_dict('records')

# --- 3. LÓGICA DE NEGÓCIO (SABORES E PREÇOS) ---
cardapio = {
    "Pilsen": 10.00, "IPA": 15.00, "Black Jack": 15.00, 
    "Vinho": 12.00, "Manga": 13.00
}

# --- 4. INTERFACE VISUAL ---
st.title("🍺 PDV Seven Dwarfs - Gestão de Eventos")

tab1, tab2, tab3 = st.tabs(["Vendas", "Contas Abertas", "Fechamento/Estorno"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Seleção de Bebidas")
        # Botões para os sabores fixos
        for sabor, preco in cardapio.items():
            if st.button(f"➕ {sabor} (R$ {preco:.2f})"):
                st.session_state.carrinho.append({"item": sabor, "qtd": 1, "preco": preco})
        
        st.divider()
        with st.expander("Adição Manual"):
            m_nome = st.text_input("Nome do Item")
            m_preco = st.number_input("Preço", min_value=0.0)
            if st.button("Adicionar Manual"):
                st.session_state.carrinho.append({"item": m_nome, "qtd": 1, "preco": m_preco})

    with col2:
        st.subheader("Carrinho / Pedido")
        if st.session_state.carrinho:
            df_c = pd.DataFrame(st.session_state.carrinho)
            st.table(df_c)
            
            total = sum(item['preco'] for item in st.session_state.carrinho)
            st.write(f"### TOTAL: R$ {total:.2f}")

            if st.button("❌ Limpar Carrinho"):
                st.session_state.carrinho = []
                st.rerun()

            st.divider()
            metodo = st.selectbox("Pagamento", ["PIX", "DEBITO", "CREDITO", "DINHEIRO", "CORTESIA", "CONTA", "DESCONTO"])
            
            # Lógica específica de pagamento
            valor_final = total
            cliente_nome = "Balcão"
            
            if metodo == "DINHEIRO":
                rec = st.number_input("Valor Recebido", min_value=total)
                st.info(f"Troco: R$ {rec - total:.2f}")
            elif metodo == "DESCONTO":
                valor_final = st.number_input("Valor com Desconto", max_value=total)
            elif metodo == "CONTA":
                cliente_nome = st.text_input("Nome do Organizador/Amigo").upper()

            if st.button("✅ FINALIZAR E IMPRIMIR"):
                if metodo == "CONTA" and not cliente_nome:
                    st.error("Informe o nome para a conta!")
                else:
                    id_v = len(st.session_state.vendas_realizadas) + 1
                    hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    
                    nova_venda = {
                        "id": id_v, "itens": str(st.session_state.carrinho), 
                        "total": valor_final, "metodo": metodo, 
                        "cliente": cliente_nome, "data": hora, "status": "CONCLUIDA"
                    }
                    
                    st.session_state.vendas_realizadas.append(nova_venda)
                    pd.DataFrame(st.session_state.vendas_realizadas).to_csv(ARQUIVO_VENDAS, index=False)
                    
                    # Simulação de Ficha
                    st.success("Venda Registrada!")
                    st.code(f"ID: {id_v}\n{metodo}\n---\n{total:.2f}\n{hora}\nChopp Seven Dwarfs", language='text')
                    st.session_state.carrinho = []
                    st.rerun()

with tab2:
    st.subheader("Contas Pendentes")
    df_v = pd.DataFrame(st.session_state.vendas_realizadas)
    if not df_v.empty:
        contas = df_v[df_v['metodo'] == "CONTA"]
        st.dataframe(contas)

with tab3:
    st.subheader("Relatório e Estorno")
    if st.session_state.vendas_realizadas:
        df_final = pd.DataFrame(st.session_state.vendas_realizadas)
        st.write(f"Faturamento Líquido: R$ {df_final[df_final['status']=='CONCLUIDA']['total'].sum():.2f}")
        st.dataframe(df_final)
        
        id_estorno = st.number_input("ID para Estorno", min_value=1)
        if st.button("Confirmar Estorno"):
            for v in st.session_state.vendas_realizadas:
                if v['id'] == id_estorno:
                    v['status'] = "ESTORNADA"
                    pd.DataFrame(st.session_state.vendas_realizadas).to_csv(ARQUIVO_VENDAS, index=False)
                    st.warning(f"Venda {id_estorno} Estornada!")
                    st.rerun()
