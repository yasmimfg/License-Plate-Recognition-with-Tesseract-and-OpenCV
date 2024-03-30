import cv2
import pytesseract
from imutils.video import VideoStream
import imutils
import mysql.connector
from datetime import datetime 
import re
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def conectar(host, user, senha, banco):
    return mysql.connector.connect(host=host, user=user, password=senha, database=banco)

def open_webcam_and_process():
    # Inicialize a webcam
    cap = cv2.VideoCapture(0)

    # Verifique se a webcam foi aberta corretamente
    if not cap.isOpened():
        print("Erro ao abrir a webcam")
        return

    while True:
        # Captura o frame
        ret, frame = cap.read()

        # Verifica se o frame foi capturado corretamente
        if not ret:
            print("Erro ao capturar o frame")
            break

        # Redimensionando o frame para um tamanho específico (opcional)
        frame = imutils.resize(frame, width=800)

        # Convertendo o frame para escala de cinza
        frame_cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Aplicando um desfoque para melhorar o OCR
        frame_desfocado = cv2.GaussianBlur(frame_cinza, (5, 5), 0)
 
        # Usando o Tesseract para realizar o OCR no frame
        placa = pytesseract.image_to_string(frame_desfocado, config='--psm 8')

        placa_filtrada = re.sub(r'[^a-zA-Z0-9]', '', placa)
        # Exibindo a placa detectada
        print('Placa do carro:', placa_filtrada)

        # Conectar ao banco de dados
        conn = conectar("localhost", "root", "Projeto0324.", "armaz_placas")
        c = conn.cursor()

        # Obter data e hora atual
        data_hora_acesso = datetime.now()

        # Inserir a placa no banco de dados
        c.execute("INSERT INTO placas (placa, data_hora_acesso) VALUES (%s, %s)", (placa_filtrada, data_hora_acesso))
        conn.commit()
        print("Placa inserida com sucesso!")

                
        def listar_placas():
            c.execute("SELECT * FROM placas")
            placas = c.fetchall()
            print("Placas armazenadas:")
            for placa in placas:
                print(placa)
        
        c.close()
        conn.close()

        # Exibindo o frame com a placa destacada (opcional)
        cv2.imshow('Frame', frame)

        # Verifique se o usuário pressionou a tecla 'q' para sair do loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Libera a webcam e fecha a janela
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    open_webcam_and_process()