import cv2
import pytesseract
import imutils
import mysql.connector
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def conectar(host, user, senha, banco):
    return mysql.connector.connect(host=host, user=user, password=senha, database=banco)

def read_license_plate(image):
    # Converter a imagem em escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aplicar filtro de suavização para reduzir o ruído
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detectar as bordas da placa de licença
    edged = cv2.Canny(blurred, 100, 200)

    # Encontrar contornos na imagem
    contours = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    # Ordenar os contornos pela área e manter apenas os maiores
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    for contour in contours:
        # Aproximar o contorno para uma forma retangular
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

        # Se a figura for um retângulo, consideramos que é a placa de licença
        if len(approx) == 4:
            (x, y, w, h) = cv2.boundingRect(approx)

            # Recortar a região da placa de licença
            plate = gray[y:y + h, x:x + w]

            # Usar Tesseract para reconhecer o texto na placa de licença
            plate_text = pytesseract.image_to_string(plate, config='--psm 11')

            # Se encontrou algum texto, retorna
            if plate_text:
                return plate_text.strip()

    # Se não encontrou nenhuma placa de licença, retorna None
    return None

def main():
    # Inicializar a webcam
    cap = cv2.VideoCapture(0)

    while True:
        # Capturar frame da webcam
        ret, frame = cap.read()

        # Verificar se o frame foi capturado corretamente
        if not ret:
            print("Erro ao capturar o frame")
            break

        # Detectar e ler a placa de licença
        plate_text = read_license_plate(frame)

        # Se placa de licença foi detectada, exibir o texto
        if plate_text:
            print("Placa de licença:", plate_text)

        # Exibir o frame
        cv2.imshow('Frame', frame)

        conn = conectar("localhost", "root", "Projeto0324.", "armaz_placas")
        c = conn.cursor()

        data_hora_acesso = datetime.now()

        # Pressione 'q' para sair do loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        

        c.execute("INSERT INTO placas (placa, data_hora_acesso) VALUES (%s, %s)", (plate_text, data_hora_acesso))
        conn.commit()

        def listar_placas():
            c.execute("SELECT * FROM placas")
            placas = c.fetchall()
            print("Placas armazenadas:")
            for placa in placas:
                print(placa)
        
        c.close()
        conn.close()
    # Liberar a webcam e fechar todas as janelas
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
