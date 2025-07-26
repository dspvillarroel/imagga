import os
import sqlite3
import base64
import requests
from flask import Flask, render_template, request, g, send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Crear directorio de subidas si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configuración
IMAGGA_API_URL = "https://api.imagga.com/v2/tags"

# Database setup
DATABASE = 'results.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY,
                filename TEXT NOT NULL,
                tag1 TEXT,
                confidence1 REAL,
                tag2 TEXT,
                confidence2 REAL
            )
        ''')
        db.commit()
    return db

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    
    if request.method == 'POST':
        # Verificar si se envió el formulario de análisis
        if 'analyze' in request.form:
            # Obtener todas las imágenes analizadas de la base de datos
            cursor = db.cursor()
            cursor.execute("SELECT * FROM results")
            results = cursor.fetchall()
            
            # Formatear resultados para la plantilla
            images = []
            for row in results:
                images.append({
                    'filename': row[1],
                    'tags': [
                        {'tag': row[2], 'confidence': row[3]},
                        {'tag': row[4], 'confidence': row[5]}
                    ] if row[2] else None
                })
            return render_template('index.html', images=images)
        
        # Procesar subida de archivos
        files = request.files.getlist('file')
        results = []
        
        for file in files[:3]:  # Procesar máximo 3 imágenes
            if file and allowed_file(file.filename):
                filename = file.filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Convertir imagen a base64 para Imagga
                with open(filepath, 'rb') as image_file:
                    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
                
                # Llamar a Imagga API
                response = requests.post(
                    IMAGGA_API_URL,
                    data={'image_base64': image_base64},
                    auth=(os.getenv('IMAGGA_API_KEY'), os.getenv('IMAGGA_API_SECRET'))
                )
                
                if response.status_code == 200:
                    tags = response.json().get('result', {}).get('tags', [])[:2]
                    
                    if tags:
                        # Guardar en DB
                        cursor = db.cursor()
                        cursor.execute(
                            "INSERT INTO results (filename, tag1, confidence1, tag2, confidence2) VALUES (?, ?, ?, ?, ?)",
                            (filename, tags[0]['tag']['en'], tags[0]['confidence'], 
                             tags[1]['tag']['en'], tags[1]['confidence'] if len(tags) > 1 else None)
                        )
                        db.commit()
                        
                        results.append({
                            'filename': filename,
                            'tags': [
                                {'tag': tags[0]['tag']['en'], 'confidence': tags[0]['confidence']},
                                {'tag': tags[1]['tag']['en'], 'confidence': tags[1]['confidence']} if len(tags) > 1 else None
                            ]
                        })
                    else:
                        results.append({'filename': filename, 'error': 'No se encontraron etiquetas'})
                else:
                    results.append({'filename': filename, 'error': f'Error API: {response.status_code}'})
        
        return render_template('index.html', upload_results=results)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)