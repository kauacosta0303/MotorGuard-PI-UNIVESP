"""Reconstrói o dataset SIMULADO com seed 42, seguindo o gerador da V1.

Aviso: probabilidades e rótulos são artificiais; não representam medições
nem taxas reais de falhas de motores elétricos.
"""
import numpy as np
import pandas as pd
from pathlib import Path
rng=np.random.default_rng(42);n=5000
T=rng.normal(65,14,n).clip(25,115)
RPM=rng.normal(1750,380,n).clip(500,3500)
torque=rng.normal(35,13,n).clip(2,85)
vib=(rng.gamma(2.3,1.1,n)+np.maximum(0,(RPM-2000)/550)).clip(.1,15)
corrente=(torque*.35+rng.normal(2,2,n)).clip(1,40)
horas=rng.uniform(0,16000,n)
logit=-7+.055*(T-60)+.42*(vib-2)+.035*(corrente-12)+.00013*horas+.012*(torque-35)
p=1/(1+np.exp(-logit));falha=rng.binomial(1,p)
df=pd.DataFrame({'temperatura_c':T.round(2),'vibracao_mm_s':vib.round(2),'corrente_a':corrente.round(2),'rotacao_rpm':RPM.round(0).astype(int),'torque_nm':torque.round(2),'horas_operacao':horas.round(0).astype(int),'falha':falha})
out=Path(__file__).with_name('motores_sinteticos.csv');df.to_csv(out,index=False)
print(f'{out}: {len(df)} linhas e {int(df.falha.sum())} rótulos positivos')
