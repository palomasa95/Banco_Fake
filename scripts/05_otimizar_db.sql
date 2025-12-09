-- Arquivo SQL de otimização de performance.
-- A ser executado após a carga dos dados (script 04).

-- Objetivo: Acelerar todas as consultas que usam JOIN ou WHERE na coluna 'conta_id'
-- da tabela 'transacoes', que é a maior tabela do banco (10M de linhas).

CREATE INDEX idx_trans_conta_id ON transacoes (conta_id);

-- O índice é criado na tabela 'transacoes' (tabela grande) na coluna 'conta_id' (chave de ligação).
