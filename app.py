from flask import Flask, request, jsonify, render_template
import os
import cv2
import pickle
import extrairGabarito as exG
from PIL import Image
from io import BytesIO
import numpy as np

app = Flask(__name__)

# Configuração da pasta de upload
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Rota para servir o arquivo HTML
@app.route('/')
def index():
    return render_template('index.html',  mimetype='text/html')

# Rota para receber a imagem
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Nome do arquivo vazio"}), 400
    
    image_bytes = file.read()
    
    retorno = pontuacao(convert_image(image_bytes))

    # Salva o arquivo na pasta 'uploads'
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    return jsonify(retorno), 200

def pontuacao(imagem):
    campos = []
    with open('campos.pkl', 'rb') as arquivo:
        campos = pickle.load(arquivo)

    resp = []
    with open('resp.pkl', 'rb') as arquivo:
        resp = pickle.load(arquivo)

    respostasCorretas = ["1-A","2-C","3-B","4-D","5-A"]

    gabarito,bbox = exG.extrairMaiorCtn(imagem)
    imgGray = cv2.cvtColor(gabarito, cv2.COLOR_BGR2GRAY)
    ret,imgTh = cv2.threshold(imgGray,70,255,cv2.THRESH_BINARY_INV)
    cv2.rectangle(imagem, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255,0), 3)
 
    respostas = []
    for id,vg in enumerate(campos):
        x = int(vg[0])
        y = int(vg[1])
        w = int(vg[2])
        h = int(vg[3])
        cv2.rectangle(gabarito, (x, y), (x + w, y + h),(0,0,255),2)
        cv2.rectangle(imgTh, (x, y), (x + w, y + h), (255, 255, 255), 1)
        campo = imgTh[y:y + h, x:x + w]
        height, width = campo.shape[:2]
        tamanho = height * width
        pretos = cv2.countNonZero(campo)
        percentual = round((pretos / tamanho) * 100, 2)
        if percentual >=10:
            cv2.rectangle(gabarito, (x, y), (x + w, y + h), (255, 0, 0), 2)
            respostas.append(resp[id])

    #print(respostas)
    erros = 0
    acertos = 0
    if len(respostas)==len(respostasCorretas):
        for num,res in enumerate(respostas):
            if res == respostasCorretas[num]:
                #print(f'{res} Verdadeiro, correto: {respostasCorretas[num]}')
                acertos +=1
            else:
                #print(f'{res} Falso, correto: {respostasCorretas[num]}')
                erros +=1

    return {"erros": erros, "acertos": acertos, "pontuacao": int(acertos * 6)};


# Função para converter imagem em formato JPEG para escala de cinza
def convert_image(image_bytes):
    # Abre a imagem com PIL (Pillow)
    image = Image.open(BytesIO(image_bytes))
    
    # Converte a imagem para um formato NumPy (o que o OpenCV entende)
    return np.array(image)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)