from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_health_and_summary():
    r=client.get('/api/health');assert r.status_code==200 and r.json()['ok']
    data=client.get('/api/summary').json();assert data['total_registros']==5000

def test_prediction_valid():
    sample={'temperatura_c':65,'vibracao_mm_s':3.2,'corrente_a':15,'rotacao_rpm':1700,'torque_nm':40,'horas_operacao':5000}
    r=client.post('/api/predict',json=sample)
    assert r.status_code==200 and 0<=r.json()['score']<=1

def test_prediction_rejects_invalid():
    sample={'temperatura_c':-2,'vibracao_mm_s':3.2,'corrente_a':15,'rotacao_rpm':1700,'torque_nm':40,'horas_operacao':5000}
    assert client.post('/api/predict',json=sample).status_code==422

def test_batch_valid():
    content=b'temperatura_c,vibracao_mm_s,corrente_a,rotacao_rpm,torque_nm,horas_operacao\n65,3.2,15,1700,40,5000\n'
    r=client.post('/api/batch',content=content,headers={'Content-Type':'text/csv'})
    assert r.status_code==200 and r.json()['n']==1

def test_batch_rejects_missing_columns():
    r=client.post('/api/batch',content=b'temperatura_c\n50\n',headers={'Content-Type':'text/csv'})
    assert r.status_code==422

def test_dashboard_and_local_assets():
    home=client.get('/')
    assert home.status_code==200
    assert 'MotorGuard' in home.text
    assert 'page-simulator' in home.text
    assert client.get('/static/app.js').status_code==200
    assert client.get('/static/style.css').status_code==200


def test_performance_and_exploration():
    report=client.get('/api/performance').json()
    assert report['teste']['n']==1000
    assert report['teste']['falhas_reais']==11
    rows=client.get('/api/sample?limit=25').json()['rows']
    assert len(rows)==25
