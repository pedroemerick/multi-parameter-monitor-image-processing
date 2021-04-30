# import the necessary packages
import argparse
import cv2
import pytesseract # Módulo para a utilização da tecnologia OCR
import re

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
cropping = False
imageCrops = []
refPt = []

def click_and_crop(event, x, y, flags, param):
	if not bool(param[0]):
		return

	# grab references to the global variables
	global refPt, imageCrops, cropping
	# if the left mouse button was clicked, record the starting
	# (x, y) coordinates and indicate that cropping is being
	# performed
	if event == cv2.EVENT_LBUTTONDOWN:
		refPt = [(x, y)]
		cropping = True
	# check to see if the left mouse button was released
	elif event == cv2.EVENT_LBUTTONUP:
		# record the ending (x, y) coordinates and indicate that
		# the cropping operation is finished
		refPt.append((x, y))
		cropping = False
		# draw a rectangle around the region of interest
		cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 2)
		cv2.putText(image, param[1], (refPt[0][0], refPt[0][1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
		cv2.imshow("image", image)

		imageCrops.append(refPt)

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

def getNumberOfImage(image):
	image = imageProcessing(image)
	cv2.imshow("proc", image)

	# custom_config = r'--oem 3 --psm 1 -c tessedit_char_whitelist=0123456789'
	# result = pytesseract.image_to_string(image, config=custom_config)
	# print('2:',result)
	# custom_config = r'--oem 3 --psm 3 -c tessedit_char_whitelist=0123456789'
	# result = pytesseract.image_to_string(image, config=custom_config)
	# print('3:',result)
	# custom_config = r'--oem 3 --psm 4 -c tessedit_char_whitelist=0123456789'
	# result = pytesseract.image_to_string(image, config=custom_config)
	# print('4:',result)
	# custom_config = r'--oem 3 --psm 5 -c tessedit_char_whitelist=0123456789'
	# result = pytesseract.image_to_string(image, config=custom_config)
	# print('5:',result)
	# custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
	# result = pytesseract.image_to_string(image, config=custom_config)
	# print('6:',result)
	custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
	result = pytesseract.image_to_string(image, config=custom_config)
	print('7:',result, end='')
	custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789'
	result = pytesseract.image_to_string(image, config=custom_config)
	print('8:',result, end='')
	# custom_config = r'--oem 3 --psm 9 -c tessedit_char_whitelist=0123456789'
	# result = pytesseract.image_to_string(image, config=custom_config)
	# print('9:',result)
	# custom_config = r'--oem 3 --psm 10 -c tessedit_char_whitelist=0123456789'
	# result = pytesseract.image_to_string(image, config=custom_config)
	# print('10:',result)
	# custom_config = r'--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789'
	# result = pytesseract.image_to_string(image, config=custom_config)
	# print('11:',result)
	# custom_config = r'--oem 3 --psm 12 -c tessedit_char_whitelist=0123456789'
	# result = pytesseract.image_to_string(image, config=custom_config)
	# print('12:',result, end='')
	custom_config = r'--oem 3 --psm 13 -c tessedit_char_whitelist=0123456789'
	result = pytesseract.image_to_string(image, config=custom_config)
	print('13:',result, end='')

	return re.findall(r'\d+', result)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Caminho para a imagem")
ap.add_argument("-p", "--properties", nargs='+', required=True, help="Propriedades a serem lidas")
args = vars(ap.parse_args())

# load the image, clone it, and setup the mouse callback function
properties = [prop.upper() for prop in args["properties"]]

image = cv2.imread(args["image"])
clone = image.copy()
cv2.namedWindow("image")

(h, w) = image.shape[:2]

# keep looping until the 'q' key is pressed
while True:
	if(len(imageCrops) < len(properties)):
		prop = properties[len(imageCrops)]
		cv2.setMouseCallback("image", click_and_crop, [True, prop])

		# display the image and wait for a keypress
		cv2.imshow("image", image)
		cv2.putText(image, "1- Selecione a area do " + prop, (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
	else:
		cv2.setMouseCallback("image", click_and_crop, [False])

	key = cv2.waitKey(1) & 0xFF
	# if the 'r' key is pressed, reset the cropping region
	if key == ord("r"):
		image = clone.copy()
		imageCrops.pop()
		for ii, crop in enumerate(imageCrops):
			cv2.putText(image, properties[ii], (crop[0][0], crop[0][1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
			cv2.rectangle(image, crop[0], crop[1], (0, 255, 0), 2)
		
	# if the 'c' key is pressed, break from the loop
	elif key == ord("c"):
		break
	

# if there are two reference points, then crop the region of interest
# from teh image and display it
for ii, crop in enumerate(imageCrops):
	if len(crop) == 2:
		roi = clone[crop[0][1]:crop[1][1], crop[0][0]:crop[1][0]]
		print(properties[ii], getNumberOfImage(roi))
		cv2.imshow("ROI", roi)
		cv2.waitKey(0)

# close all open windows
cv2.destroyAllWindows()