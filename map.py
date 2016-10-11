import numpy as np
import dxfgrabber
import cv2


def main():
	resolutionPower = 2
	housingMaxLenInMM = 70
	arrayLen = housingMaxLenInMM * 10 ** resolutionPower
	XYoffset = (41.90 + 5, 28.25+ 5)
	housing = np.ones((arrayLen ,arrayLen), np.uint8) * 255
	housing = drawPartsFromDxf(housing, r"C:\Users\eltoshon\Desktop\housing.dxf", XYoffset, resolutionPower, arrayLen)
	showImage(housing)

def drawPartsFromDxf(pixelArray, dxfFilePath, offset, resolution, arrayLength):
	black = (0, 0, 0)
	lineWidth = 5
	pixelArray = cv2.circle(pixelArray, (7000,0), 500, black,-1)
	pixelArray = cv2.circle(pixelArray, (7000,7000), 500, black,-1)

	dxf = dxfgrabber.readfile(dxfFilePath)
	entity = dxf.entities
	for part in entity:
		if part.dxftype == 'LINE':
			startP, endP = linePointsConversion(part.start, part.end, offset, resolution, arrayLength)
			print(startP, endP)
			pixelArray = cv2.line(pixelArray, startP, endP, black, lineWidth)
			
		if part.dxftype == 'ARC':
			center = part.center
			radius = part.radius
			sAngle = part.start_angle
			eAngle = part.end_angle
			center, radius = circleConversion(center, radius, offset, resolution, arrayLength)
			pixelArray = cv2.circle(pixelArray, center, radius, black, 5)
		
		if part.dxftype == 'CIRCLE':
			center = part.center
			radius = part.radius
			center, radius = circleConversion(center, radius, offset, resolution, arrayLength)
			pixelArray = cv2.circle(pixelArray, center, radius, black, 5)

	return pixelArray

def circleConversion(center, radius, offset, resolution, flip):
	center = ((int((center[0] + offset[0]) * 10**resolution)), flip - int((center[1] + offset[1]) * 10**resolution))
	radius = radius * 10**(resolution)
	if radius.is_integer():
		radius = int(radius)
	else:
		radius = int(radius) + 1
	return center, radius

def linePointsConversion(sPoint, ePoint, offset, resolution, flip):
	sPointX = (sPoint[0] + offset[0]) * 10**resolution
	sPointY = (sPoint[1] + offset[1]) * 10**resolution
	ePointX = (ePoint[0] + offset[0]) * 10**resolution
	ePointY = (ePoint[1] + offset[1]) * 10**resolution


	if sPointX > ePointX:
		if sPointX % 10 != 0:
			sPointX = int(sPointX) + 1
		else:
			sPointX = int(sPointX)
		ePointX = int(ePointX)
	else:
		if ePointX % 10 != 0:
			ePointX = int(ePointX) + 1
		else:
			ePointX = int(ePointX)
		sPointX = int(sPointX)

	if sPointY > ePointY:
		if sPointY % 10 != 0:
			sPointY = int(sPointY) + 1
		else:
			sPointY = int(sPointY)
		ePointY = int(ePointY)
	else:
		if ePointY % 10 != 0:
			ePointY = int(ePointY) + 1
		else:
			ePointY = int(ePointY)
		sPointY = int(sPointY)

	ePointY = flip - ePointY
	sPointY = flip - sPointY

	return (sPointX, sPointY), (ePointX, ePointY)


def showImage(pixelArray):
	cv2.namedWindow('window', cv2.WINDOW_KEEPRATIO)
	cv2.imshow('window', pixelArray)
	cv2.waitKey(0)

main()