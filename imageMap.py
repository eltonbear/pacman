import numpy as np
import dxfgrabber
import cv2
import math

def createMap(dxfFile):
	resolutionPower = 2
	housingMaxXInMM = 25
	housingMaxYInMM = 16


	arrayXlen = housingMaxXInMM * 10 ** resolutionPower 
	arrayYlen = housingMaxYInMM * 10 ** resolutionPower 
	XYoffset = (0, 0)

	housing = np.zeros((arrayYlen, arrayXlen), np.uint8)
	housing = drawPartsFromDxf(housing, dxfFile, XYoffset, resolutionPower)

	firstPoint = findFirstPoint(housing)

	return housing, firstPoint


def drawPartsFromDxf(pixelArray, dxfFilePath, offset, resolution):
	pixelArray[5][2] = 0
	white = 225
	lineWidth = 3
	dxf = dxfgrabber.readfile(dxfFilePath)
	entity = dxf.entities
	for part in entity:
		if part.dxftype == 'LINE':  # maybe need to add polyline

			startP, endP = linePointsConversion(part.start, part.end, offset, resolution)
			pixelArray = cv2.line(pixelArray, startP, endP, white, lineWidth)
			
		if part.dxftype == 'ARC':
			center = part.center
			radius = part.radius
			# print(center, radius, part.start_angle, part.end_angle, part.end_angle < part.start_angle)

			if part.end_angle < part.start_angle:
				part.start_angle = part.start_angle - 360

			center, radius = circleConversion(center, radius, offset, resolution)
			pixelArray = cv2.ellipse(pixelArray, center, (radius, radius), 0, part.start_angle, part.end_angle, white, lineWidth)

		if part.dxftype == 'CIRCLE':
			center = part.center
			radius = part.radius

			center, radius = circleConversion(center, radius, offset, resolution)
			pixelArray = cv2.circle(pixelArray, center, radius, white, lineWidth)
	# pixelArray = cv2.circle(pixelArray, (500,100), 50, white, lineWidth)


	return pixelArray

def circleConversion(center, radius, offset, resolution):
	center = ((int((center[0] + offset[0]) * 10**resolution)), int((center[1] + offset[1]) * 10**resolution))
	radius = radius * 10**(resolution)
	if radius.is_integer():
		radius = int(radius)
	else:
		radius = int(radius) + 1
	return center, radius

def linePointsConversion(sPoint, ePoint, offset, resolution):
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

	ePointY = ePointY
	sPointY = sPointY
	return (sPointX, sPointY), (ePointX, ePointY)

def showImage(pixelArray, saveImg):
	flippedImage = cv2.flip(pixelArray, 0)
	cv2.namedWindow('window', cv2.WINDOW_KEEPRATIO)
	cv2.imshow('window', flippedImage)
	cv2.waitKey(0)
	cv2.imwrite(saveImg, flippedImage)

def findFirstPoint(pixelArray):
	for yIndex in range(0, len(pixelArray)):
		for xIndex in range(0, len(pixelArray[0])):
			if pixelArray[yIndex][xIndex] != 0:
				return (xIndex, yIndex)