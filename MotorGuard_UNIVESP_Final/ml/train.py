"""Treinamento reproduzível: seleção na validação, avaliação final em teste intocado.

Executar na raiz do projeto: python -m ml.train
Dados de demonstração SIMULADOS; os scores NÃO têm calibração industrial.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from joblib import dump
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_recall_curve, average_precision_score, roc_auc_score,
    precision_score, recall_score, f1_score, fbeta_score, accuracy_score,
    balanced_accuracy_score, confusion_matrix
)
from ml.features import FEATURES, LABEL

ROOT = Path(__file__).resolve().parents[1]
SEED = 42

def load_data(path=None):
    df = pd.read_csv(path or ROOT/'data'/'motores_sinteticos.csv')
    required = set(FEATURES+[LABEL])
    if not required.issubset(df.columns):
        raise ValueError('CSV sem colunas: '+', '.join(sorted(required-set(df.columns))))
    df[FEATURES] = df[FEATURES].apply(pd.to_numeric, errors='raise')
    if df[FEATURES].isna().any().any() or df[LABEL].isna().any():
        raise ValueError('Valores ausentes não previstos na base inicial')
    if set(df[LABEL].unique())!={0,1}:
        raise ValueError('Rótulo deve possuir as duas classes 0 e 1')
    return df

def select_threshold(y, probs):
    """Busca limiar no conjunto de validação; otimiza F2 sem tocar no teste."""
    thresholds = np.round(np.linspace(.03,.95,93),3)
    scores = [fbeta_score(y,probs>=t,beta=2,zero_division=0) for t in thresholds]
    # maior limiar no empate reduz falsos alarmes na seleção
    best=max(zip(scores,thresholds), key=lambda q:(q[0],q[1]))
    return float(best[1]),float(best[0])

def metric_report(y,p,threshold):
    pred=(p>=threshold).astype(int)
    tn,fp,fn,tp = [int(n) for n in confusion_matrix(y,pred,labels=[0,1]).ravel()]
    return {
        'n':int(len(y)), 'falhas_reais':int(np.sum(y)),
        'threshold':threshold,
        'average_precision':float(average_precision_score(y,p)),
        'roc_auc':float(roc_auc_score(y,p)),
        'accuracy':float(accuracy_score(y,pred)),
        'balanced_accuracy':float(balanced_accuracy_score(y,pred)),
        'precision':float(precision_score(y,pred,zero_division=0)),
        'recall':float(recall_score(y,pred,zero_division=0)),
        'f1':float(f1_score(y,pred,zero_division=0)),
        'f2':float(fbeta_score(y,pred,beta=2,zero_division=0)),
        'specificity':float(tn/(tn+fp)) if tn+fp else 0.,
        'confusion_matrix':[[tn,fp],[fn,tp]],
        'false_positives':fp,'false_negatives':fn,'true_positives':tp,'true_negatives':tn
    }

def train():
    df=load_data()
    X=df[FEATURES]; y=df[LABEL].astype(int)
    indices=np.arange(len(df))
    # 60% treino; 20% validação; 20% teste estratificados.
    trtmp, test = train_test_split(indices,test_size=.20,stratify=y,random_state=SEED)
    train, val = train_test_split(trtmp,test_size=.25,stratify=y.iloc[trtmp],random_state=SEED)
    candidates={
        'Baseline (classe majoritária)':make_pipeline(SimpleImputer(strategy='median'),DummyClassifier(strategy='prior')),
        'Regressão logística balanceada':make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),LogisticRegression(class_weight='balanced',random_state=SEED,max_iter=2000)),
        'Random Forest balanceado':make_pipeline(SimpleImputer(strategy='median'),RandomForestClassifier(n_estimators=220,min_samples_leaf=3,max_depth=12,class_weight='balanced_subsample',random_state=SEED,n_jobs=-1))
    }
    comparisons=[]; fits={}; thresholds={}
    for name,model in candidates.items():
        model.fit(X.iloc[train],y.iloc[train])
        p=model.predict_proba(X.iloc[val])[:,1]
        t,fb=select_threshold(y.iloc[val],p)
        r=metric_report(y.iloc[val],p,t)
        comparisons.append({'modelo':name,'ap_validacao':r['average_precision'],'roc_auc_validacao':r['roc_auc'],'f2_validacao':fb,'limiar_validacao':t})
        fits[name]=model; thresholds[name]=t
    # Seleção científica: AP/PR-AUC da validação, não AUC de teste.
    winner=max(comparisons,key=lambda x:x['ap_validacao'])['modelo']
    model=fits[winner]; threshold=thresholds[winner]
    probabilities=model.predict_proba(X.iloc[test])[:,1]
    stats=metric_report(y.iloc[test],probabilities,threshold)
    baseline=metric_report(y.iloc[test],np.full(len(test),float(y.iloc[train].mean())),.5)
    (ROOT/'models').mkdir(exist_ok=True);(ROOT/'outputs').mkdir(exist_ok=True)
    dump({'estimator':model,'features':FEATURES,'threshold':threshold,'name':winner,'seed':SEED},ROOT/'models'/'motorguard.joblib')
    pd.DataFrame({'indice_original':test,'real':y.iloc[test].to_numpy(),'score':probabilities,'previsto':(probabilities>=threshold).astype(int)}).to_csv(ROOT/'outputs'/'predicoes_teste.csv',index=False)
    meta={'projeto':'MotorGuard','data_source':'SIMULADO — motor sintético de demonstração, base v2 do projeto',
          'n_total':int(len(df)), 'falhas_total':int(y.sum()),'taxa_falha':float(y.mean()),
          'split':{'treinamento':len(train),'validacao':len(val),'teste':len(test),'seed':SEED},
          'modelos_comparados':comparisons,'selecionado':winner,'limiar_selecionado_na_validacao':threshold,
          'teste':stats,'baseline_teste':baseline,
          'limitacoes':['Amostras e rótulos sintéticos','Sem sensores físicos ou validação com motores reais','Não há horizonte temporal de previsão','Score não calibrado como probabilidade industrial'],
          'colunas':FEATURES}
    (ROOT/'outputs'/'metricas.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps({'modelo':winner,'val_AP':[r for r in comparisons if r['modelo']==winner][0]['ap_validacao'],'teste':stats},indent=2,ensure_ascii=False))
    return meta

if __name__=='__main__':train()
