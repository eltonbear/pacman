import numpy as np
import dxfgrabber
import cv2

def main():
	resolutionPower = 2
	housingMaxLenInMM = 65
	arrayLen = housingMaxLenInMM * 10 ** resolutionPower
	XYoffset = (41.90 + 5, 28.25+ 5)
	housing = np.ones((arrayLen ,arrayLen), np.uint8) * 255
	housing = drawPartsFromDxf(housing, r"C:\Users\eltoshon\Desktop\housing.dxf", XYoffset, resolutionPower, arrayLen)
	showImage(housing)

def drawPartsFromDxf(pixelArray, dxfFilePath, offset, resolution, arrayLength):
	black = (0, 0, 0)
	lineWidth = 3
	dxf = dxfgrabber.readfile(dxfFilePath)
	entity = dxf.entities
	for part in entity:
		if part.dxftype == 'LINE':  # maybe need to add polyline
			startP, endP = linePointsConversion(part.start, part.end, offset, resolution, arrayLength)
			pixelArray = cv2.line(pixelArray, startP, endP, black, lineWidth)
			
		if part.dxftype == 'ARC':
			center = part.center
			radius = part.radius
			deltaAngle = abs(part.end_angle - part.start_angle)
			if part.end_angle < part.start_angle:
				deltaAngle = 360 - deltaAngle
			sAngle = 360 - part.end_angle
			eAngle = sAngle + deltaAngle
			center, radius = circleConversion(center, radius, offset, resolution, arrayLength)
			pixelArray = cv2.ellipse(pixelArray, center, (radius, radius), 0, sAngle, eAngle, black, lineWidth)

		if part.dxftype == 'CIRCLE':
			center = part.center
			radius = part.radius
			center, radius = circleConversion(center, radius, offset, resolution, arrayLength)
			pixelArray = cv2.circle(pixelArray, center, radius, black, lineWidth)

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
	sPointX = (sPoint[0] + offset[0]) * 10**(resolution+1)
	sPointY = (sPoint[1] + offset[1]) * 10**(resolution+1)
	ePointX = (ePoint[0] + offset[0]) * 10**(resolution+1)
	ePointY = (ePoint[1] + offset[1]) * 10**(resolution+1)

	if sPointX > ePointX:
		if sPointX % 10 != 0:
			sPointX = int(sPointX/10) + 1
		else:
			sPointX = int(sPointX/10) 
		ePointX = int(ePointX/10)
	else:
		if ePointX % 10 != 0:
			ePointX = int(ePointX/10)  + 1
		else:
			ePointX = int(ePointX/10) 
		sPointX = int(sPointX/10)

	if sPointY > ePointY:
		if sPointY % 10 != 0:
			sPointY = int(sPointY/10) + 1
		else:
			sPointY = int(sPointY/10) 
		ePointY = int(ePointY/10) 
	else:
		if ePointY % 10 != 0:
			ePointY = int(ePointY/10) + 1
		else:
			ePointY = int(ePointY/10)
		sPointY = int(sPointY/10)

	ePointY = flip - ePointY
	sPointY = flip - sPointY
	return (sPointX, sPointY), (ePointX, ePointY)

def showImage(pixelArray):
	cv2.namedWindow('window', cv2.WINDOW_KEEPRATIO)
	cv2.imshow('window', pixelArray)
	cv2.waitKey(0)
	cv2.imwrite(r"C:\Users\eltoshon\Desktop\housingIMAGE.jpeg", pixelArray)

main()