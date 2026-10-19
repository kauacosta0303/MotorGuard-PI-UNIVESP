import numpy as np
from ml.train import load_data, select_threshold, metric_report
from ml.features import FEATURES

def test_schema_and_labels():
    df=load_data()
    assert len(df)==5000
    assert df[FEATURES].notna().all().all()
    assert set(df.falha.unique())=={0,1}

def test_threshold_between_zero_and_one():
    t,f2=select_threshold(np.array([0,0,0,1,1]),np.array([.01,.2,.3,.8,.9]))
    assert 0<t<1 and 0<=f2<=1

def test_confusion_counts_add_up():
    y=np.array([0,0,0,1,1,1]);p=np.array([.05,.9,.1,.8,.2,.7])
    metrics=metric_report(y,p,.5)
    assert sum(sum(row) for row in metrics['confusion_matrix'])==len(y)
    assert metrics['false_negatives']==1
