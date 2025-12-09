import csv
import random
from datetime import datetime, timedelta
from faker import Faker

# --- CONFIGURAÇÃO ---
NOME_ARQUIVO_CREDITO = 'CREDITO.csv'
ARQUIVO_CLIENTES = 'banco_fake/clientes.csv'
ARQUIVO_CONTAS = 'banco_fake/CONTAS.csv'
LOCALE = 'pt_BR'

fake = Faker(LOCALE)
STATUS_CREDITO = ['Aprovado', 'Negado', 'Inadimplente', 'Pago']
TAXAS_JUROS = [0.05, 0.08, 0.12, 0.15, 0.20] # 5% a 20%

# Define o limite de idade para conceder crédito: 18 anos e 6 meses
DIAS_IDADE_MINIMA_CREDITO = int(365 * 18.5) 

# --- FUNÇÕES DE LEITURA ---

def ler_clientes_e_contas():
    """Lê dados essenciais dos clientes e suas contas para simular o risco."""
    dados_risco = {} # {cliente_id: {'renda': X, 'saldo_total': Y, 'data_nascimento': Z}}
    
    # 1. Ler Rendas e Datas de Nascimento dos Clientes
    try:
        with open(ARQUIVO_CLIENTES, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) 
            for row in reader:
                cliente_id = int(row[0])
                renda = float(row[4])
                # Data de nascimento está na coluna 2
                data_nascimento = datetime.strptime(row[2], '%Y-%m-%d') 
                dados_risco[cliente_id] = {'renda': renda, 'saldo_total': 0, 'data_nascimento': data_nascimento}
    except FileNotFoundError:
        print(f"ERRO: Arquivo de clientes não encontrado.")
        return None

    # 2. Ler e somar Saldos das Contas
    try:
        with open(ARQUIVO_CONTAS, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                cliente_id = int(row[1])
                saldo = float(row[3]) 
                
                if cliente_id in dados_risco:
                    dados_risco[cliente_id]['saldo_total'] += saldo
    except FileNotFoundError:
        print(f"ERRO: Arquivo de contas não encontrado.")
        return None
        
    print(f"Lidos {len(dados_risco)} clientes para análise de risco.")
    return dados_risco

# --- FUNÇÕES DE LÓGICA DE CRÉDITO ---

def calcular_limite(renda, saldo):
    """Calcula um limite de empréstimo baseado na renda e saldo."""
    limite = (renda * random.uniform(0.5, 1.5)) + (saldo * random.uniform(0.1, 0.5))
    return max(1000, round(limite / 500) * 500)

def determinar_status(renda, saldo, limite):
    """Simula a decisão de crédito e o status subsequente."""
    score_base = renda + (saldo * 0.5)
    
    status = 'Negado'
    if score_base > 10000:
        status = random.choices(['Aprovado', 'Inadimplente', 'Pago'], weights=[70, 5, 25], k=1)[0]
    elif score_base > 5000:
        status = random.choices(['Aprovado', 'Negado', 'Inadimplente', 'Pago'], weights=[50, 15, 10, 25], k=1)[0]
    else:
        status = random.choices(['Aprovado', 'Negado', 'Inadimplente', 'Pago'], weights=[20, 50, 5, 25], k=1)[0]
        
    return status

# --- EXECUÇÃO PRINCIPAL ---

dados_risco = ler_clientes_e_contas()

if dados_risco:
    dados_credito = []
    
    cabecalho = [
        'credito_id', 'cliente_id', 'valor_emprestado', 
        'taxa_juros', 'status', 'data_aprovacao'
    ]
    dados_credito.append(cabecalho)
    
    credito_id_counter = 1
    
    print("Gerando operações de crédito...")
    
    hoje = datetime.now()
    
    for cliente_id, dados in dados_risco.items():
        
        data_nascimento = dados['data_nascimento']
        
        # 🟢 REGRA DE NEGÓCIO: IGNORAR MENORES DE 18 ANOS E 6 MESES
        data_minima_credito = data_nascimento + timedelta(days=DIAS_IDADE_MINIMA_CREDITO)
        
        if data_minima_credito > hoje:
            # Cliente ainda não atingiu a idade mínima de 18,5 anos para crédito. Pula.
            continue 
            
        # Apenas 80% dos clientes elegíveis terão alguma operação de crédito
        if random.random() < 0.8:
            
            renda = dados['renda']
            saldo = dados['saldo_total']
            
            limite = calcular_limite(renda, saldo)
            status = determinar_status(renda, saldo, limite)
            
            valor_emprestado = round(limite * random.uniform(0.5, 1.0), 2)
            
            if status == 'Inadimplente' or status == 'Negado':
                taxa = random.choice(TAXAS_JUROS[2:])
            else:
                taxa = random.choice(TAXAS_JUROS[:3])
            
            # Data de aprovação (mínimo: data que fez 18,5 anos; máximo: 90 dias atrás)
            data_maxima = hoje - timedelta(days=90) 
            
            # Garante que o start_date nunca seja maior que o end_date (solução para o erro anterior)
            data_inicio_faker = max(data_minima_credito, data_maxima - timedelta(days=365*2)) # Se a data_maxima for muito recente, usamos ela como início, retroagindo 2 anos
            
            if data_inicio_faker > data_maxima:
                 data_inicio_faker = data_maxima - timedelta(days=30) # Se ainda falhar, garantimos um intervalo de 30 dias

            data_aprovacao = fake.date_between(start_date=data_inicio_faker, end_date=data_maxima).strftime('%Y-%m-%d')
            
            dados_credito.append([
                credito_id_counter,
                cliente_id,
                valor_emprestado,
                taxa,
                status,
                data_aprovacao
            ])
            
            credito_id_counter += 1

    # --- EXPORTAÇÃO PARA CSV ---
    
    caminho_saida = f"{ARQUIVO_CLIENTES.split('/')[0]}/{NOME_ARQUIVO_CREDITO}"
    total_operacoes = len(dados_credito) - 1
    
    try:
        with open(caminho_saida, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(dados_credito)
        
        print(f"Sucesso! Arquivo '{caminho_saida}' criado com {total_operacoes} operações de crédito.")

    except Exception as e:
        print(f"Erro ao escrever no arquivo: {e}")
