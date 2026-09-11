from flask import Flask, render_template, request, jsonify, session
import random
import math
import uuid

app = Flask(__name__)
app.secret_key = 'scorehouse_secret_2024'

# ─── Mock database of applications ───────────────────────────────────────────
APPLICATIONS = [
    {"id": "SCH-001", "name": "Carlos Mendoza", "amount": "$2,500,000", "score": 820, "status": "Aprobado",  "date": "2024-06-01"},
    {"id": "SCH-002", "name": "Ana García",     "amount": "$1,800,000", "score": 650, "status": "Revisión",  "date": "2024-06-03"},
    {"id": "SCH-003", "name": "Luis Torres",    "amount": "$3,200,000", "score": 430, "status": "Rechazado", "date": "2024-06-05"},
    {"id": "SCH-004", "name": "María López",    "amount": "$2,100,000", "score": 780, "status": "Aprobado",  "date": "2024-06-07"},
    {"id": "SCH-005", "name": "Roberto Díaz",   "amount": "$1,500,000", "score": 710, "status": "Aprobado",  "date": "2024-06-09"},
    {"id": "SCH-006", "name": "Sofía Ramírez",  "amount": "$4,000,000", "score": 560, "status": "Revisión",  "date": "2024-06-10"},
]

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    total      = len(APPLICATIONS)
    approved   = sum(1 for a in APPLICATIONS if a['status'] == 'Aprobado')
    rejected   = sum(1 for a in APPLICATIONS if a['status'] == 'Rechazado')
    in_review  = sum(1 for a in APPLICATIONS if a['status'] == 'Revisión')
    stats = {
        'total':     total,
        'approved':  approved,
        'rejected':  rejected,
        'in_review': in_review,
    }
    return render_template('dashboard.html', stats=stats, applications=APPLICATIONS)


@app.route('/scoring')
def scoring():
    return render_template('scoring.html')


@app.route('/report')
def report():
    score_data = session.get('score_data', None)
    return render_template('report.html', score_data=score_data)


# ─── Scoring API ──────────────────────────────────────────────────────────────

@app.route('/calculate-score', methods=['POST'])
def calculate_score():
    data = request.get_json()

    # ── Extract fields ──────────────────────────────────────────────────────
    age              = int(data.get('age', 30))
    monthly_income   = float(data.get('monthly_income', 0))
    monthly_debts    = float(data.get('monthly_debts', 0))
    credit_history   = data.get('credit_history', 'bueno')   # excelente/bueno/regular/malo
    property_value   = float(data.get('property_value', 0))
    loan_amount      = float(data.get('loan_amount', 0))
    property_type    = data.get('property_type', 'casa')
    docs_complete    = int(data.get('docs_complete', 0))      # 0-5 docs checked

    # ── Sub-scores (each 0-200, total max 1000) ─────────────────────────────

    # 1. Debt-to-income ratio (DTI) — 0-200
    if monthly_income > 0:
        dti = monthly_debts / monthly_income
    else:
        dti = 1.0
    if dti <= 0.20:
        dti_score = 200
    elif dti <= 0.35:
        dti_score = 160
    elif dti <= 0.50:
        dti_score = 110
    elif dti <= 0.65:
        dti_score = 60
    else:
        dti_score = 20

    # 2. Credit history — 0-250
    history_map = {'excelente': 250, 'bueno': 190, 'regular': 110, 'malo': 40, 'sin_historial': 70}
    history_score = history_map.get(credit_history, 100)

    # 3. Income level — 0-200
    if monthly_income >= 80_000:
        income_score = 200
    elif monthly_income >= 50_000:
        income_score = 170
    elif monthly_income >= 30_000:
        income_score = 130
    elif monthly_income >= 15_000:
        income_score = 80
    else:
        income_score = 30

    # 4. Age factor — 0-150
    if 28 <= age <= 55:
        age_score = 150
    elif 25 <= age < 28 or 55 < age <= 65:
        age_score = 110
    elif 22 <= age < 25 or 65 < age <= 70:
        age_score = 70
    else:
        age_score = 40

    # 5. Property value vs income — 0-150
    annual_income = monthly_income * 12
    if annual_income > 0:
        pv_ratio = property_value / annual_income
    else:
        pv_ratio = 99
    if pv_ratio <= 3:
        property_score = 150
    elif pv_ratio <= 5:
        property_score = 120
    elif pv_ratio <= 8:
        property_score = 80
    elif pv_ratio <= 12:
        property_score = 40
    else:
        property_score = 15

    # 6. Documentation completeness — 0-50
    doc_score = min(50, docs_complete * 10)
    # ── Total ────────────────────────────────────────────────────────────────
    raw_total = dti_score + history_score + income_score + age_score + property_score + doc_score
    # Scale to 0-1000
    max_possible = 200 + 250 + 200 + 150 + 150 + 50  # 1000
    total_score = round((raw_total / max_possible) * 1000)
    total_score = max(0, min(1000, total_score))

    # ── Recommendation ───────────────────────────────────────────────────────
    if total_score >= 750:
        recommendation = 'Aprobado'
        rec_text = 'El perfil crediticio es excelente. Se recomienda aprobar el crédito con condiciones estándar.'
        rec_color = '#00D4AA'
    elif total_score >= 600:
        recommendation = 'Revisión'
        rec_text = 'El perfil presenta algunas áreas de mejora. Se recomienda revisión adicional y posible garantía extra.'
        rec_color = '#FFD700'
    else:
        recommendation = 'Rechazado'
        rec_text = 'El perfil crediticio no cumple con los requisitos mínimos. Se recomienda rechazar la solicitud.'
        rec_color = '#FF4757'

    result = {
        'total_score': total_score,
        'recommendation': recommendation,
        'rec_text': rec_text,
        'rec_color': rec_color,
        'applicant_id': f'SCH-{random.randint(100, 999)}',
        'breakdown': {
            'dti':      {'label': 'Relación Deuda/Ingreso', 'score': dti_score,      'max': 200},
            'history':  {'label': 'Historial Crediticio',   'score': history_score,  'max': 250},
            'income':   {'label': 'Nivel de Ingresos',      'score': income_score,   'max': 200},
            'age':      {'label': 'Factor de Edad',         'score': age_score,      'max': 150},
            'property': {'label': 'Valor del Inmueble',     'score': property_score, 'max': 150},
            'docs':     {'label': 'Documentación',          'score': doc_score,      'max': 50},
        },
        'applicant': {
            'name':           data.get('full_name', 'N/A'),
            'age':            age,
            'monthly_income': monthly_income,
            'property_value': property_value,
            'loan_amount':    loan_amount,
            'property_type':  property_type,
        }
    }

    # Store in session for the report page
    session['score_data'] = result
    return jsonify(result)


# ─── Login (mock) ─────────────────────────────────────────────────────────────

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email    = data.get('email', '')
    password = data.get('password', '')
    # Mock: any non-empty credentials work
    if email and password:
        session['user'] = email
        return jsonify({'success': True, 'redirect': '/dashboard'})
    return jsonify({'success': False, 'message': 'Credenciales inválidas'}), 401


if __name__ == '__main__':
    app.run(debug=True, port=5000)
