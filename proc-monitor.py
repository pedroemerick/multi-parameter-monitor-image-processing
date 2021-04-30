# importando pacotes necessários
import argparse
import cv2
import pytesseract # Módulo para a utilização da tecnologia OCR
import re
import math

# inicializando a lista de pontos da imagem para serem recortados e booleano de controle para verificar se está realizando corte ou não
cropping = False
imageCrops = []
refPt = []

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
	r = 150.0 / image.shape[1]
	dim = (150, int(image.shape[0] * r))
	resized = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

	gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
	rn = cv2.medianBlur(gray,5)
	canny = cv2.Canny(rn, 100, 200)
	ref = cv2.threshold(canny, 10, 255, cv2.THRESH_BINARY_INV)[1]
	thresh = cv2.threshold(ref, 180, 255, cv2.THRESH_BINARY)[1]

	return thresh

# Função que realiza a leitura do dígito na passada por parâmetro utilizando o tesseract
def getNumberOfImage(image):
	image = imageProcessing(image)

	custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
	result = pytesseract.image_to_string(image, config=custom_config)
	print('7:',result, end='')
	custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789'
	result = pytesseract.image_to_string(image, config=custom_config)
	print('8:',result, end='')
	custom_config = r'--oem 3 --psm 13 -c tessedit_char_whitelist=0123456789'
	result = pytesseract.image_to_string(image, config=custom_config)
	print('13:',result, end='')

	numbers = re.findall(r'\d+', result)
	return int(numbers[0]) if numbers else None

# Função que realiza a leitura dos frames do video
def readFrames(videoPath):
	frames = []
	cap = cv2.VideoCapture(videoPath)
	frameRate = cap.get(5)

	while(cap.isOpened()):
		if len(frames) == 10:
			break

		frameId = cap.get(1) # frame atual
		ret, frame = cap.read()

		if (ret != True):
			break
		if (frameId % math.floor(frameRate) == 0):
			frames.append(frame)
	
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
			cv2.putText(image, "1- Selecione a area do " + prop, (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
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

# mostra o vídeo
print(videoPath)

# carrega os frames do vídeo
frames = readFrames(videoPath)

if frames:
	frame = frames[0]
	getAreas(frame)

values = {prop: [] for prop in properties}

# percorre loop dos frames selecionados e realiza o processamento para cada frame
for frame in frames:
	for ii, crop in enumerate(imageCrops):
		if len(crop) == 2:
			roi = frame[crop[0][1]:crop[1][1], crop[0][0]:crop[1][0]]
			values[properties[ii]].append(getNumberOfImage(roi))

print(values)

# close all open windows
cv2.destroyAllWindows()