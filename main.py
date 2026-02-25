import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO E PERSISTÊNCIA ---
NOME_EVENTO = "Chopp Seven Dwarfs"
ARQUIVO_DADOS = "vendas_seven_dwarfs.csv"
ARQUIVO_CONTAS = "contas_abertas.csv"

# Cardápio Fixo
cardapio = {
    1: {"item": "Pilsen", "preco": 10.00},
    2: {"item": "IPA", "preco": 15.00},
    3: {"item": "Black Jack", "preco": 15.00},
    4: {"item": "Vinho", "preco": 12.00},
    5: {"item": "Manga", "preco": 13.00}
}

vendas_realizadas = []
contas_abertas = {} # { "Nome": [lista_de_itens] }

def salvar_dados():
    df = pd.DataFrame(vendas_realizadas)
    df.to_csv(ARQUIVO_DADOS, index=False)

# --- MÓDULO DE VENDAS ---
def realizar_venda():
    carrinho = []
    total_original = 0
    
    print(f"\n>>> NOVO PEDIDO - {NOME_EVENTO}")
    while True:
        print("\nCardápio: 1-Pilsen, 2-IPA, 3-Black Jack, 4-Vinho, 5-Manga | 0-Finalizar | 99-Manual")
        try:
            cod = int(input("Seleção: "))
            if cod == 0: break
            
            item_nome = ""
            preco_unit = 0.0

            if cod in cardapio:
                item_nome = cardapio[cod]['item']
                preco_unit = cardapio[cod]['preco']
            elif cod == 99:
                item_nome = input("Nome do item manual: ")
                preco_unit = float(input("Preço unitário: "))
            else:
                print("Código inválido!")
                continue

            # Simulação dos botões +/- (no terminal via input de qtd)
            qtd = int(input(f"Quantidade de {item_nome} (+/-): "))
            if qtd <= 0: continue
            
            subtotal = preco_unit * qtd
            carrinho.append({"item": item_nome, "qtd": qtd, "preco_unit": preco_unit, "subtotal": subtotal})
            total_original += subtotal
            print(f"Carrinho: {qtd}x {item_nome} - Subtotal: R$ {subtotal:.2f}")

        except ValueError:
            print("Entrada inválida.")

    if not carrinho: return

    print(f"\nTOTAL ORIGINAL: R$ {total_original:.2f}")
    print("Pagamento: 1-PIX | 2-DÉBITO | 3-CRÉDITO | 4-DINHEIRO | 5-CORTESIA | 6-CONTA | 7-DESCONTO")
    opcao = input("Escolha a opção: ")

    metodo = ""
    valor_pago = total_original
    nome_conta = ""

    if opcao == "1": metodo = "PIX"
    elif opcao == "2": metodo = "DEBITO"
    elif opcao == "3": metodo = "CREDITO"
    elif opcao == "4":
        metodo = "DINHEIRO"
        recebido = float(input("Valor recebido: "))
        print(f"TROCO: R$ {recebido - total_original:.2f}")
    elif opcao == "5":
        metodo = "CORTESIA"
        valor_pago = 0.0
    elif opcao == "6":
        metodo = "CONTA"
        nome_conta = input("Nome para a conta (Organizador/Amigo): ").upper()
        if nome_conta not in contas_abertas: contas_abertas[nome_conta] = []
        contas_abertas[nome_conta].extend(carrinho)
        print(f"Registrado na conta de {nome_conta}")
    elif opcao == "7":
        metodo = "DESCONTO"
        valor_pago = float(input("Informe o valor final a ser pago: "))

    # Registro da Venda
    id_venda = len(vendas_realizadas) + 1
    dados_venda = {
        "id": id_venda,
        "itens": carrinho,
        "total_real": valor_pago,
        "metodo": metodo,
        "cliente": nome_conta,
        "status": "CONCLUIDA",
        "data_hora": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    }
    
    if metodo != "CONTA":
        vendas_realizadas.append(dados_venda)
        imprimir_ficha(dados_venda)
        salvar_dados()

def imprimir_ficha(venda):
    print(f"\n{'-'*30}")
    print("      CHOPP SEVEN DWARFS") # Logo simplificado
    print(f"ID: {venda['id']}")
    print(f"{venda['metodo']}") # Forma resumida conforme pedido
    print(f"{'-'*30}")
    for i in venda['itens']:
        print(f"{i['qtd']}x {i['item']}")
    print(f"{'-'*30}")
    print(f"TOTAL: R$ {venda['total_real']:.2f}")
    # Rodapé conforme especificações
    print(f"\n{venda['data_hora']}")
    print("Válido apenas na data de emissão durante o evento")
    print("Chopp Seven Dwarfs a verdadeira delícia gelada")
    print("BEBA COM MODERAÇÃO")
    print(f"{'-'*30}\n")

# --- MÓDULO DE ESTORNO (INDIVIDUAL OU TOTAL) ---
def estornar_venda():
    id_busca = int(input("ID da venda para estorno: "))
    for venda in vendas_realizadas:
        if venda['id'] == id_busca:
            print("1- Estornar TUDO | 2- Selecionar itens individuais")
            tipo = input("Opção: ")
            if tipo == "1":
                venda['status'] = "ESTORNADA"
                venda['total_real'] = 0
            else:
                for i, item in enumerate(venda['itens']):
                    op = input(f"Estornar {item['item']}? (S/N): ").upper()
                    if op == 'S':
                        venda['total_real'] -= item['subtotal']
                        item['qtd'] = 0 # Zera a qtd no relatório
            salvar_dados()
            print("Procedimento de estorno finalizado.")
            return

# --- MÓDULO DE FECHAMENTO ---
def fechar_evento():
    df = pd.DataFrame(vendas_realizadas)
    if df.empty: return print("Sem vendas.")
    
    print("\n" + "#"*40)
    print("ESTATÍSTICAS DE FECHAMENTO")
    print("#"*40)
    print(f"Faturamento Total: R$ {df[df['status']=='CONCLUIDA']['total_real'].sum():.2f}")
    print("\nVendas por Método:")
    print(df.groupby('metodo')['total_real'].sum())
    
    print("\nContas Pendentes:")
    for nome, itens in contas_abertas.items():
        total_conta = sum(i['subtotal'] for i in itens)
        print(f"- {nome}: R$ {total_conta:.2f}")
    print("#"*40)

# Exemplo de execução
if __name__ == "__main__":
    # realizar_venda()
    pass
