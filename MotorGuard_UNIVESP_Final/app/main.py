"""MotorGuard — serviço local FastAPI. Execução: uvicorn app.main:app --reload"""
from pathlib import Path
from io import StringIO
import json
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from joblib import load
from ml.features import FEATURES, DISPLAY_NAMES, RANGES

ROOT=Path(__file__).resolve().parents[1]
app=FastAPI(title='MotorGuard API',description='Classificação experimental com dados sintéticos; não utilizar como decisão industrial.',version='3.0.0')
app.mount('/static',StaticFiles(directory=ROOT/'app'/'static'),name='static')
artifact=load(ROOT/'models'/'motorguard.joblib')
model=artifact['estimator']; threshold=float(artifact['threshold'])
metricas=json.loads((ROOT/'outputs'/'metricas.json').read_text(encoding='utf8'))
dataset=pd.read_csv(ROOT/'data'/'motores_sinteticos.csv')

class MotorInput(BaseModel):
    temperatura_c:float=Field(ge=0,le=180)
    vibracao_mm_s:float=Field(ge=0,le=50)
    corrente_a:float=Field(ge=0,le=250)
    rotacao_rpm:float=Field(ge=0,le=10000)
    torque_nm:float=Field(ge=0,le=600)
    horas_operacao:float=Field(ge=0,le=100000)
    @field_validator('*')
    @classmethod
    def require_finite(cls,v):
        if not np.isfinite(v):raise ValueError('Valor numérico finito obrigatório')
        return v

def predict_df(df):
    missing=[f for f in FEATURES if f not in df.columns]
    if missing:raise ValueError('Colunas faltantes: '+', '.join(missing))
    x=df[FEATURES].apply(pd.to_numeric,errors='coerce')
    if not np.isfinite(x.to_numpy(dtype='float64')).all():raise ValueError('Existem valores ausentes, infinitos ou não numéricos')
    for col,(lo,hi) in RANGES.items():
        if not x[col].between(lo,hi).all():raise ValueError(f'Valores fora da faixa esperada em {col}: {lo} a {hi}')
    scores=model.predict_proba(x)[:,1]
    return scores

@app.get('/')
def home():return FileResponse(ROOT/'app'/'static'/'index.html')

@app.get('/api/health')
def health():return {'ok':True,'versao':'3.0','base':'sintetica','modelo':artifact['name']}

@app.get('/api/summary')
def summary():
    stats={}
    for f in FEATURES:
        stats[f]={'min':float(dataset[f].min()),'max':float(dataset[f].max()),'media':float(dataset[f].mean())}
    return {'total_registros':int(len(dataset)), 'falhas_rotuladas':int(dataset.falha.sum()),
       'taxa_falha':float(dataset.falha.mean()),'variaveis':stats,
       'threshold':threshold,'model_name':artifact['name'],
       'scores_teste':metricas['teste'], 'nota':'Registros artificiais; não são motores físicos monitorados.'}

@app.get('/api/sample')
def sample(limit:int=900):
    limit=max(10,min(limit,1500))
    sampled=dataset.sample(n=min(limit,len(dataset)),random_state=31).copy()
    sampled.insert(0,'registro',sampled.index.astype(int)+1)
    return {'rows':sampled.to_dict(orient='records'), 'features':FEATURES,'labels':DISPLAY_NAMES}

@app.get('/api/performance')
def performance():return metricas

@app.post('/api/predict')
def predict(item:MotorInput):
    frame=pd.DataFrame([item.model_dump()])
    try: score=float(predict_df(frame)[0])
    except ValueError as e:raise HTTPException(status_code=422,detail=str(e))
    return {'score':round(score,6),'limiar':threshold,'classificacao':'ATENÇÃO' if score>=threshold else 'SEM SINALIZAÇÃO',
        'avisos':['Score experimental; não é probabilidade industrial calibrada','Não substitui medições e manutenção técnica','Não estima tempo até a falha']}

@app.post('/api/batch')
async def batch(csv_bytes:bytes=Body(...,media_type='text/csv')):
    if len(csv_bytes)>2_000_000:raise HTTPException(status_code=413,detail='Limite de 2 MB por arquivo')
    try:
        incoming=pd.read_csv(StringIO(csv_bytes.decode('utf-8-sig')))
        if len(incoming)>5000:raise ValueError('Máximo de 5.000 linhas')
        if len(incoming)<1:raise ValueError('Arquivo vazio')
        scores=predict_df(incoming)
        result=incoming.copy(); result.insert(0,'registro',np.arange(1,len(result)+1))
        result['score_experimental']=np.round(scores,5)
        result['classificacao']=np.where(scores>=threshold,'ATENÇÃO','SEM SINALIZAÇÃO')
    except (ValueError,UnicodeError,pd.errors.ParserError) as e:
        raise HTTPException(status_code=422,detail=str(e))
    return {'n':len(result),'sinalizados':int((scores>=threshold).sum()),'rows':result.to_dict(orient='records')}

@app.get('/api/csv-modelo')
def csv_modelo():
    from fastapi.responses import Response
    return Response(content=dataset[FEATURES].head(12).to_csv(index=False),media_type='text/csv',headers={'Content-Disposition':'attachment; filename="modelo_importacao.csv"'})
