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
		self.dxfObject = dxfgrabber.readfile(dxfFile)
		self.unins = 'mm'
		self.backGrdColor = 0
		self.wallColor = 255
		self.resolutionPower = 2
		self.housingMaxXInMM = 0
		self.housingMaxYInMM = 0
		self.XYoffset = (0, 0)
		self.XYmin = (0, 0)	

		self.getMaxAndMinXY()

		self.arrayXlen = self.housingMaxXInMM * 10 ** self.resolutionPower 
		self.arrayYlen = self.housingMaxYInMM * 10 ** self.resolutionPower 

		self.housingImg = np.zeros((self.arrayYlen, self.arrayXlen), np.uint8)
		self.contourImgPlain = np.copy(self.housingImg)
		self.drawPartsFromDxf(93, 2)
		self.contourImg = np.copy(self.housingImg)
		self.contourImg = cv2.bilateralFilter(self.contourImg, 9, 80, 80)
		
	def drawPartsFromDxf(self, lineWidth1, lineWidth2):
		# line width = 1 --> 1 pixel
		# line width = 94-100 --> 50 pixel # 93 for now
		entities = self.dxfObject.entities
		offset = self.XYoffset
		for part in entities:
			if part.dxftype == 'LINE':  # maybe need to add polyline
				startP, endP = linePointsConversion(part.start, part.end, offset, self.resolutionPower)
				cv2.line(self.housingImg, startP, endP, self.wallColor, lineWidth1)
				cv2.line(self.contourImgPlain, startP, endP, self.wallColor, lineWidth2)

			if part.dxftype == 'ARC':
				center = part.center
				radius = part.radius
				if part.end_angle < part.start_angle:
					part.start_angle = part.start_angle - 360

				center, radius = circleConversion(center, radius, offset, self.resolutionPower)
				cv2.ellipse(self.housingImg, center, (radius, radius), 0, part.start_angle, part.end_angle, self.wallColor, lineWidth1)
				cv2.ellipse(self.contourImgPlain, center, (radius, radius), 0, part.start_angle, part.end_angle, self.wallColor, lineWidth2)

			if part.dxftype == 'CIRCLE':
				center = part.center
				radius = part.radius
				center, radius = circleConversion(center, radius, offset, self.resolutionPower)
				cv2.circle(self.housingImg, center, radius, self.wallColor, lineWidth1)
				cv2.circle(self.contourImgPlain, center, radius, self.wallColor, lineWidth2)

	def inBounds(self, point):
		(x, y) = point
		return 0 <= x < self.arrayXlen and 0 <= y < self.arrayYlen

	def passable(self, point):
		return self.housingImg[point[1], point[0]] != self.wallColor

	# 4 ways
	def getNeighbors(self, point):
		(x, y) = point
		neighbors = [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]
		costDict = {point: 1 for point in neighbors}
		# if (x + y) % 2 == 0: neighbors.reverse() # aesthetics
		neighbors = filter(self.inBounds, neighbors)
		neighbors = filter(self.passable, neighbors)


		return neighbors, costDict

	# 8 ways
	def getNeighbors1(self, point):
		(x, y) = point
		D1 = 1
		D2 = math.sqrt(2)
		costDict = {(x+1, y): D1, (x+1, y-1): D2, (x, y-1):D1, (x-1, y-1): D2, (x-1, y): D1, (x-1, y+1): D2,(x, y+1): D1, (x+1, y+1): D2}
		# neighbors = [(x+1, y), (x+1, y-1) (x, y-1), (x-1, y-1), (x-1, y), (x-1, y+1),(x, y+1), (x+1, y+1)]
		neighbors = costDict.keys()
		# if (x + y) % 2 == 0: neighbors.reverse() # aesthetics
		neighbors = filter(self.inBounds, neighbors)
		neighbors = filter(self.passable, neighbors)
		
		return neighbors, costDict

	def getImageArray(self):
		return self.housingImg

	def getContourArray(self):
		return self.contourImgPlain

	def findFirstPoint(self):
		# Find smallest x in a fixed y
		for yIndex in range(0, self.arrayYlen):
			for xIndex in range(0, self.arrayXlen ):
				if not self.passable((xIndex, yIndex)):
					return (xIndex, yIndex)

	def getAndDrawContours(self):
		# [Next, Previous, First_Child, Parent]
		# approxMethod = cv2.CHAIN_APPROX_SIMPLE
		# approxMethod = cv2.CHAIN_APPROX_TC89_L1
		# mode = cv2.RETR_TREE
		mode = cv2.RETR_CCOMP
		approxMethod = cv2.CHAIN_APPROX_TC89_KCOS
		_, contours, hierarchy = cv2.findContours(self.contourImg, mode, approxMethod)
		# print('number of contours:', len(contours))
		parentIndex = 3
		outerMostContour = max(contours, key = cv2.contourArea)
		hierarchy = hierarchy[0]

		for index in range(0, len(contours)):
			# index = 0
			contour = contours[index]
			numOfvertice = len(contour)

			if hierarchy[index][parentIndex] == -1 and numOfvertice > 2 and not contour is outerMostContour:
				if numOfvertice > 150:
					percentage = 0.006
				elif numOfvertice < 60:
					percentage = 0.03
				else:
					percentage = 0.009
				epsilon = percentage*cv2.arcLength(contour, True)
				approxPoints = cv2.approxPolyDP(contour, epsilon,True)
				approxPointsFlaten = approxPoints.ravel().reshape((len(approxPoints),2))
				numOfApproxPoints = len(approxPoints)
				# print('index/number of points berfore/after:', index, numOfvertice, numOfApproxPoints)

				if numOfApproxPoints > 14 and numOfApproxPoints< 18: ### 15? 17? 16!
					p = np.zeros(2, np.uint8)
					for point in approxPointsFlaten:
						p = p + point
					(cX, cY), radius = cv2.minEnclosingCircle(contour)
					cX, cY = int(cX), int(cY)
					print(approxPointsFlaten)
					if abs(cX - int(p[0]/numOfApproxPoints)) < 6 and abs(cY - int(p[1]/numOfApproxPoints)) < 6:
						cv2.circle(self.contourImgPlain, (cX,cY), int(radius), 100, 2) ################################### add to a data structure for output
						cv2.circle(self.housingImg, (cX,cY), int(radius), 100, 2)
					else:
						drawPolyline(self.contourImgPlain, approxPointsFlaten, True) ################################### add to a data structure for output
						drawPolyline(self.housingImg, approxPointsFlaten, True)
				else:
					drawPolyline(self.contourImgPlain, approxPointsFlaten, True) ################################### add to a data structure for output
					drawPolyline(self.housingImg, approxPointsFlaten, True)

				# if len(approxPointsFlaten) <13 and len(approxPointsFlaten)> 7: ?????????????????????????????????/
				# 	x,y,w,h = cv2.boundingRect(contour) #### WORKs IF APPROXpOINTSfLATEN is between 7 and 13
				# 	print(x,y,w,h)
				# 	cv2.rectangle(self.contourImgPlain,(x,y),(x+w,y+h),100,2)
			# break

		# print(approxPointsFlaten)

	def getMaxAndMinXY(self):
		entities = self.dxfObject.entities
		xMax, xMin, yMax, yMin = 0, 0, 0, 0
		for partIndex in range(0, len(entities)):
			part = entities[partIndex]
			if part.dxftype == 'LINE':
				x1, y1 = part.start[0], part.start[1]
				x2, y2 = part.end[0], part.end[1]
				if partIndex == 0:
					xMax, yMax = max(x1, x2), max(y1, y2)
					xMin, yMin= min(x1, x2), min(y1, y2)
				else:
					xMax, yMax = max(xMax, x1, x2), max(yMax, y1, y2)
					xMin, yMin= min(xMin, x1, x2), min(yMin, y1, y2)
			elif part.dxftype == 'ARC' or part.dxftype == 'CIRCLE':
				cx, cy, R = part.center[0], part.center[1], part.radius
				xRight, yUp = cx + R, cy + R
				xLeft, yDown = cx - R, cy - R
				if partIndex == 0:
					xMax, yMax = xRight, yUp
					xMin, yMin = xLeft, yDown
				else:
					xMax, yMax = max(xMax, xRight), max(yMax, yUp)
					xMin, yMin= min(xMin, xLeft), min(yMin, yDown)

		xOffset, yOffset = 0, 0
		if xMin <= 0:
			xOffset = int(-(xMin)) + 2
		elif xMin > 5:
			xOffset = 5 - xMin 
		if yMin <= 0:
			yOffset = int(-(yMin)) + 2
		elif yMin > 5:
			yOffset = 5 - yMin 
		self.XYmin = (xMin, yMin)
		self.XYoffset = (xOffset, yOffset)
		self.housingMaxXInMM = int(xMax - xMin) + 3
		self.housingMaxYInMM = int(yMax - yMin) + 3
		print(self.XYmin, self.XYoffset)

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
	cv2.imwrite(saveImg, flippedImage)
	# cv2.namedWindow('window', cv2.WINDOW_KEEPRATIO)
	# cv2.imshow('window', flippedImage)
	# cv2.waitKey(0)

def covertToNpArrayPoint(points):

	return np.array(points)

def drawPolyline(pixelArray, points, ifEnclosed):

	cv2.polylines(pixelArray, [points], ifEnclosed, 100, 2)



if __name__ == "__main__":
	f = r"C:\Users\eltoshon\Desktop\drawings\housing\housing.dxf"
	saveImgc = r"C:\Users\eltoshon\Desktop\drawings\housing\housingContour.jpeg"
	saveImg = r"C:\Users\eltoshon\Desktop\drawings\housing\housing.jpeg"


	# m = pixelMap(dxf)
	# img = m.getImageArray()
	# showImage(m.getImageArray(), saved)

	# saveImg = r"C:\Users\eltoshon\Desktop\drawings\housingHalf\housingHalf.jpeg"
	# saveImgc = r"C:\Users\eltoshon\Desktop\drawings\housingHalf\housingHalfContour.jpeg"

	# f = r"C:\Users\eltoshon\Desktop\drawings\housingHalf\housingHalf.dxf"
	m = pixelMap(f)
	img = m.getImageArray()
	imgC = m.getContourArray()
	m.getAndDrawContours()

	showImage(imgC, saveImgc)
	showImage(img, saveImg)