# MotorGuard | Projeto Integrador UNIVESP — Versão acadêmica

**Tema:** Sistema inteligente para monitoramento e prevenção de falhas em motores elétricos por meio de análise de dados e aprendizagem de máquina.

**Orientador:** Rafael Enrique Nunes. **Instituição:** UNIVESP, Engenharia de Computação, 2026.

## ATENÇÃO: escopo científico
- O arquivo `data/motores_sinteticos.csv` é uma **base simulada**, com 5.000 registros. NÃO são medições de motores reais.
- O modelo demonstra **classificação de condições associadas a falhas**, não previsão temporal nem vida útil residual; a aplicação não está validada para decisões industriais.
- As probabilidades de `predict_proba` são **scores experimentais não calibrados**. A base tem apenas 54 rótulos positivos, e os resultados precisam ser interpretados com cautela.
- Integração IoT e validação com a comunidade externa são trabalhos futuros; não foram simuladas entrevistas nem feedbacks.

## Execução no Windows
1. Instale Python 3.11 a 3.13. Execute `INICIAR_WINDOWS.bat`. Necessita conexão à internet **apenas para instalar bibliotecas** se ainda não estiverem instaladas.
2. Abra `http://127.0.0.1:8000` no navegador.
3. Explore as seis telas: visão geral, dados, simulador, avaliação, CSV e metodologia.
4. Pressione `Ctrl+C` no terminal para parar o servidor.

## Execução via terminal
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m ml.train
python -m pytest tests -q
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Arquitetura
`CSV sintético → Python/pandas → preparação + comparação ML → artefato joblib → API FastAPI → HTML/CSS/JavaScript com Plotly local`

## Reproduzibilidade / prevenção de vazamento
- 60% treino, 20% validação, 20% teste estratificados com seed 42;
- pré-processamento por Pipeline aprendendo APENAS no treino;
- seleção do algoritmo pelo Average Precision na validação;
- escolha do limiar pela métrica F2 na validação; teste final mantido separado;
- comparação com classificador majoritário;
- resultados completos, matriz de confusão, previsões e métricas em `outputs/`;
- nunca usar `falha` como entrada e nunca usar classes de teste para selecionar o modelo.

## Campos obrigatórios CSV
`temperatura_c,vibracao_mm_s,corrente_a,rotacao_rpm,torque_nm,horas_operacao`

## Conteúdo
- `app/main.py`: API documentada automaticamente em `/docs`;
- `app/static/`: interface offline e biblioteca Plotly embutida;
- `ml/train.py`, `ml/features.py`: código de treino, validação e comparação;
- `data/`: base sintética;
- `models/`: modelo serializado;
- `outputs/`: métricas e previsões de teste;
- `tests/`: testes automatizados;
- `figuras/`: gráficos técnicos e capturas do aplicativo;
- `documentos/`: relatório Word conforme modelo final da UNIVESP;
- `roteiros/`: instruções e apresentação.

## Reprodutibilidade de resultados
Os números podem variar entre versões de bibliotecas. Para reproduzir exatamente, mantenha as versões do ambiente de referência documentadas em `outputs/ambiente.txt`. Arquivos `joblib` só devem ser carregados de fontes confiáveis.

## Fonte acadêmica complementar
O benchmark [AI4I 2020 da UCI](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset) é citado como alternativa de evolução e **NÃO foi utilizado para gerar as métricas desta versão**; ele é sintético e sobre manutenção de máquinas, não dados reais especificamente de motores.
