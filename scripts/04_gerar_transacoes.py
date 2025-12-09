import csv
import random
from datetime import datetime, timedelta
from faker import Faker
import sys

# Aumenta o limite de campo para o CSV para lidar com registros grandes (segurança)
csv.field_size_limit = sys.maxsize 

# --- CONFIGURAÇÃO DE PRODUÇÃO ---
NUM_TRANSACOES = 10_000_000  # Dez milhões de transações
CHUNK_SIZE = 100_000          # Escrevemos em blocos de 100 mil para preservar a RAM
NOME_ARQUIVO_TRANSACOES = 'TRANSACOES.csv'
ARQUIVO_CONTAS = 'banco_fake/CONTAS.csv'
LOCALE = 'pt_BR'

fake = Faker(LOCALE)
TIPOS_TRANSACAO = ['Depósito', 'Saque', 'TED', 'Pix', 'Compra Débito']

# --- FUNÇÕES DE LEITURA ---

def ler_contas():
    """Lê todas as contas e suas datas de abertura."""
    contas = {}
    try:
        # Nota: O arquivo de contas é pequeno, podemos ler ele inteiro sem chunking
        with open(ARQUIVO_CONTAS, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) 
            for row in reader:
                conta_id = int(row[0])
                data_abertura_str = row[4] 
                contas[conta_id] = datetime.strptime(data_abertura_str, '%Y-%m-%d')
        print(f"Lidas {len(contas)} contas ativas.")
    except FileNotFoundError:
        print(f"ERRO: Arquivo de contas não encontrado em '{ARQUIVO_CONTAS}'.")
        return None
    return contas

# --- FUNÇÕES DE GERAÇÃO ---

def gerar_destino(tipo):
    """Simula o destino ou origem da transação."""
    if tipo in ['TED', 'Pix']:
        return fake.name()
    elif tipo == 'Compra Débito':
        return random.choice(['Supermercado X', 'Farmácia Y', 'Posto Z', 'Loja de Roupas D', 'Restaurante F'])
    else:
        return 'Interno'

def gerar_transacao(conta_id, data_abertura):
    """Gera uma única linha de transação."""
    
    # 1. Definir o tipo e valor
    tipo = random.choice(TIPOS_TRANSACAO)
    
    if tipo in ['Saque', 'Compra Débito']:
        valor = round(random.uniform(10, 500), 2)
    elif tipo == 'Depósito':
        valor = round(random.uniform(50, 5000), 2)
    else: # TED, Pix
        valor = round(random.uniform(100, 10000), 2)

    # 2. Definir a Data/Hora
    data_maxima = datetime.now() - timedelta(days=7) 
    data_inicio_valida = data_abertura + timedelta(days=30) 
    
    data_inicio_faker = data_inicio_valida
    if data_inicio_valida > data_maxima:
        # Se a conta é muito nova, ajusta o início (garante que end_date > start_date)
        data_inicio_faker = data_maxima - timedelta(days=1)
        
    data_hora = fake.date_time_between_dates(
        datetime_start=data_inicio_faker, 
        datetime_end=data_maxima
    ).strftime('%Y-%m-%d %H:%M:%S')

    # 3. Gerar a linha
    return [
        conta_id,
        tipo,
        valor,
        data_hora,
        gerar_destino(tipo)
    ]

# --- EXECUÇÃO PRINCIPAL ---

contas_data = ler_contas()

if contas_data:
    lista_ids = list(contas_data.keys())
    
    caminho_saida = f"banco_fake/{NOME_ARQUIVO_TRANSACOES}"
    
    print(f"Iniciando a geração de {NUM_TRANSACOES:,} transações (aprox. 1 GB)...")
    
    try:
        # 'w' abre o arquivo e o cria se não existir, ou o trunca (limpa) se existir
        with open(caminho_saida, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Escreve o cabeçalho
            writer.writerow(['transacao_id', 'conta_id', 'tipo', 'valor', 'data_hora', 'destino'])
            
            dados_chunk = []
            transacao_id_counter = 1
            
            # Loop principal de GERAÇÃO e ESCRITA EM CHUNKS
            for i in range(1, NUM_TRANSACOES + 1):
                
                # Seleção aleatória de uma conta ID para distribuir as transações
                conta_id = random.choice(lista_ids)
                data_abertura = contas_data[conta_id]
                
                # Gera e formata a linha de transação
                transacao_linha = gerar_transacao(conta_id, data_abertura)
                dados_chunk.append([transacao_id_counter] + transacao_linha)
                transacao_id_counter += 1
                
                # Verifica se atingiu o tamanho do CHUNK ou se é a última iteração
                if i % CHUNK_SIZE == 0 or i == NUM_TRANSACOES:
                    
                    # 🚀 ESCREVE O BLOCO NO DISCO
                    writer.writerows(dados_chunk)
                    dados_chunk = [] # Limpa a lista da memória RAM
                    
                    # Feedback de progresso
                    print(f" -> Escritos: {i / 1_000_000:.1f}M registros ({i / NUM_TRANSACOES * 100:.1f}%)")
                    
        print(f"\n✅ Concluído! Arquivo '{caminho_saida}' criado com {NUM_TRANSACOES:,} transações.")

    except Exception as e:
        print(f"\nERRO FATAL DURANTE A ESCRITA: {e}")
