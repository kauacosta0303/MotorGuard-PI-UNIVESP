"""Esquema de variáveis usado no treinamento e na predição."""
FEATURES = [
    'temperatura_c', 'vibracao_mm_s', 'corrente_a',
    'rotacao_rpm', 'torque_nm', 'horas_operacao'
]
LABEL = 'falha'
DISPLAY_NAMES = {
    'temperatura_c': 'Temperatura (°C)',
    'vibracao_mm_s': 'Vibração (mm/s)',
    'corrente_a': 'Corrente (A)',
    'rotacao_rpm': 'Rotação (rpm)',
    'torque_nm': 'Torque (N·m)',
    'horas_operacao': 'Horas de operação',
}
RANGES = {
    'temperatura_c': (0., 180.),
    'vibracao_mm_s': (0., 50.),
    'corrente_a': (0., 250.),
    'rotacao_rpm': (0., 10000.),
    'torque_nm': (0., 600.),
    'horas_operacao': (0., 100000.),
}
