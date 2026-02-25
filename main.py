# --- TELA DE CONFIGURAÇÃO (CORRIGIDA) ---
if st.session_state.configurado == False:
    st.title("⚙️ Gestão de Cardápio Seven Dwarfs")
    v_ini = st.number_input("Troco Inicial (R$):", min_value=0.0, format="%.2f", value=st.session_state.caixa_inicial)
    
    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        opcoes_base = ["Pilsen", "IPA", "Black Jack", "Vinho", "Manga", "Morango"]
        # Mantém o que já estava selecionado no estado do cardápio
        default_base = [s for s in st.session_state.cardapio.keys() if s in opcoes_base]
        selec_base = st.multiselect("Sabores Fixos:", opcoes_base, default=default_base)
    
    with col_cfg2:
        # Pega itens extras que NÃO estão nas opções base para preencher o texto
        extras_atuais_lista = [s for s in st.session_state.cardapio.keys() if s not in opcoes_base]
        extras_atuais_str = ", ".join(extras_atuais_lista)
        
        # O segredo aqui é o 'value' vir do que já existe, mas processar a saída corretamente
        novos_extras_input = st.text_area("Adicionar Outros (Separe por vírgula):", 
                                        value=extras_atuais_str,
                                        placeholder="Ex: Água, Refrigerante, Suco",
                                        key="input_extras_area")

    # Processamento: transformamos a string em lista, limpando espaços e removendo duplicatas
    lista_extras = [s.strip() for s in novos_extras_input.split(",") if s.strip()]
    # União de Sabores Fixos + Extras (preservando a ordem)
    lista_total_config = []
    for item in (selec_base + lista_extras):
        if item not in lista_total_config:
            lista_total_config.append(item)
    
    st.write("---")
    st.subheader("Defina os Preços:")
    temp_card = {}
    
    if lista_total_config:
        cols_p = st.columns(3)
        for i, s in enumerate(lista_total_config):
            # Buscamos o preço que já existia no estado global para não resetar enquanto digita
            p_existente = st.session_state.cardapio.get(s, 0.0)
            
            # A CHAVE (key) precisa ser única por nome de produto para o Streamlit não perder a referência
            temp_card[s] = cols_p[i%3].number_input(
                f"Preço {s}:", 
                min_value=0.0, 
                format="%.2f", 
                key=f"preco_final_{s}", # Chave dinâmica baseada no nome
                value=float(p_existente)
            )
    
    if st.button("SALVAR E ABRIR VENDAS", type="primary", use_container_width=True):
        if lista_total_config:
            st.session_state.caixa_inicial = v_ini
            st.session_state.cardapio = temp_card
            st.session_state.configurado = True
            st.rerun()
        else:
            st.error("Selecione ou digite pelo menos um item.")
    st.stop()
