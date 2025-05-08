from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os
from werkzeug.utils import secure_filename

import os
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

app.secret_key = 'supersecretkey'  # Để sử dụng session

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['excel_file']
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        session['file_path'] = path

        # Lấy danh sách sheet
        xls = pd.ExcelFile(path)
        sheets = xls.sheet_names
        return render_template('select_sheet.html', sheets=sheets)

    return render_template('upload.html')

@app.route('/select-sheet', methods=['POST'])
def select_sheet():
    sheet = request.form['sheet']
    session['sheet'] = sheet
    file_path = session['file_path']
    df = pd.read_excel(file_path, sheet_name=sheet)
    df = df[df['Enable'] == 1].reset_index(drop=True)
    session['data'] = df.to_dict(orient='records')
    session['index'] = 0
    session['direction'] = 'Nghia'  # hoặc 'Tu'
    return redirect(url_for('study'))

@app.route('/set-direction/<direction>')
def set_direction(direction):
    session['direction'] = direction
    session['index'] = 0
    return redirect(url_for('study'))

@app.route('/study', methods=['GET', 'POST'])
def study():
    data = session.get('data', [])
    index = session.get('index', 0)
    direction = session.get('direction', 'Nghia')

    if index >= len(data):
        return render_template('complete.html')

    row = data[index]
    show = row[direction]
    correct = row['Tu']
    nghia = row['Nghia']
    pinyin = row['Pinyin']

    if request.method == 'POST':
        answer = request.form['answer'].strip()
        if (direction == 'Nghia' and answer == row['Tu']) or (direction == 'Tu' and answer == row['Nghia']):
            session['index'] = index + 1
            return redirect(url_for('study'))
        else:
            return render_template('study.html', show=show, correct=correct, nghia=nghia,
                                   pinyin=pinyin, incorrect=True, direction=direction)

    return render_template('study.html', show=show, correct=correct, nghia=nghia,
                           pinyin=pinyin, incorrect=False, direction=direction)

@app.route('/reset')
def reset():
    session['index'] = 0
    return redirect(url_for('study'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
