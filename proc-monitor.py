# importando pacotes necessários
import argparse
import cv2
import pytesseract # Módulo para a utilização da tecnologia OCR
import re
import math
from tabulate import tabulate
import time
import calendar
import imutils

# inicializando a lista de pontos da imagem para serem recortados e booleano de controle para verificar se está realizando corte ou não
cropping = False
imageCrops = []
refPt = []
numFrames = 100

# Função que define as funções do mouse para que seja possivel selecionar as areas
def clickAndCrop(event, x, y, flags, param):
	if not bool(param[0]):
		return

	global refPt, imageCrops, cropping

	# captura evento de clique inicial para obter coordenadas iniciais
	if event == cv2.EVENT_LBUTTONDOWN:
		refPt = [(x, y)]
		cropping = True
	# verifica se o botão direito do mouse foi solto
	elif event == cv2.EVENT_LBUTTONUP:
		# armazena as coordenadas finais e finaliza a operação
		refPt.append((x, y))
		cropping = False

		# desenha retângulo na área selecionada
		cv2.rectangle(param[2], refPt[0], refPt[1], (0, 255, 0), 2)
		cv2.putText(param[2], param[1], (refPt[0][0], refPt[0][1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
		cv2.imshow("image", param[2])

		imageCrops.append(refPt)

# Função que realiza o tratamento da imagem
def imageProcessing(image):
	resized = imutils.resize(image, width=150)
	gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
	rn = cv2.medianBlur(gray,5)
	canny = cv2.Canny(rn, 100, 200)
	ref = cv2.threshold(canny, 10, 255, cv2.THRESH_BINARY_INV)[1]
	thresh = cv2.threshold(ref, 180, 255, cv2.THRESH_BINARY)[1]
	
	return thresh

# Função que realiza a leitura do dígito na passada por parâmetro utilizando o tesseract
def getNumberOfImage(image):
	image = imageProcessing(image)

	custom_config = r'--oem 3 --psm 13'
	result = pytesseract.image_to_string(image, config=custom_config)

	numbers = re.findall(r'\d+', result)
	return numbers[0] if numbers else '-'

# Função que realiza a leitura dos frames do video
def readFrames(videoPath):
	frames = []
	cap = cv2.VideoCapture(videoPath)
	frameRate = cap.get(5)

	while(cap.isOpened()):
		if len(frames) == numFrames:
			break

		frameId = cap.get(1) # frame atual
		ret, frame = cap.read()

		if (ret != True):
			break
		if (frameId % math.floor(frameRate) == 0):
			resized = imutils.resize(frame, width=1440)
			frames.append(resized)

	cap.release()

	return frames

# Função que solicita ao usuário que informe as áreas das propriedades para leitura dos dados
def getAreas(image):
	clone = image.copy()
	cv2.namedWindow("image")

	(h, w) = image.shape[:2]

	# continua executando até a tecla 'q' ser pressionada
	while True:
		if(len(imageCrops) < len(properties)):
			prop = properties[len(imageCrops)]
			cv2.setMouseCallback("image", clickAndCrop, [True, prop, image])

			# mostra a imagem e aguarda pela ação do usuário
			cv2.imshow("image", image)
			cv2.putText(image, "Selecione a area da propriedade", (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
		else:
			cv2.setMouseCallback("image", clickAndCrop, [False])

		key = cv2.waitKey(1) & 0xFF

		# reseta a seleção caso 'r' seja pressionado
		if key == ord("r"):
			image = clone.copy()
			imageCrops.pop()
			for ii, crop in enumerate(imageCrops):
				cv2.putText(image, properties[ii], (crop[0][0], crop[0][1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
				cv2.rectangle(image, crop[0], crop[1], (0, 255, 0), 2)
			
		# finaliza a seleção caso 'c' seja pressionado
		elif key == ord("c"):
			break

# recebe os argumentos para execução inicial
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True, help="Caminho para o video")
ap.add_argument("-p", "--properties", nargs='+', required=True, help="Propriedades a serem lidas")
args = vars(ap.parse_args())

# carrega as propriedades a serem lidas
properties = [prop.upper() for prop in args["properties"]]

# carrega path do vídeo
videoPath = args["video"]

print("--> Informações recebidas")
print("Video:", videoPath)
print("Propriedades:", properties)

# carrega os frames do vídeo
print("\n--> Lendo frames do vídeo...")
frames = readFrames(videoPath)

if frames:
	frame = frames[0]
	print("\n--> Recebendo as áreas das propriedades...")
	getAreas(frame.copy())

# fecha todas as janelas abertas
cv2.destroyAllWindows()

values = {prop: [] for prop in properties}

headers = ["TIMESTAMP"]
for prop in properties:
	headers.append(prop)

formatRow = "{:>12}" * (len(headers))
print("\n--> Dados lidos")
print(formatRow.format(*headers))

# percorre loop dos frames selecionados e realiza o processamento para cada frame
for frame in frames:
	gmt = time.gmtime()
	ts = calendar.timegm(gmt)

	aux = []
	aux.append(ts)

	for ii, crop in enumerate(imageCrops):
		if len(crop) == 2:
			roi = frame[crop[0][1]:crop[1][1], crop[0][0]:crop[1][0]]
			number = getNumberOfImage(roi)

			values[properties[ii]].append(number)
			aux.append(number)

			cv2.rectangle(frame, crop[0], crop[1], (0, 255, 0), 2)
			cv2.putText(frame, number, (crop[0][0], crop[0][1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
			cv2.imshow('frame', frame)

			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
	
	print(formatRow.format(*aux))

# fecha todas as janelas abertas
cv2.destroyAllWindows()