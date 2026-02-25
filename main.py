# --- ETAPA 2: VENDAS ---
t1, t2, t3 = st.tabs(["🛒 PDV", "🔄 ESTORNO", "📊 FECHAMENTO"])

with t1:
    col_menu, col_carrinho = st.columns([1.6, 1])
    
    with col_menu:
        st.subheader("Sabores")
        # Criamos o grid de botões
        c_btns = st.columns(2)
        sabores_lista = list(st.session_state.cardapio.items())
        
        for i, (nome, preco) in enumerate(sabores_lista):
            # O segredo é usar um on_click ou garantir que o estado mude antes do rerun
            if c_btns[i%2].button(f"{nome}\nR$ {preco:.2f}", key=f"btn_{nome}", use_container_width=True):
                if nome in st.session_state.carrinho:
                    st.session_state.carrinho[nome]['qtd'] += 1
                else:
                    st.session_state.carrinho[nome] = {'preco': preco, 'qtd': 1}
                st.rerun() # Força o Streamlit a redesenhar o carrinho com o novo item
        
        st.write("---")
        st.subheader("Contas VIP Abertas")
        if st.session_state.contas_vip:
            for nome_vip, total_vip in st.session_state.contas_vip.items():
                st.warning(f"👤 {nome_vip}: R$ {total_vip:.2f}")

    with col_carrinho:
        st.subheader("Carrinho")
        total_venda = 0.0
        
        if not st.session_state.carrinho:
            st.info("Selecione um produto ao lado")
        else:
            # Criamos uma cópia das chaves para evitar erro de dicionário mudando de tamanho durante o loop
            itens_no_carrinho = list(st.session_state.carrinho.items())
            for n, it in itens_no_carrinho:
                subtotal = it['preco'] * it['qtd']
                total_venda += subtotal
                
                with st.container():
                    c_n, c_q, c_d = st.columns([2, 1.5, 0.5])
                    c_n.write(f"**{n}**\n(R$ {it['preco']:.2f})")
                    
                    # Controles de Quantidade
                    col_q1, col_q2, col_q3 = c_q.columns([1,1,1])
                    if col_q1.button("➖", key=f"min_{n}"):
                        st.session_state.carrinho[n]['qtd'] -= 1
                        if st.session_state.carrinho[n]['qtd'] <= 0:
                            del st.session_state.carrinho[n]
                        st.rerun()
                    
                    col_q2.write(f"{it['qtd']}")
                    
                    if col_q3.button("➕", key=f"plus_{n}"):
                        st.session_state.carrinho[n]['qtd'] += 1
                        st.rerun()
                        
                    if c_d.button("🗑️", key=f"rem_{n}"):
                        del st.session_state.carrinho[n]
                        st.rerun()
            
            st.divider()
            st.markdown(f"### TOTAL: R$ {total_venda:.2f}")
            
            # --- ÁREA DE PAGAMENTO ---
            metodo_selecionado = None
            
            # Linha 1 de botões
            p1, p2, p3 = st.columns(3)
            if p1.button("PIX", use_container_width=True): metodo_selecionado = "PIX"
            if p2.button("DÉBITO", use_container_width=True): metodo_selecionado = "Débito"
            if p3.button("CRÉDITO", use_container_width=True): metodo_selecionado = "Crédito"
            
            # Linha 2 de botões
            p4, p5, p6 = st.columns(3)
            if p4.button("CORTESIA", use_container_width=True): metodo_selecionado = "Cortesia"
            
            if p5.button("DINHEIRO", use_container_width=True):
                st.session_state.show_dinheiro = True
            
            if p6.button("VIP", use_container_width=True):
                st.session_state.show_vip = True

            # Campos extras condicionais
            if st.session_state.get('show_dinheiro', False):
                v_pago = st.number_input("Quanto o cliente entregou?", min_value=total_venda, step=1.0)
                if st.button("FINALIZAR DINHEIRO"):
                    st.success(f"Troco: R$ {v_pago - total_venda:.2f}")
                    metodo_selecionado = "Dinheiro"
                    st.session_state.show_dinheiro = False

            if st.session_state.get('show_vip', False):
                nome_v = st.text_input("Nome do Cliente VIP:")
                if st.button("LANÇAR NA CONTA"):
                    if nome_v:
                        metodo_selecionado = f"VIP - {nome_v}"
                        st.session_state.contas_vip[nome_v] = st.session_state.contas_vip.get(nome_v, 0.0) + total_venda
                        st.session_state.show_vip = False
                    else:
                        st.error("Digite o nome!")

            # EXECUÇÃO FINAL DA VENDA
            if metodo_selecionado:
                v_id = int(datetime.now().timestamp())
                for sabor, info in st.session_state.carrinho.items():
                    for _ in range(info['qtd']):
                        # Salva no histórico
                        nova_venda = {
                            "id": v_id, 
                            "sabor": sabor, 
                            "valor": info['preco'], 
                            "tipo": metodo_selecionado, 
                            "hora": datetime.now().strftime("%H:%M")
                        }
                        st.session_state.vendas.append(nova_venda)
                        # Adiciona na fila de impressão
                        st.session_state.fichas_pendentes.append(gerar_ficha_imagem(sabor, v_id, metodo_selecionado))
                
                st.session_state.carrinho = {} # Limpa carrinho
                salvar_dados() # Backup CSV
                st.success("Venda realizada!")
                st.rerun()

    # Botão de impressão (aparece fora das colunas para ter destaque)
    if st.session_state.fichas_pendentes:
        st.write("---")
        if st.button("🔥 IMPRIMIR FICHAS AGORA", type="primary", use_container_width=True):
            for f in st.session_state.fichas_pendentes:
                st.image(f)
            st.session_state.fichas_pendentes = []
