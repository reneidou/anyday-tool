import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
from datetime import datetime, date, timedelta
from collections import defaultdict

# --- Flask App Initialisierung ---
app = Flask(__name__)
app.secret_key = os.urandom(24).hex() # Sicherer Secret Key für die Session

# Macht 'datetime' und 'date' in allen Jinja2-Templates verfügbar
@app.context_processor
def inject_now():
    return {'datetime': datetime, 'date': date}

# --- Datenbank-Helferfunktionen ---
DATABASE = 'finanzen.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Ermöglicht den Zugriff auf Spalten per Namen
    return conn

def init_db():
    # Initialisiert die Datenbank und erstellt alle benötigten Tabellen, falls sie noch nicht existieren.
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'member'
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    ''')
    # Anpassung: is_estimated, confirmed_value, confirmed_date hinzugefügt
    conn.execute('''
        CREATE TABLE IF NOT EXISTS account_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            snapshot_date TEXT NOT NULL,
            balance REAL NOT NULL,
            is_estimated INTEGER DEFAULT 0, -- 0 for false, 1 for true
            confirmed_value REAL,
            confirmed_date TEXT,
            FOREIGN KEY (account_id) REFERENCES accounts (id)
        );
    ''')
    # Anpassung: is_estimated, confirmed_value, confirmed_date hinzugefügt
    conn.execute('''
        CREATE TABLE IF NOT EXISTS fixed_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            planned_amount REAL NOT NULL,
            frequency TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            is_estimated INTEGER DEFAULT 0,
            confirmed_value REAL,
            confirmed_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS paid_fixed_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fixed_cost_id INTEGER NOT NULL,
            paid_date TEXT NOT NULL,
            actual_amount REAL NOT NULL,
            planned_amount_at_time REAL NOT NULL,
            FOREIGN KEY (fixed_cost_id) REFERENCES fixed_costs (id)
        );
    ''')
    # Anpassung: is_estimated, confirmed_value, confirmed_date hinzugefügt
    conn.execute('''
        CREATE TABLE IF NOT EXISTS remarkable_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            expense_date TEXT NOT NULL,
            category TEXT,
            user_id INTEGER NOT NULL,
            is_estimated INTEGER DEFAULT 0,
            confirmed_value REAL,
            confirmed_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    ''')
    # Anpassung: is_estimated, confirmed_value, confirmed_date hinzugefügt
    conn.execute('''
        CREATE TABLE IF NOT EXISTS incomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            source TEXT NOT NULL,
            amount REAL NOT NULL,
            frequency TEXT NOT NULL,
            is_estimated INTEGER DEFAULT 0,
            confirmed_value REAL,
            confirmed_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS prognosis_overrides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            month TEXT NOT NULL, -- Format: YYYY-MM
            variable_expenses_override REAL,
            income_override REAL,
            UNIQUE(user_id, month),
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    ''')
    # NEUE TABELLE: Dump Sheet Notizen
    conn.execute('''
        CREATE TABLE IF NOT EXISTS dump_sheet_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            note_text TEXT NOT NULL,
            created_at TEXT NOT NULL, -- YYYY-MM-DD HH:MM:SS
            is_categorized INTEGER DEFAULT 0, -- 0 for false, 1 for true
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    ''')
    conn.commit()
    conn.close()

# --- Benutzer-Authentifizierung ---
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# --- Prognose-Helferfunktionen ---

def _get_monthly_summary(user_id, num_months=12):
    """
    Aggregiert historische Finanzdaten nach Monaten für Prognosezwecke.
    Gibt eine Liste von Dictionaries zurück, die jeden Monat repräsentieren.
    """
    conn = get_db_connection()
    
    monthly_data = defaultdict(lambda: {
        'start_balance': None,
        'end_balance': None,
        'total_income': 0.0,
        'total_fixed_costs_paid': 0.0,
        'total_remarkable_expenses': 0.0,
        'variable_expenses': None,
        'month_str': '',
        'month_key': ''
    })

    today = date.today()
    
    accounts = conn.execute('SELECT id FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
    account_ids = tuple(acc['id'] for acc in accounts)
    
    monthly_balances = defaultdict(dict)
    if account_ids:
        snapshots = conn.execute(f'''
            SELECT snapshot_date, SUM(balance) as total_balance
            FROM account_snapshots
            WHERE account_id IN ({','.join('?'*len(account_ids))}) AND is_estimated = 0 -- Nur exakte Snapshots für Historie
            GROUP BY snapshot_date
            ORDER BY snapshot_date ASC
        ''', account_ids).fetchall()

        for snap in snapshots:
            snap_date = datetime.strptime(snap['snapshot_date'], '%Y-%m-%d').date()
            month_key = snap_date.strftime('%Y-%m')
            if month_key not in monthly_balances or snap_date >= monthly_balances[month_key].get('last_date', date.min):
                monthly_balances[month_key]['last_balance'] = snap['total_balance']
                monthly_balances[month_key]['last_date'] = snap_date

    month_keys_to_process = []
    for i in range(num_months + 2): # +2 for start_balance calculation
        current_month_start = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        month_keys_to_process.append(current_month_start.strftime('%Y-%m'))
    month_keys_to_process.sort()

    incomes_db = conn.execute('SELECT amount, frequency, is_estimated, confirmed_value FROM incomes WHERE user_id = ?', (user_id,)).fetchall()
    paid_fixed_costs_db = conn.execute('''
        SELECT SUM(pfc.actual_amount) as total_paid, pfc.paid_date
        FROM paid_fixed_costs pfc
        JOIN fixed_costs fc ON pfc.fixed_cost_id = fc.id
        WHERE fc.user_id = ?
        GROUP BY pfc.paid_date
    ''', (user_id,)).fetchall()
    remarkable_expenses_db = conn.execute('SELECT amount, expense_date, is_estimated, confirmed_value FROM remarkable_expenses WHERE user_id = ?', (user_id,)).fetchall()

    for month_key in month_keys_to_process:
        year, month = map(int, month_key.split('-'))
        current_month_date = date(year, month, 1)
        
        monthly_data[month_key]['month_str'] = current_month_date.strftime('%b %Y')
        monthly_data[month_key]['month_key'] = month_key

        for income in incomes_db:
            amount_to_use = income['confirmed_value'] if income['is_estimated'] and income['confirmed_value'] is not None else income['amount']
            if income['frequency'] == 'monthly':
                monthly_data[month_key]['total_income'] += amount_to_use
            elif income['frequency'] == 'yearly' and current_month_date.month == 1:
                monthly_data[month_key]['total_income'] += amount_to_use

        for pfc in paid_fixed_costs_db:
            paid_date = datetime.strptime(pfc['paid_date'], '%Y-%m-%d').date()
            if paid_date.year == year and paid_date.month == month:
                monthly_data[month_key]['total_fixed_costs_paid'] += pfc['total_paid']

        for re in remarkable_expenses_db:
            amount_to_use = re['confirmed_value'] if re['is_estimated'] and re['confirmed_value'] is not None else re['amount']
            exp_date = datetime.strptime(re['expense_date'], '%Y-%m-%d').date()
            if exp_date.year == year and exp_date.month == month:
                monthly_data[month_key]['total_remarkable_expenses'] += amount_to_use

    final_historical_data = []
    ordered_keys = sorted(monthly_data.keys())

    for i, month_key in enumerate(ordered_keys):
        current_month_end_balance = monthly_balances[month_key].get('last_balance')
        prev_month_end_balance = None
        if i > 0:
            prev_month_key = ordered_keys[i-1]
            prev_month_end_balance = monthly_balances[prev_month_key].get('last_balance')

        monthly_data[month_key]['start_balance'] = prev_month_end_balance
        monthly_data[month_key]['end_balance'] = current_month_end_balance

        if monthly_data[month_key]['start_balance'] is not None and monthly_data[month_key]['end_balance'] is not None:
            net_wealth_change = monthly_data[month_key]['end_balance'] - monthly_data[month_key]['start_balance']
            
            calculated_variable_expenses = (
                monthly_data[month_key]['total_income'] -
                monthly_data[month_key]['total_fixed_costs_paid'] -
                monthly_data[month_key]['total_remarkable_expenses'] -
                net_wealth_change
            )
            monthly_data[month_key]['variable_expenses'] = round(calculated_variable_expenses, 2)
            final_historical_data.append(monthly_data[month_key])
        else:
            monthly_data[month_key]['variable_expenses'] = None
        
    conn.close()
    
    return sorted([m for m in final_historical_data if m['variable_expenses'] is not None], 
                  key=lambda x: datetime.strptime(x['month_str'], '%b %Y'))[-num_months:]


def _generate_variable_expenses_prognosis(historical_data, model_type, num_months_prognosis=12):
    """
    Generiert eine Prognose der variablen Ausgaben basierend auf historischen Daten.
    """
    prognosis_values = []
    historical_variable_expenses = [d['variable_expenses'] for d in historical_data if d['variable_expenses'] is not None]

    if not historical_variable_expenses:
        return [0.0] * num_months_prognosis

    if model_type == 'sma':
        data_for_avg = historical_variable_expenses[-3:] if len(historical_variable_expenses) >= 3 else historical_variable_expenses
        avg_expense = sum(data_for_avg) / len(data_for_avg) if data_for_avg else 0.0
        for _ in range(num_months_prognosis):
            prognosis_values.append(round(avg_expense, 2))
    
    elif model_type == 'wma':
        if len(historical_variable_expenses) < 3: 
             data_for_avg = historical_variable_expenses
             avg_expense = sum(data_for_avg) / len(data_for_avg) if data_for_avg else 0.0
             for _ in range(num_months_prognosis):
                prognosis_values.append(round(avg_expense, 2))
        else:
            weights = [1, 2, 3] 
            recent_data = historical_variable_expenses[-3:]
            weighted_sum = sum(recent_data[i] * weights[i] for i in range(len(recent_data)))
            total_weights = sum(weights[:len(recent_data)])
            weighted_avg_expense = weighted_sum / total_weights if total_weights != 0 else 0.0
            
            for _ in range(num_months_prognosis):
                prognosis_values.append(round(weighted_avg_expense, 2))

    return prognosis_values

def _get_default_income_prognosis(user_id, num_months_prognosis=12):
    """
    Generiert eine einfache Prognose der Einnahmen basierend auf den registrierten monatlichen und jährlichen Einnahmen.
    """
    conn = get_db_connection()
    incomes = conn.execute('SELECT amount, frequency, is_estimated, confirmed_value FROM incomes WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()

    monthly_base_income = 0.0
    for income in incomes:
        amount_to_use = income['confirmed_value'] if income['is_estimated'] and income['confirmed_value'] is not None else income['amount']
        if income['frequency'] == 'monthly':
            monthly_base_income += amount_to_use
    
    yearly_income_in_jan = 0.0
    for income in incomes:
        amount_to_use = income['confirmed_value'] if income['is_estimated'] and income['confirmed_value'] is not None else income['amount']
        if income['frequency'] == 'yearly':
            yearly_income_in_jan += amount_to_use

    prognosis = []
    today = date.today()
    for i in range(num_months_prognosis):
        future_month_date = (today.replace(day=1) + timedelta(days=i * 30)).replace(day=1)
        current_month_income = monthly_base_income
        if future_month_date.month == 1:
            current_month_income += yearly_income_in_jan
        prognosis.append(round(current_month_income, 2))
    
    return prognosis

def _calculate_model_accuracy(historical_data, prognosis_function, model_type):
    """
    Berechnet die Genauigkeit eines Prognosemodells (z.B. Mean Absolute Error - MAE).
    """
    if len(historical_data) < 2: # Benötigt mindestens 2 Datenpunkte, um eine Prognose zu bewerten
        return None

    errors = []
    # Wir bewerten die Prognose, indem wir versuchen, den Vormonat zu prognostizieren
    # und mit dem tatsächlichen Wert zu vergleichen.
    for i in range(1, len(historical_data)):
        # Historische Daten bis zum Vormonat für die Prognose
        data_for_prognosis = historical_data[:i] 
        # Prognostiziere den aktuellen Monat basierend auf den vorherigen Daten
        predicted_values = prognosis_function(data_for_prognosis, model_type, num_months_prognosis=1)
        
        if predicted_values and historical_data[i]['variable_expenses'] is not None:
            actual_value = historical_data[i]['variable_expenses']
            predicted_value = predicted_values[0]
            errors.append(abs(actual_value - predicted_value))
    
    if errors:
        return round(sum(errors) / len(errors), 2)
    return None


# --- Routen der Web-App ---

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                            (username, hashed_password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_role'] = user['role']
            flash(f'Willkommen zurück, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Falscher Benutzername oder Passwort', 'danger')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = get_db_connection()
    admin_exists = conn.execute("SELECT 1 FROM users WHERE role = 'admin'").fetchone()
    conn.close()

    if admin_exists and (session.get('user_role') != 'admin' or 'user_id' not in session):
        flash('Zugriff verweigert. Nur Administratoren können neue Benutzer registrieren.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'member')

        if not username or not password:
            flash('Benutzername und Passwort dürfen nicht leer sein.', 'danger')
            return render_template('register.html')

        hashed_password = hash_password(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                        (username, hashed_password, role))
            conn.commit()
            flash('Registrierung erfolgreich! Bitte melden Sie sich an.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Dieser Benutzername existiert bereits.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('user_role', None)
    flash('Sie wurden abgemeldet.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()

    # Aktueller Gesamtvermögensstand
    current_total_balance = 0.0
    accounts_data = conn.execute('SELECT id, name FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
    for account in accounts_data:
        latest_snapshot = conn.execute(
            'SELECT balance FROM account_snapshots WHERE account_id = ? ORDER BY snapshot_date DESC, id DESC LIMIT 1',
            (account['id'],)
        ).fetchone()
        if latest_snapshot:
            current_total_balance += latest_snapshot['balance']

    # Offene Fixkosten-Bestätigungen für den aktuellen Monat
    today = date.today()
    first_day_of_month = today.replace(day=1)
    
    all_fixed_costs = conn.execute('SELECT id, name, planned_amount, frequency FROM fixed_costs WHERE user_id = ?', (user_id,)).fetchall()
    
    fixed_costs_to_confirm = []
    for fc in all_fixed_costs:
        is_due_this_month = False
        if fc['frequency'] == 'monthly':
            is_due_this_month = True
        elif fc['frequency'] == 'quarterly' and today.month % 3 == 1:
            is_due_this_month = True
        elif fc['frequency'] == 'yearly' and today.month == 1:
            is_due_this_month = True
        
        if is_due_this_month:
            paid_this_month = conn.execute(
                'SELECT 1 FROM paid_fixed_costs WHERE fixed_cost_id = ? AND paid_date >= ?',
                (fc['id'], first_day_of_month.strftime('%Y-%m-%d'))
            ).fetchone()
            
            if not paid_this_month:
                fixed_costs_to_confirm.append(fc)

    # Zukünftige bemerkenswerte Ausgaben (ab heute)
    remarkable_upcoming = conn.execute(
        'SELECT description, amount, expense_date, category FROM remarkable_expenses WHERE user_id = ? AND expense_date >= ? ORDER BY expense_date ASC',
        (user_id, today.strftime('%Y-%m-%d'))
    ).fetchall()

    # --- Prognose-Berechnungen für Dashboard Charts ---
    historical_data_summary = _get_monthly_summary(user_id, num_months=12) # Letzte 12 Monate für die Historie
    
    # Daten für die Darstellung der historischen variablen Ausgaben und Einnahmen (für Chart)
    chart_labels = [d['month_str'] for d in historical_data_summary]
    chart_data_variable_expenses = [d['variable_expenses'] for d in historical_data_summary]
    chart_data_incomes = [d['total_income'] for d in historical_data_summary]

    # Prognose für die nächsten 12 Monate
    num_months_prognosis = 12 
    prognosis_months = []
    for i in range(num_months_prognosis):
        next_month_date = (today.replace(day=1) + timedelta(days=i * 30)).replace(day=1)
        prognosis_months.append(next_month_date.strftime('%b %Y'))

    # Prognose für 'variable_expenses' basierend auf verschiedenen Modellen
    # Diese Prognosen berücksichtigen jetzt die Overrides
    prognosis_sma_var_exp_raw = _generate_variable_expenses_prognosis(historical_data_summary, 'sma', num_months_prognosis)
    prognosis_wma_var_exp_raw = _generate_variable_expenses_prognosis(historical_data_summary, 'wma', num_months_prognosis)

    # Prognose für Einnahmen (einfach, da meist fester)
    prognosis_income_raw = _get_default_income_prognosis(user_id, num_months_prognosis)

    # Overrides für Prognose abrufen und anwenden
    overrides = conn.execute('SELECT month, variable_expenses_override, income_override FROM prognosis_overrides WHERE user_id = ?', (user_id,)).fetchall()
    override_map = {o['month']: o for o in overrides}

    prognosis_sma_var_exp = []
    prognosis_wma_var_exp = []
    prognosis_income = []
    
    # Apply overrides to the raw prognoses
    for i in range(num_months_prognosis):
        future_month_date = (today.replace(day=1) + timedelta(days=i * 30)).replace(day=1)
        month_key = future_month_date.strftime('%Y-%m')
        
        override = override_map.get(month_key)
        
        # Variable Expenses Override
        if override and override['variable_expenses_override'] is not None:
            prognosis_sma_var_exp.append(override['variable_expenses_override'])
            prognosis_wma_var_exp.append(override['variable_expenses_override'])
        else:
            prognosis_sma_var_exp.append(prognosis_sma_var_exp_raw[i] if i < len(prognosis_sma_var_exp_raw) else 0.0)
            prognosis_wma_var_exp.append(prognosis_wma_var_exp_raw[i] if i < len(prognosis_wma_var_exp_raw) else 0.0)
            
        # Income Override
        if override and override['income_override'] is not None:
            prognosis_income.append(override['income_override'])
        else:
            prognosis_income.append(prognosis_income_raw[i] if i < len(prognosis_income_raw) else 0.0)


    # --- Modell-Genauigkeit berechnen (MAE) ---
    sma_mae = _calculate_model_accuracy(historical_data_summary, _generate_variable_expenses_prognosis, 'sma')
    wma_mae = _calculate_model_accuracy(historical_data_summary, _generate_variable_expenses_prognosis, 'wma')

    conn.close()

    return render_template('dashboard.html',
                           username=session['username'],
                           current_total_balance=current_total_balance,
                           fixed_costs_to_confirm=fixed_costs_to_confirm,
                           remarkable_upcoming=remarkable_upcoming,
                           
                           chart_labels=chart_labels,
                           chart_data_variable_expenses=chart_data_variable_expenses,
                           chart_data_incomes=chart_data_incomes,
                           
                           prognosis_months=prognosis_months,
                           prognosis_sma_var_exp=prognosis_sma_var_exp,
                           prognosis_wma_var_exp=prognosis_wma_var_exp,
                           prognosis_sma_income=prognosis_income, # SMA und WMA Income sind hier gleich, da nur eine einfache Prognose
                           prognosis_wma_income=prognosis_income, # Könnte später differenziert werden
                           
                           sma_mae=sma_mae,
                           wma_mae=wma_mae
                           )

# --- NEUE ROUTE FÜR PROGNOSE-ANPASSUNGEN ---
@app.route('/manage_prognosis_overrides', methods=['GET', 'POST'])
def manage_prognosis_overrides():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    today = date.today()
    num_months_prognosis = 12

    prognosis_data_for_template = []
    
    historical_data_summary = _get_monthly_summary(user_id, num_months=12)
    default_variable_expenses_prognosis = _generate_variable_expenses_prognosis(historical_data_summary, 'sma', num_months_prognosis)
    default_income_prognosis = _get_default_income_prognosis(user_id, num_months_prognosis)

    current_overrides = conn.execute(
        'SELECT month, variable_expenses_override, income_override FROM prognosis_overrides WHERE user_id = ?',
        (user_id,)
    ).fetchall()
    overrides_dict = {o['month']: {'variable_expenses_override': o['variable_expenses_override'], 
                                   'income_override': o['income_override']} 
                      for o in current_overrides}

    for i in range(num_months_prognosis):
        future_month_date = (today.replace(day=1) + timedelta(days=i * 30)).replace(day=1)
        month_key = future_month_date.strftime('%Y-%m')
        month_display = future_month_date.strftime('%b %Y')

        default_var_exp = default_variable_expenses_prognosis[i] if i < len(default_variable_expenses_prognosis) else 0.0
        default_inc = default_income_prognosis[i] if i < len(default_income_prognosis) else 0.0

        override_var_exp = overrides_dict.get(month_key, {}).get('variable_expenses_override')
        override_inc = overrides_dict.get(month_key, {}).get('income_override')

        prognosis_data_for_template.append({
            'month': month_key,
            'month_display': month_display,
            'default_variable_expenses': default_var_exp,
            'override_variable_expenses': override_var_exp,
            'default_income': default_inc,
            'override_income': override_inc
        })

    if request.method == 'POST':
        success = True
        for month_data in prognosis_data_for_template: # Use the generated list for iteration
            month_key = month_data['month']
            
            var_exp_input = request.form.get(f'variable_expenses_{month_key}')
            income_input = request.form.get(f'income_{month_key}')

            var_exp_override = None
            income_override = None

            try:
                if var_exp_input is not None and var_exp_input.strip() != '':
                    var_exp_override = float(var_exp_input)
                if income_input is not None and income_input.strip() != '':
                    income_override = float(income_input)

                if var_exp_override is not None or income_override is not None:
                    conn.execute('''
                        INSERT INTO prognosis_overrides (user_id, month, variable_expenses_override, income_override)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(user_id, month) DO UPDATE SET
                            variable_expenses_override = EXCLUDED.variable_expenses_override,
                            income_override = EXCLUDED.income_override
                    ''', (user_id, month_key, var_exp_override, income_override))
                else:
                    conn.execute('DELETE FROM prognosis_overrides WHERE user_id = ? AND month = ?', (user_id, month_key))
                
                conn.commit()

            except ValueError:
                flash(f'Ungültiger Zahlenwert für einen Override im Monat {month_data["month_display"]}.', 'danger')
                success = False
                break
            except sqlite3.Error as e:
                flash(f'Fehler beim Speichern der Overrides: {e}', 'danger')
                conn.rollback()

        if success:
            flash('Prognose-Anpassungen erfolgreich gespeichert.', 'success')
        return redirect(url_for('manage_prognosis_overrides'))

    conn.close()
    return render_template('manage_prognosis_overrides.html', prognosis_data=prognosis_data_for_template)


# --- Routen für Vermögensverwaltung ---
@app.route('/manage_accounts', methods=['GET', 'POST'])
def manage_accounts():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_account':
            account_name = request.form['account_name'].strip()
            if account_name:
                try:
                    conn.execute('INSERT INTO accounts (user_id, name) VALUES (?, ?)', (user_id, account_name))
                    conn.commit()
                    flash(f'Konto "{account_name}" erfolgreich hinzugefügt.', 'success')
                except sqlite3.IntegrityError:
                    flash(f'Konto "{account_name}" existiert bereits.', 'danger')
            else:
                flash('Kontoname darf nicht leer sein.', 'danger')
        
        elif action == 'add_snapshot':
            account_id = request.form['account_id']
            balance = request.form['balance']
            snapshot_date = request.form['snapshot_date']
            is_estimated = 1 if request.form.get('is_estimated') == 'on' else 0 # NEU
            
            if account_id and balance and snapshot_date:
                try:
                    balance = float(balance)
                    account_owner = conn.execute('SELECT user_id FROM accounts WHERE id = ?', (account_id,)).fetchone()
                    if account_owner and account_owner['user_id'] == user_id:
                        conn.execute('INSERT INTO account_snapshots (account_id, snapshot_date, balance, is_estimated) VALUES (?, ?, ?, ?)',
                                     (account_id, snapshot_date, balance, is_estimated))
                        conn.commit()
                        flash('Kontostand erfolgreich erfasst.', 'success')
                    else:
                        flash('Zugriff verweigert: Konto gehört nicht diesem Benutzer.', 'danger')
                except ValueError:
                    flash('Ungültiger Betrag für den Kontostand.', 'danger')
            else:
                flash('Alle Felder für den Kontostand müssen ausgefüllt sein.', 'danger')
        
        elif action == 'delete_account':
            account_id = request.form['account_id']
            account_owner = conn.execute('SELECT user_id FROM accounts WHERE id = ?', (account_id,)).fetchone()
            if account_owner and account_owner['user_id'] == user_id:
                conn.execute('DELETE FROM account_snapshots WHERE account_id = ?', (account_id,))
                conn.execute('DELETE FROM accounts WHERE id = ? AND user_id = ?', (account_id, user_id))
                conn.commit()
                flash('Konto und zugehörige Snapshots erfolgreich gelöscht.', 'info')
            else:
                flash('Zugriff verweigert: Konto gehört nicht diesem Benutzer.', 'danger')

        return redirect(url_for('manage_accounts'))

    accounts = conn.execute('SELECT id, name FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
    
    accounts_with_snapshots = []
    for account in accounts:
        latest_snapshot = conn.execute(
            'SELECT snapshot_date, balance, is_estimated, confirmed_value, confirmed_date FROM account_snapshots WHERE account_id = ? ORDER BY snapshot_date DESC, id DESC LIMIT 1',
            (account['id'],)
        ).fetchone()
        
        all_snapshots = conn.execute(
            'SELECT snapshot_date, balance, is_estimated, confirmed_value, confirmed_date FROM account_snapshots WHERE account_id = ? ORDER BY snapshot_date DESC',
            (account['id'],)
        ).fetchall()
        
        accounts_with_snapshots.append({
            'id': account['id'],
            'name': account['name'],
            'latest_snapshot': latest_snapshot,
            'all_snapshots': all_snapshots
        })
    
    conn.close()
    return render_template('manage_accounts.html', accounts=accounts_with_snapshots)


# --- Routen für Fixkostenverwaltung ---
@app.route('/manage_fixed_costs', methods=['GET', 'POST'])
def manage_fixed_costs():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_fixed_cost':
            name = request.form['name'].strip()
            planned_amount = request.form['planned_amount']
            frequency = request.form['frequency']
            is_estimated = 1 if request.form.get('is_estimated') == 'on' else 0 # NEU

            if name and planned_amount and frequency:
                try:
                    planned_amount = float(planned_amount)
                    conn.execute('INSERT INTO fixed_costs (name, planned_amount, frequency, user_id, is_estimated) VALUES (?, ?, ?, ?, ?)',
                                 (name, planned_amount, frequency, user_id, is_estimated))
                    conn.commit()
                    flash(f'Fixkosten "{name}" erfolgreich hinzugefügt.', 'success')
                except ValueError:
                    flash('Ungültiger Betrag für die Fixkosten.', 'danger')
            else:
                flash('Alle Felder für Fixkosten müssen ausgefüllt sein.', 'danger')
        
        elif action == 'confirm_fixed_cost':
            fixed_cost_id = request.form['fixed_cost_id']
            actual_amount = request.form['actual_amount']
            paid_date = request.form['paid_date']

            if fixed_cost_id and actual_amount and paid_date:
                try:
                    actual_amount = float(actual_amount)
                    fixed_cost = conn.execute('SELECT planned_amount, user_id FROM fixed_costs WHERE id = ?', (fixed_cost_id,)).fetchone()
                    if fixed_cost and fixed_cost['user_id'] == user_id:
                        # Bestätige den Wert im fixed_costs Eintrag selbst
                        conn.execute('UPDATE fixed_costs SET confirmed_value = ?, confirmed_date = ? WHERE id = ?',
                                     (actual_amount, paid_date, fixed_cost_id)) # NEU: Update confirmed_value in fixed_costs
                        
                        planned_amount_at_time = fixed_cost['planned_amount']
                        conn.execute('INSERT INTO paid_fixed_costs (fixed_cost_id, paid_date, actual_amount, planned_amount_at_time) VALUES (?, ?, ?, ?)',
                                     (fixed_cost_id, paid_date, actual_amount, planned_amount_at_time))
                        conn.commit()
                        flash('Fixkosten erfolgreich bestätigt.', 'success')
                    elif not fixed_cost:
                        flash('Fixkosten nicht gefunden.', 'danger')
                    else:
                        flash('Zugriff verweigert: Fixkosten gehören nicht diesem Benutzer.', 'danger')
                except ValueError:
                    flash('Ungültiger Betrag für die Bestätigung.', 'danger')
            else:
                flash('Alle Felder für die Bestätigung müssen ausgefüllt sein.', 'danger')

        elif action == 'delete_fixed_cost':
            fixed_cost_id = request.form['fixed_cost_id']
            fixed_cost_owner = conn.execute('SELECT user_id FROM fixed_costs WHERE id = ?', (fixed_cost_id,)).fetchone()
            if fixed_cost_owner and fixed_cost_owner['user_id'] == user_id:
                conn.execute('DELETE FROM paid_fixed_costs WHERE fixed_cost_id = ?', (fixed_cost_id,))
                conn.execute('DELETE FROM fixed_costs WHERE id = ? AND user_id = ?', (fixed_cost_id, user_id))
                conn.commit()
                flash('Fixkosten und zugehörige Zahlungen erfolgreich gelöscht.', 'info')
            else:
                flash('Zugriff verweigert: Fixkosten gehören nicht diesem Benutzer.', 'danger')

        return redirect(url_for('manage_fixed_costs'))

    fixed_costs = conn.execute('SELECT id, name, planned_amount, frequency, is_estimated, confirmed_value, confirmed_date FROM fixed_costs WHERE user_id = ?', (user_id,)).fetchall()
    
    fixed_costs_with_payments = []
    for fc in fixed_costs:
        payments = conn.execute(
            'SELECT paid_date, actual_amount, planned_amount_at_time FROM paid_fixed_costs WHERE fixed_cost_id = ? ORDER BY paid_date DESC',
            (fc['id'],)
        ).fetchall()
        
        is_due_this_month = False
        today = date.today()
        first_day_of_month = today.replace(day=1)

        if fc['frequency'] == 'monthly':
            is_due_this_month = True
        elif fc['frequency'] == 'quarterly' and today.month % 3 == 1:
            is_due_this_month = True
        elif fc['frequency'] == 'yearly' and today.month == 1:
            is_due_this_month = True
        
        paid_this_month = conn.execute(
            'SELECT 1 FROM paid_fixed_costs WHERE fixed_cost_id = ? AND paid_date >= ?',
            (fc['id'], first_day_of_month.strftime('%Y-%m-%d'))
        ).fetchone()
        
        needs_confirmation = is_due_this_month and not paid_this_month
        
        fixed_costs_with_payments.append({
            'id': fc['id'],
            'name': fc['name'],
            'planned_amount': fc['planned_amount'],
            'frequency': fc['frequency'],
            'payments': payments,
            'needs_confirmation': needs_confirmation,
            'is_estimated': fc['is_estimated'], # NEU
            'confirmed_value': fc['confirmed_value'], # NEU
            'confirmed_date': fc['confirmed_date'] # NEU
        })

    conn.close()
    return render_template('manage_fixed_costs.html', fixed_costs=fixed_costs_with_payments)

# --- Routen für bemerkenswerte Ausgaben ---
@app.route('/manage_remarkable_expenses', methods=['GET', 'POST'])
def manage_remarkable_expenses():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_expense':
            description = request.form['description'].strip()
            amount = request.form['amount']
            expense_date = request.form['expense_date']
            category = request.form['category'].strip()
            is_estimated = 1 if request.form.get('is_estimated') == 'on' else 0 # NEU

            if description and amount and expense_date:
                try:
                    amount = float(amount)
                    conn.execute('INSERT INTO remarkable_expenses (description, amount, expense_date, category, user_id, is_estimated) VALUES (?, ?, ?, ?, ?, ?)',
                                 (description, amount, expense_date, category, user_id, is_estimated))
                    conn.commit()
                    flash(f'Besondere Ausgabe "{description}" erfolgreich hinzugefügt.', 'success')
                except ValueError:
                    flash('Ungültiger Betrag für die Ausgabe.', 'danger')
            else:
                flash('Alle Felder für die Ausgabe müssen ausgefüllt sein.', 'danger')
        
        elif action == 'delete_expense':
            expense_id = request.form['expense_id']
            expense_owner = conn.execute('SELECT user_id FROM remarkable_expenses WHERE id = ?', (expense_id,)).fetchone()
            if expense_owner and expense_owner['user_id'] == user_id:
                conn.execute('DELETE FROM remarkable_expenses WHERE id = ? AND user_id = ?', (expense_id, user_id))
                conn.commit()
                flash('Besondere Ausgabe erfolgreich gelöscht.', 'info')
            else:
                flash('Zugriff verweigert: Ausgabe gehört nicht diesem Benutzer.', 'danger')
        
        elif action == 'confirm_expense': # NEU: Bestätigungsaktion für geschätzte Ausgaben
            expense_id = request.form['expense_id']
            confirmed_value = request.form['confirmed_value']
            confirmed_date = request.form['confirmed_date']
            
            if expense_id and confirmed_value and confirmed_date:
                try:
                    confirmed_value = float(confirmed_value)
                    expense_owner = conn.execute('SELECT user_id FROM remarkable_expenses WHERE id = ?', (expense_id,)).fetchone()
                    if expense_owner and expense_owner['user_id'] == user_id:
                        conn.execute('UPDATE remarkable_expenses SET confirmed_value = ?, confirmed_date = ? WHERE id = ?',
                                     (confirmed_value, confirmed_date, expense_id))
                        conn.commit()
                        flash('Besondere Ausgabe erfolgreich bestätigt.', 'success')
                    else:
                        flash('Zugriff verweigert: Ausgabe gehört nicht diesem Benutzer.', 'danger')
                except ValueError:
                    flash('Ungültiger Betrag für die Bestätigung.', 'danger')
            else:
                flash('Alle Felder für die Bestätigung müssen ausgefüllt sein.', 'danger')

        return redirect(url_for('manage_remarkable_expenses'))

    remarkable_expenses = conn.execute(
        'SELECT id, description, amount, expense_date, category, is_estimated, confirmed_value, confirmed_date FROM remarkable_expenses WHERE user_id = ? ORDER BY expense_date DESC',
        (user_id,)
    ).fetchall()
    conn.close()
    return render_template('manage_remarkable_expenses.html', remarkable_expenses=remarkable_expenses)

# --- Routen für Einnahmenverwaltung ---
@app.route('/manage_incomes', methods=['GET', 'POST'])
def manage_incomes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_income':
            source = request.form['source'].strip()
            amount = request.form['amount']
            frequency = request.form['frequency']
            is_estimated = 1 if request.form.get('is_estimated') == 'on' else 0 # NEU

            if source and amount and frequency:
                try:
                    amount = float(amount)
                    conn.execute('INSERT INTO incomes (source, amount, frequency, user_id, is_estimated) VALUES (?, ?, ?, ?, ?)',
                                 (source, amount, frequency, user_id, is_estimated))
                    conn.commit()
                    flash(f'Einnahmequelle "{source}" erfolgreich hinzugefügt.', 'success')
                except ValueError:
                    flash('Ungültiger Betrag für die Einnahme.', 'danger')
            else:
                flash('Alle Felder für die Einnahme müssen ausgefüllt sein.', 'danger')
        
        elif action == 'delete_income':
            income_id = request.form['income_id']
            income_owner = conn.execute('SELECT user_id FROM incomes WHERE id = ?', (income_id,)).fetchone()
            if income_owner and income_owner['user_id'] == user_id:
                conn.execute('DELETE FROM incomes WHERE id = ? AND user_id = ?', (income_id, user_id))
                conn.commit()
                flash('Einnahmequelle erfolgreich gelöscht.', 'info')
            else:
                flash('Zugriff verweigert: Einnahme gehört nicht diesem Benutzer.', 'danger')
        
        elif action == 'confirm_income': # NEU: Bestätigungsaktion für geschätzte Einnahmen
            income_id = request.form['income_id']
            confirmed_value = request.form['confirmed_value']
            confirmed_date = request.form['confirmed_date']
            
            if income_id and confirmed_value and confirmed_date:
                try:
                    confirmed_value = float(confirmed_value)
                    income_owner = conn.execute('SELECT user_id FROM incomes WHERE id = ?', (income_id,)).fetchone()
                    if income_owner and income_owner['user_id'] == user_id:
                        conn.execute('UPDATE incomes SET confirmed_value = ?, confirmed_date = ? WHERE id = ?',
                                     (confirmed_value, confirmed_date, income_id))
                        conn.commit()
                        flash('Einnahmequelle erfolgreich bestätigt.', 'success')
                    else:
                        flash('Zugriff verweigert: Einnahme gehört nicht diesem Benutzer.', 'danger')
                except ValueError:
                    flash('Ungültiger Betrag für die Bestätigung.', 'danger')
            else:
                flash('Alle Felder für die Bestätigung müssen ausgefüllt sein.', 'danger')

        return redirect(url_for('manage_incomes'))

    incomes = conn.execute(
        'SELECT id, source, amount, frequency, is_estimated, confirmed_value, confirmed_date FROM incomes WHERE user_id = ?',
        (user_id,)
    ).fetchall()
    conn.close()
    return render_template('manage_incomes.html', incomes=incomes)

# --- Routen für Benutzerverwaltung ---
@app.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    if 'user_id' not in session or session['user_role'] != 'admin':
        flash('Zugriff verweigert. Nur Administratoren können Benutzer verwalten.', 'danger')
        return redirect(url_for('dashboard'))

    conn = get_db_connection()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_user':
            username = request.form['username'].strip()
            password = request.form['password']
            role = request.form.get('role', 'member')

            if not username or not password:
                flash('Benutzername und Passwort dürfen nicht leer sein.', 'danger')
            else:
                hashed_password = hash_password(password)
                try:
                    conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                                 (username, hashed_password, role))
                    conn.commit()
                    flash(f'Benutzer "{username}" erfolgreich hinzugefügt.', 'success')
                except sqlite3.IntegrityError:
                    flash('Dieser Benutzername existiert bereits.', 'danger')
            
            return redirect(url_for('manage_users'))
        
        elif action == 'delete_user':
            user_to_delete_id = request.form['user_id']
            
            if int(user_to_delete_id) == session['user_id']:
                flash('Du kannst dein eigenes Konto nicht löschen.', 'danger')
            else:
                user_info = conn.execute('SELECT username, role FROM users WHERE id = ?', (user_to_delete_id,)).fetchone()
                if user_info and user_info['username'] == 'admin':
                    flash('Der initiale Admin-Benutzer kann nicht gelöscht werden.', 'danger')
                else:
                    conn.execute('DELETE FROM incomes WHERE user_id = ?', (user_to_delete_id,))
                    conn.execute('DELETE FROM remarkable_expenses WHERE user_id = ?', (user_to_delete_id,))
                    fixed_cost_ids_to_delete = conn.execute('SELECT id FROM fixed_costs WHERE user_id = ?', (user_to_delete_id,)).fetchall()
                    for fc_id in fixed_cost_ids_to_delete:
                        conn.execute('DELETE FROM paid_fixed_costs WHERE fixed_cost_id = ?', (fc_id['id'],))
                    conn.execute('DELETE FROM fixed_costs WHERE user_id = ?', (user_to_delete_id,))
                    
                    account_ids_to_delete = conn.execute('SELECT id FROM accounts WHERE user_id = ?', (user_to_delete_id,)).fetchall()
                    for acc_id in account_ids_to_delete:
                        conn.execute('DELETE FROM account_snapshots WHERE account_id = ?', (acc_id['id'],))
                    conn.execute('DELETE FROM accounts WHERE user_id = ?', (user_to_delete_id,))
                    conn.execute('DELETE FROM prognosis_overrides WHERE user_id = ?', (user_to_delete_id,))
                    conn.execute('DELETE FROM dump_sheet_notes WHERE user_id = ?', (user_to_delete_id,)) # NEU: Dump Sheet Notizen löschen

                    conn.execute('DELETE FROM users WHERE id = ?', (user_to_delete_id,))
                    conn.commit()
                    flash(f'Benutzer "{user_info["username"]}" und alle zugehörigen Daten erfolgreich gelöscht.', 'info')
            
            return redirect(url_for('manage_users'))

    users = conn.execute('SELECT id, username, role FROM users').fetchall()
    conn.close()
    return render_template('manage_users.html', users=users)

# --- NEUE ROUTEN FÜR DUMP SHEET ---
@app.route('/dump_sheet', methods=['GET', 'POST'])
def dump_sheet():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_note':
            note_text = request.form['note_text'].strip()
            if note_text:
                created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                conn.execute('INSERT INTO dump_sheet_notes (user_id, note_text, created_at, is_categorized) VALUES (?, ?, ?, ?)',
                             (user_id, note_text, created_at, 0)) # is_categorized = 0 (false)
                conn.commit()
                flash('Notiz erfolgreich hinzugefügt.', 'success')
            else:
                flash('Notiz darf nicht leer sein.', 'danger')
        elif action == 'mark_categorized':
            note_id = request.form['note_id']
            conn.execute('UPDATE dump_sheet_notes SET is_categorized = 1 WHERE id = ? AND user_id = ?', (note_id, user_id))
            conn.commit()
            flash('Notiz als kategorisiert markiert.', 'info')
        elif action == 'delete_note':
            note_id = request.form['note_id']
            conn.execute('DELETE FROM dump_sheet_notes WHERE id = ? AND user_id = ?', (note_id, user_id))
            conn.commit()
            flash('Notiz gelöscht.', 'info')
        
        return redirect(url_for('dump_sheet'))

    uncategorized_notes = conn.execute(
        'SELECT id, note_text, created_at FROM dump_sheet_notes WHERE user_id = ? AND is_categorized = 0 ORDER BY created_at DESC',
        (user_id,)
    ).fetchall()
    conn.close()
    return render_template('dump_sheet.html', uncategorized_notes=uncategorized_notes)


# --- Start der App ---
if __name__ == '__main__':
    init_db()

    conn = get_db_connection()
    if not conn.execute("SELECT 1 FROM users WHERE username = 'admin'").fetchone():
        print("Erstelle Admin-Benutzer...")
        conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    ('admin', hash_password('adminpass'), 'admin'))
        conn.commit()
        print("Admin-Benutzer 'admin' mit Passwort 'adminpass' erstellt.")
    conn.close()
    app.run(debug=True)
