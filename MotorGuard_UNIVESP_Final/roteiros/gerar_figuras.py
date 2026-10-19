"""Gráficos científicos e diagramas ilustrativos derivados de resultados efetivos.
Não são capturas de uma planta industrial: são figuras produzidas pelo grupo.
"""
from pathlib import Path
import json
import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from matplotlib.colors import LinearSegmentedColormap

ROOT=Path(__file__).resolve().parents[1]
figs=ROOT/'figuras';figs.mkdir(exist_ok=True)
metrics=json.loads((ROOT/'outputs'/'metricas.json').read_text(encoding='utf8'))
df=pd.read_csv(ROOT/'data'/'motores_sinteticos.csv')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':15,'figure.facecolor':'white','axes.spines.top':False,'axes.spines.right':False})
BLUE='#1e526d';TEAL='#087f8c';ORANGE='#d67538';PALE='#e6f3f3';INK='#1c3347'

# System architecture
fig,ax=plt.subplots(figsize=(13,3.7));ax.set_xlim(0,13);ax.set_ylim(0,4);ax.axis('off')
stages=[('BASE DE DADOS','CSV sintético\n5.000 registros'),('PROCESSAMENTO','Pandas\n6 variáveis'),('APRENDIZAGEM','Scikit-learn\n3 algoritmos'),('API REST','FastAPI\n/health /predict'),('INTERFACE','HTML · JavaScript\nPlotly interativo')]
for i,(a,b) in enumerate(stages):
 x=.22+i*2.58
 box=FancyBboxPatch((x,1.05),2.22,1.96,boxstyle='round,pad=0.09,rounding_size=.17',facecolor=PALE if i%2==0 else '#eaf1f9',edgecolor=TEAL,linewidth=1.8)
 ax.add_patch(box);ax.text(x+1.11,2.48,a,ha='center',va='center',weight='bold',color=INK,fontsize=10)
 ax.text(x+1.11,1.75,b,ha='center',va='center',color=INK,fontsize=10)
 if i<4:ax.add_patch(FancyArrowPatch((x+2.24,2.0),(x+2.53,2.0),arrowstyle='-|>',mutation_scale=17,color=ORANGE,linewidth=1.6))
ax.text(6.5,3.65,'Arquitetura funcional implementada — MotorGuard',ha='center',weight='bold',color=INK,fontsize=16)
ax.text(6.5,.38,'O protótipo não possui coleta física IoT nem integração com CLP/SCADA.',ha='center',color='#586c7a',fontsize=10)
fig.savefig(figs/'fig01_arquitetura.png',dpi=175,bbox_inches='tight');plt.close(fig)

# Methodology
fig,ax=plt.subplots(figsize=(12,4));ax.set_xlim(0,12);ax.set_ylim(0,4.5);ax.axis('off')
steps=[('01','OUVIR E INTERPRETAR','Definir problema\nRevisão técnica\nLevantar requisitos'),('02','CRIAR E PROTOTIPAR','Dados simulados\nTreino e validação\nDesenvolver API e UI'),('03','IMPLEMENTAR E TESTAR','Teste separado\n10 testes automatizados\nAnalisar limitações')]
for i,(num,title,desc) in enumerate(steps):
 x=.3+i*4.05
 box=FancyBboxPatch((x,.45),3.57,3.4,boxstyle='round,pad=0.07,rounding_size=.15',facecolor=['#edf7f4','#eaf1f8','#fff3e8'][i],edgecolor=[TEAL,BLUE,ORANGE][i],linewidth=2)
 ax.add_patch(box);ax.text(x+.25,3.32,num,ha='left',fontsize=26,weight='bold',color=[TEAL,BLUE,ORANGE][i]);ax.text(x+.25,2.57,title,fontsize=11,weight='bold',color=INK);ax.text(x+.25,1.76,desc,fontsize=11,va='center',color=INK,linespacing=1.7)
fig.savefig(figs/'fig02_metodologia.png',dpi=175,bbox_inches='tight');plt.close(fig)

# split and class imbalance
fig,axs=plt.subplots(1,2,figsize=(12,4.5))
sizes=[metrics['split'][n] for n in ['treinamento','validacao','teste']]
axs[0].bar(['Treino','Validação','Teste'],sizes,color=[BLUE,TEAL,ORANGE],width=.58)
for i,v in enumerate(sizes):axs[0].text(i,v+60,format(v,','),ha='center',weight='bold',color=INK)
axs[0].set_ylim(0,3600);axs[0].set_title('Separação estratificada 60/20/20',weight='bold',color=INK)
counts=[len(df)-df.falha.sum(),int(df.falha.sum())]
axs[1].bar(['Sem falha','Com falha'],counts,color=[BLUE,ORANGE],width=.55)
for i,v in enumerate(counts):axs[1].text(i,v+60,format(v,','),ha='center',weight='bold',color=INK)
axs[1].set_title('Desbalanceamento de classes',weight='bold',color=INK)
fig.tight_layout(pad=2);fig.savefig(figs/'fig03_distribuicao.png',dpi=185,bbox_inches='tight');plt.close(fig)

# matrix
fig,ax=plt.subplots(figsize=(7.6,5.5));cm=np.array(metrics['teste']['confusion_matrix']);im=ax.imshow(cm,cmap=LinearSegmentedColormap.from_list('c',["#eef7f8","#17798b"]),vmin=0,vmax=cm.max())
for i in range(2):
 for j in range(2):ax.text(j,i,str(cm[i,j]),fontsize=28,weight='bold',ha='center',va='center',color='white' if cm[i,j]>450 else INK)
ax.set_xticks([0,1],['Normal','Atenção']);ax.set_yticks([0,1],['Normal','Falha']);ax.set_xlabel('Classe prevista');ax.set_ylabel('Rótulo real (sintético)');ax.set_title('Matriz de confusão · teste intocado (n=1.000)',weight='bold',color=INK,pad=20)
fig.colorbar(im,ax=ax,shrink=.8,label='Número de registros');fig.tight_layout();fig.savefig(figs/'fig04_matriz_confusao.png',dpi=175,bbox_inches='tight');plt.close(fig)

# metrics compare
fig,axs=plt.subplots(1,2,figsize=(13,4.7))
comparisons=metrics['modelos_comparados']; names=[r['modelo'].replace(' balanceada','').replace(' balanceado','').replace(' (classe majoritária)','') for r in comparisons]
vals=[r['ap_validacao'] for r in comparisons]
axs[0].barh(names,vals,color=[BLUE,TEAL,ORANGE]);axs[0].invert_yaxis();axs[0].set_xlim(0,max(vals)*1.32)
for i,v in enumerate(vals):axs[0].text(v+.003,i,f'{v:.3f}',va='center',fontsize=10,weight='bold')
axs[0].set_title('Average Precision · validação',weight='bold',color=INK)
quant=[metrics['teste'][k] for k in ['precision','recall','f1','roc_auc','average_precision']]
labels=['Precisão','Recall','F1','ROC AUC','Avg. Precision']
axs[1].barh(labels,quant,color=[TEAL,ORANGE,TEAL,BLUE,ORANGE]);axs[1].invert_yaxis();axs[1].set_xlim(0,1)
for i,v in enumerate(quant):axs[1].text(v+.015,i,f'{v:.3f}',va='center',weight='bold',fontsize=10)
axs[1].set_title('Desempenho · teste final',weight='bold',color=INK)
fig.tight_layout(pad=2);fig.savefig(figs/'fig05_metricas.png',dpi=180,bbox_inches='tight');plt.close(fig)

# conceptual rendering of dashboard (not screenshot), using real test values
fig,ax=plt.subplots(figsize=(13.5,7));fig.patch.set_facecolor('#0b1525');ax.set_facecolor('#0b1525');ax.set_xlim(0,13.5);ax.set_ylim(0,7);ax.axis('off')
ax.add_patch(FancyBboxPatch((.1,.1),2.28,6.8,boxstyle='round,pad=.03',facecolor='#0e1d30',edgecolor='#24415c'))
ax.text(.42,6.45,'⚙  MOTORGUARD',weight='bold',color='#94edcb',fontsize=14)
for i,label in enumerate(['Visão geral','Explorar dados','Simulador','Avaliação científica','Importar CSV','Metodologia']):
 y=5.6-i*.65
 if i==0:ax.add_patch(FancyBboxPatch((.26,y-.18),1.95,.43,boxstyle='round,pad=.04',facecolor='#1b4651',edgecolor='none'))
 ax.text(.45,y,label,color='#dceef2' if i==0 else '#92aabc',fontsize=10)
ax.text(2.75,6.5,'Painel de análise experimental',color='#e7f4f7',weight='bold',fontsize=18)
ax.text(2.75,6.13,'REGISTROS SINTÉTICOS  ·  SEM INTEGRAÇÃO IoT',color='#e7ac83',fontsize=10)
cards=[('Registros','5.000'),('Falhas rotuladas','54'),('Taxa de falha','1,08%'),('Recall teste',f"{metrics['teste']['recall']:.1%}")]
for i,(key,val) in enumerate(cards):
 x=2.74+i*2.58
 ax.add_patch(FancyBboxPatch((x,4.65),2.38,1.1,boxstyle='round,pad=.08',facecolor='#152c3e',edgecolor='#304b5d'))
 ax.text(x+.2,5.45,key.upper(),color='#9ec0c8',fontsize=9)
 ax.text(x+.2,4.88,val,color='#f0fbfa',fontsize=20,weight='bold')
ax.add_patch(FancyBboxPatch((2.74,.7),5.05,3.5,boxstyle='round,pad=.07',facecolor='#152c3e',edgecolor='#304b5d'))
ax.add_patch(FancyBboxPatch((8.02,.7),4.97,3.5,boxstyle='round,pad=.07',facecolor='#152c3e',edgecolor='#304b5d'))
ax.text(3.0,3.88,'Temperatura por classe',color='white',weight='bold',fontsize=12)
ax.text(8.28,3.88,'Desempenho científico',color='white',weight='bold',fontsize=12)
normal=df.loc[df.falha==0,'temperatura_c'];fail=df.loc[df.falha==1,'temperatura_c']
counts,bins=np.histogram(normal,bins=21,range=(30,115));pos=(bins[:-1]+bins[1:])/2
ax.bar(3.0+(pos-pos.min())/(pos.max()-pos.min())*4.45,counts/counts.max()*2.1,width=.155,bottom=1.1,color='#5ab9d5',alpha=.85)
ax.bar(3.0+(pos-pos.min())/(pos.max()-pos.min())*4.45,np.histogram(fail,bins=bins)[0]/max(np.histogram(fail,bins=bins)[0].max(),1)*.9,width=.10,bottom=1.1,color='#eca86c',alpha=.93)
bar_keys=[('ROC AUC',metrics['teste']['roc_auc']),('Recall',metrics['teste']['recall']),('Precisão',metrics['teste']['precision'])]
for i,(n,v) in enumerate(bar_keys):
 yy=3.3-i*.8
 ax.text(8.3,yy,n,color='#d8eefa',fontsize=11);ax.add_patch(FancyBboxPatch((9.8,yy-.03),2.7,.2,boxstyle='round,pad=.02',facecolor='#274052',edgecolor='none'))
 ax.add_patch(FancyBboxPatch((9.8,yy-.03),max(.03,2.7*v),.2,boxstyle='round,pad=.02',facecolor='#8ce6bd',edgecolor='none'))
 ax.text(12.6,yy,f'{v:.2f}',color='white',fontsize=10)
ax.text(6.9,.3,'LAYOUT CONCEITUAL DA INTERFACE · INDICADORES REAIS DO EXPERIMENTO',ha='center',fontsize=9,color='#7a9aaa')
fig.savefig(figs/'fig06_mockup_dashboard.png',dpi=170,bbox_inches='tight',facecolor=fig.get_facecolor());plt.close(fig)
print('Figuras:');[print(x.name, x.stat().st_size) for x in sorted(figs.glob('*.png'))]
