import numpy as np
import dxfgrabber
import cv2
import math

# In an array coordinate system positive Y points downward and postive X points to the right. To access an array value with a point (x, y), do array[y][x]. In the case below y = a,b,c,d. x = 0,1,2,3
#[a]->[0,1,2,3...]
#[b]->[0,1,2,3...]
#[c]->[0,1,2,3...]
#[d]->[0,1,2,3...]
#[e]->[0,1,2,3...]

class pixelMap:
	def __init__(self, dxfFile):
		self.backGrdColor = 0
		self.wallColor = 255
		resolutionPower = 2
		housingMaxXInMM = 25
		housingMaxYInMM = 16

		self.arrayXlen = housingMaxXInMM * 10 ** resolutionPower 
		self.arrayYlen = housingMaxYInMM * 10 ** resolutionPower 
		XYoffset = (0, 0)

		self.housingImg = np.zeros((self.arrayYlen, self.arrayXlen), np.uint8)
		self.drawPartsFromDxf(dxfFile, XYoffset, resolutionPower)

		self.firstPoint = findFirstPoint(self.housingImg)


	def drawPartsFromDxf(self, dxfFilePath, offset, resolution):
		lineWidth = 3
		dxf = dxfgrabber.readfile(dxfFilePath)
		entity = dxf.entities
		for part in entity:
			if part.dxftype == 'LINE':  # maybe need to add polyline
				startP, endP = linePointsConversion(part.start, part.end, offset, resolution)
				self.housingImg = cv2.line(self.housingImg, startP, endP, self.wallColor, lineWidth)
				
			if part.dxftype == 'ARC':
				center = part.center
				radius = part.radius
				if part.end_angle < part.start_angle:
					part.start_angle = part.start_angle - 360

				center, radius = circleConversion(center, radius, offset, resolution)
				self.housingImg = cv2.ellipse(self.housingImg, center, (radius, radius), 0, part.start_angle, part.end_angle, self.wallColor, lineWidth)

			if part.dxftype == 'CIRCLE':
				center = part.center
				radius = part.radius
				center, radius = circleConversion(center, radius, offset, resolution)
				self.housingImg = cv2.circle(self.housingImg, center, radius, self.wallColor, lineWidth)

	def inBounds(self, point):
		(x, y) = point
		return 0 <= x < self.arrayXlen and 0 <= y < self.arrayYlen

	def passable(self, point):
		return self.housingImg[point[1], point[0]] != self.wallColor

	def getNeighbors(self, point):
		(x, y) = point
		neighbors = [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]
		costDict = {point: 1 for point in neighbors}
		if (x + y) % 2 == 0: neighbors.reverse() # aesthetics
		neighbors = filter(self.inBounds, neighbors)
		neighbors = filter(self.passable, neighbors)
		return neighbors, costDict

	def getPixelArray(self):
		return self.housingImg


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

	return (sPointX, sPointY), (ePointX, ePointY)

def showImage(pixelArray, saveImg):
	flippedImage = cv2.flip(pixelArray, 0)
	cv2.namedWindow('window', cv2.WINDOW_KEEPRATIO)
	cv2.imshow('window', flippedImage)
	cv2.waitKey(0)
	cv2.imwrite(saveImg, flippedImage)

def findFirstPoint(pixelArray):
	# Find smallest x in a fixed y
	for yIndex in range(0, len(pixelArray)):
		for xIndex in range(0, len(pixelArray[0])):
			if pixelArray[yIndex][xIndex] != 0:
				return (xIndex, yIndex)

def covertToNpArrayPoint(points):

	return np.array(points)

def drawPolyline(pixelArray, points):

	pixelArray =  cv2.polylines(pixelArray, [points], False, 150)

	return pixelArray

# if __name__ == "__main__":
# 	dxf = r"C:\Users\eltoshon\Desktop\drawings\housingPathFindTest\housingPathFindTest.dxf"
# 	saveImg = r"C:\Users\eltoshon\Desktop\drawings\housingPathFindTest\housingPathFindTest.jpeg"
# 	m = pixelMap(dxf)
# 	points = covertToNpArrayPoint([(1, 5),  (5, 9), (500, 25)])
# 	drawPolyline(m.getPixelArray(), points)
# 	fp = m.firstPoint
# 	print(fp)
# # 	print(m.passable(fp))
# # 	print(m.passable((288, 184)))
# # 	print(m.passable((286, 184)))
# # 	print(m.passable((287, 185)))
# # 	print(m.passable((287, 183)))
# 	n, c= m.getNeighbors(fp)
# 	n = list(n)
# 	print(n)
# 	print(c)
	# print(c[(288, 184)])
	# print(c[n[0]])


	# showImage(m.getPixelArray(), saveImg)