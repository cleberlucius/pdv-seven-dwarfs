# =================================================================
# SISTEMA DE GESTÃO DE EVENTOS - VERSÃO INTEGRADA 2026
# =================================================================
import pandas as pd
from datetime import datetime

# --- MÓDULO 1: CONFIGURAÇÃO E ABERTURA ---
NOME_EVENTO = "Grande Gala 2026"
vendas_realizadas = []

# Organização do Cardápio (Código: {Item, Preço})
cardapio = {
    101: {"item": "Cerveja Lata", "preco": 8.00},
    102: {"item": "Refrigerante", "preco": 6.00},
    103: {"item": "Espetinho Carne", "preco": 12.00},
    104: {"item": "Água Mineral", "preco": 4.00},
    105: {"item": "Combo Galera", "preco": 45.00}
}

def exibir_boas_vindas():
    print(f"\n{'='*40}")
    print(f"{NOME_EVENTO.center(40)}")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*40}\n")

# --- MÓDULO 2: VENDAS, CARRINHO E FICHAS ---
def realizar_venda():
    carrinho = []
    total_venda = 0
    
    print(">>> INICIAR NOVO PEDIDO")
    while True:
        try:
            cod = int(input("Código do item (0 para finalizar / 99 para cancelar): "))
            if cod == 0: break
            if cod == 99: return print("Venda cancelada pelo operador.")
            
            if cod in cardapio:
                qtd = int(input(f"Quantidade de [{cardapio[cod]['item']}]: "))
                if qtd <= 0: continue
                
                subtotal = cardapio[cod]['preco'] * qtd
                carrinho.append({
                    "item": cardapio[cod]['item'], 
                    "qtd": qtd, 
                    "subtotal": subtotal
                })
                total_venda += subtotal
                print(f"Adicionado: {qtd}x {cardapio[cod]['item']} - R$ {subtotal:.2f}")
            else:
                print("⚠️ Código não encontrado no cardápio!")
        except ValueError:
            print("⚠️ Erro: Insira apenas números.")

    if total_venda > 0:
        print(f"\nTOTAL DO PEDIDO: R$ {total_venda:.2f}")
        pagto = input("Forma de Pagamento (PIX/CARTAO/DINHEIRO): ").upper()
        
        id_venda = len(vendas_realizadas) + 1
        dados_venda = {
            "id": id_venda,
            "itens": carrinho,
            "total": total_venda,
            "metodo": pagto,
            "status": "CONCLUIDA",
            "hora": datetime.now().strftime('%H:%M:%S')
        }
        vendas_realizadas.append(dados_venda)
        imprimir_ficha(dados_venda)

def imprimir_ficha(venda):
    print(f"\n{'*'*30}")
    print(f"FICHA DE CONSUMO - ID: {venda['id']}")
    for i in venda['itens']:
        print(f"{i['qtd']}x {i['item']}")
    print(f"PAGAMENTO: {venda['metodo']}")
    print(f"VALOR: R$ {venda['total']:.2f}")
    print(f"{'*'*30}\n")

# --- MÓDULO 3: ESTORNOS E AJUSTES ---
def estornar_venda():
    try:
        id_busca = int(input("Informe o ID da venda para ESTORNO: "))
        for venda in vendas_realizadas:
            if venda['id'] == id_busca:
                if venda['status'] == "ESTORNADA":
                    print("⚠️ Esta venda já foi estornada anteriormente.")
                    return
                
                confirmar = input(f"Confirmar estorno de R$ {venda['total']:.2f}? (S/N): ").upper()
                if confirmar == 'S':
                    venda['status'] = "ESTORNADA"
                    print(f"✅ SUCESSO: Venda {id_busca} estornada.")
                    return
        print("❌ ID não encontrado.")
    except ValueError:
        print("⚠️ Erro: ID inválido.")

# --- MÓDULO 4: FECHAMENTO E RELATÓRIOS ---
def gerar_relatorio_fechamento():
    if not vendas_realizadas:
        return print("\nNenhuma venda registrada para gerar relatório.")

    df = pd.DataFrame(vendas_realizadas)
    vendas_ativas = df[df['status'] == "CONCLUIDA"]
    
    faturamento_bruto = df['total'].sum()
    estornos = df[df['status'] == "ESTORNADA"]['total'].sum()
    faturamento_liquido = vendas_ativas['total'].sum()

    print(f"\n{'#'*40}")
    print(f"RESUMO DE FECHAMENTO - {NOME_EVENTO}")
    print(f"{'#'*40}")
    print(f"Faturamento Bruto:   R$ {faturamento_bruto:.2f}")
    print(f"Total Estornado:     R$ {estornos:.2f}")
    print(f"Faturamento Líquido: R$ {faturamento_liquido:.2f}")
    print(f"Qtd Vendas (Ativas): {len(vendas_ativas)}")
    print("-" * 40)
    if not vendas_ativas.empty:
        print("VENDAS POR MÉTODO DE PAGAMENTO:")
        print(vendas_ativas.groupby('metodo')['total'].sum().to_string())
    print(f"{'#'*40}\n")

# --- INICIALIZAÇÃO DO SISTEMA ---
exibir_boas_vindas()
# Para usar, chame as funções:
# realizar_venda()
# estornar_venda()
# gerar_relatorio_fechamento()
