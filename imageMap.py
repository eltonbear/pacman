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
		self.xBoundary = 0
		self.yBoundary = 0
		self.XYoffset = (0, 0)
		self.contours = []

		self.getMaxAndMinXY()

		self.arrayXlen = (int(self.xBoundary[1]-self.xBoundary[0]) + 3 )* 10 ** self.resolutionPower 
		self.arrayYlen = (int(self.yBoundary[1]-self.yBoundary[0]) + 3 )* 10 ** self.resolutionPower 

		self.housingFatImg = np.zeros((self.arrayYlen, self.arrayXlen), np.uint8) #### might use his for filter
		self.contourImgPlain = np.copy(self.housingFatImg)
		self.drawPartsFromDxf(93, 2)
		
	def drawPartsFromDxf(self, lineWidth1, lineWidth2):
		# line width = 1 --> 1 pixel
		# line width = 94-100 --> 50 pixel # 93 for now
		entities = self.dxfObject.entities
		offset = self.XYoffset
		for part in entities:
			if part.dxftype == 'LINE':  # maybe need to add polyline
				startP, endP = linePointsToGridConversion(part.start, part.end, offset, self.resolutionPower)
				cv2.line(self.housingFatImg, startP, endP, self.wallColor, lineWidth1)
				cv2.line(self.contourImgPlain, startP, endP, self.wallColor, lineWidth2)

			if part.dxftype == 'ARC':
				center = part.center
				radius = part.radius
				if part.end_angle < part.start_angle:
					part.start_angle = part.start_angle - 360

				center, radius = circlePointToGridConversion(center, radius, offset, self.resolutionPower)
				cv2.ellipse(self.housingFatImg, center, (radius, radius), 0, part.start_angle, part.end_angle, self.wallColor, lineWidth1)
				cv2.ellipse(self.contourImgPlain, center, (radius, radius), 0, part.start_angle, part.end_angle, self.wallColor, lineWidth2)

			if part.dxftype == 'CIRCLE':
				center = part.center
				radius = part.radius
				center, radius = circlePointToGridConversion(center, radius, offset, self.resolutionPower)
				cv2.circle(self.housingFatImg, center, radius, self.wallColor, lineWidth1)
				cv2.circle(self.contourImgPlain, center, radius, self.wallColor, lineWidth2)

	def inBounds(self, point):
		(x, y) = point
		return 0 <= x < self.arrayXlen and 0 <= y < self.arrayYlen

	def passable(self, point):#?????????????
		return self.housingFatImg[point[1], point[0]] != self.wallColor

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

	def getImageArray(self): #####??????????????????
		return self.housingFatImg

	def getDispensedImage(self):
		return self.contourImgPlain

	def getContours(self):
		return self.contours

	def getArrayDimension(self):
		return (self.arrayXlen, self.arrayYlen)

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
		housingFatImgForContourFinding = np.copy(self.housingFatImg)
		housingFatImgForContourFinding = cv2.bilateralFilter(housingFatImgForContourFinding, 9, 80, 80)
		_, cv2Contours, hierarchy = cv2.findContours(housingFatImgForContourFinding, mode, approxMethod)
		# print('number of contours:', len(cv2Contours))
		parentIndex = 3
		outerMostContour = max(cv2Contours, key = cv2.contourArea)
		hierarchy = hierarchy[0]

		for index in range(0, len(cv2Contours)):
			# index = 0
			contour = cv2Contours[index]
			numOfvertice = len(contour)

			if hierarchy[index][parentIndex] == -1 and numOfvertice > 2 and not contour is outerMostContour:
				if numOfvertice > 150:
					percentage = 0.006
				elif numOfvertice < 60:
					percentage = 0.03
				else:
					percentage = 0.009
				epsilon = percentage*cv2.arcLength(contour, True)
				approxPoints = cv2.approxPolyDP(contour, epsilon, True)
				approxPointsFlaten = approxPoints.ravel().reshape((len(approxPoints),2))
				numOfApproxPoints = len(approxPoints)
				# print('index/number of points berfore/after:', index, numOfvertice, numOfApproxPoints)

				if numOfApproxPoints > 14 and numOfApproxPoints< 18: ### 15? 17? 16!
					p = np.zeros(2, np.uint8)
					for point in approxPointsFlaten:
						p = p + point
					(cX, cY), radius = cv2.minEnclosingCircle(contour)
					cX, cY, radius= int(cX), int(cY), int(radius)
					if abs(cX - int(p[0]/numOfApproxPoints)) < 6 and abs(cY - int(p[1]/numOfApproxPoints)) < 6:
						center = (cX, cY)
						cv2.circle(self.contourImgPlain, center, radius, 100, 2)
						cv2.circle(self.housingFatImg, center, radius, 100, 2) # might not needed
						realCenter, realRadius = circleGridToPointConversion(center, radius, self.XYoffset, self.resolutionPower)
						self.contours.append({'Shape': 'CIRCLE', 'Center': realCenter, 'Radius': realRadius, 'StartEndGridPoint': (cX + radius, cY)})
						# 'DispenseVelocity': 0.5, 'Angle': math.pi*2*.98
					else:
						drawPolyline(self.contourImgPlain, approxPointsFlaten, True, 100, 2)
						drawPolyline(self.housingFatImg, approxPointsFlaten, True, 100, 2) # might not needed
						self.contours.append({'Shape': 'POLYLINE', 'LINES': polyPointsToLines(approxPointsFlaten, self.XYoffset, self.resolutionPower), 'StartEndGridPoint': (approxPointsFlaten[0][0],approxPointsFlaten[0][1])})
				else:
					drawPolyline(self.contourImgPlain, approxPointsFlaten, True, 100, 2)
					drawPolyline(self.housingFatImg, approxPointsFlaten, True, 100, 2) # might not needed
					self.contours.append({'Shape': 'POLYLINE', 'LINES': polyPointsToLines(approxPointsFlaten, self.XYoffset, self.resolutionPower), 'StartEndGridPoint': (approxPointsFlaten[0][0],approxPointsFlaten[0][1])})

				# if len(approxPointsFlaten) <13 and len(approxPointsFlaten)> 7: ?????????????????????????????????/
				# 	x,y,w,h = cv2.boundingRect(contour) #### WORKs IF APPROXpOINTSfLATEN is between 7 and 13
				# 	print(x,y,w,h)
				# 	cv2.rectangle(self.contourImgPlain,(x,y),(x+w,y+h),100,2)
			# break

		# print(self.contours)

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
			elif part.dxftype == 'CIRCLE':
				cx, cy, R = part.center[0], part.center[1], part.radius
				xRight, yUp = cx + R, cy + R
				xLeft, yDown = cx - R, cy - R
				if partIndex == 0:
					xMax, yMax = xRight, yUp
					xMin, yMin = xLeft, yDown
				else:
					xMax, yMax = max(xMax, xRight), max(yMax, yUp)
					xMin, yMin= min(xMin, xLeft), min(yMin, yDown)
			elif part.dxftype == 'ARC':
				cx, cy, R = part.center[0], part.center[1], part.radius
				f = part.start_angle
				g = part.end_angle
				if part.end_angle < part.start_angle:
					part.start_angle = part.start_angle - 360

				angles =  np.linspace(part.start_angle, part.end_angle, 7)
				x = [R*math.cos(math.radians(a)) + cx for a in angles]
				y = [R*math.sin(math.radians(a)) + cy for a in angles]

				if partIndex == 0:
					xMax, yMax = max(x), max(y)
					xMin, yMin = min(x), min(y)
				else:
					xMax, yMax = max(xMax, max(x)), max(yMax, max(y))
					xMin, yMin= min(xMin, min(x)), min(yMin, min(y))

		xOffset, yOffset = 0, 0
		if xMin <= 0:
			xOffset = int(-(xMin)) + 2
		elif xMin > 5:
			xOffset = 5 - xMin 
		if yMin <= 0:
			yOffset = int(-(yMin)) + 2
		elif yMin > 5:
			yOffset = 5 - yMin 

		self.XYoffset = (xOffset, yOffset)
		self.xBoundary = (xMin, xMax)
		self.yBoundary = (yMin, yMax)

def circlePointToGridConversion(center, radius, offset, resolution):
	cX, cY = (center[0] + offset[0]) * 10**resolution, (center[1] + offset[1]) * 10**resolution
	xInt, xReminder = int(cX), cX*10%10
	yInt, yReminder = int(cY), cY*10%10
	x = xInt + 1 if xReminder >= 5 else xInt
	y = yInt + 1 if yReminder >= 5 else yInt
	center = (x, y)
	radius = radius * 10**(resolution)
	if radius.is_integer():
		radius = int(radius)
	else:
		radius = int(radius) + 1
	return center, radius

def circleGridToPointConversion(center, radius, offset, resolution):
	center = ((center[0]/10**resolution - offset[0]), center[1]/10**resolution - offset[1])
	radius = radius/10**resolution

	return center, radius

def linePointsToGridConversion(sPoint, ePoint, offset, resolution):
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

def polyPointsToLines(polyPoints, offset, resolution):
	lines = []
	numPoints = len(polyPoints)
	firstAndEndPoint = gridPointToRealPoint(polyPoints[0], offset, resolution)
	for index in range(0, len(polyPoints)):
		if index == numPoints - 1:
			realPoint = gridPointToRealPoint(polyPoints[index],  offset, resolution)
			length, angle = getLineLengthAngle(realPoint, firstAndEndPoint)
			lines.append({'Point': realPoint, 'Length': length, 'Angle': angle})
		else:
			realPoint1 = gridPointToRealPoint(polyPoints[index],  offset, resolution)
			realPoint2 = gridPointToRealPoint(polyPoints[index + 1],  offset, resolution)
			length, angle = getLineLengthAngle(realPoint1, realPoint2)
			lines.append({'Point': realPoint1, 'Length': length, 'Angle': angle})

	return lines

def gridPointToRealPoint(point, offset, resolution):
	return (point[0]/10**resolution - offset[0], point[1]/10**resolution - offset[1])

def getLineLengthAngle(p1, p2):
	deltaY = p2[1] - p1[1]
	deltaX = p2[0] - p1[0]
	length = math.sqrt(deltaX**2 + deltaY**2)
	angle = math.atan2(deltaY, deltaX) # in radian ???? POSITIVE OR NEGATIVE

	return length, angle

def gridPointToRealPoint(point, offset, resolution):
	x = point[0]/10**resolution - offset[0]
	y = point[1]/10**resolution - offset[1]

	return (x, y)

def sortContour(contours, arrayYlength):
	sortedContours = []
	numOfLists = 6
	numOfBoundaries = numOfLists + 1
	contourLists = [[] for count in range(0, numOfLists)]
	boundary = np.linspace(arrayYlength, 0, numOfBoundaries)
	print(boundary)
	for contour in contours:
		y = contour['StartEndGridPoint'][1]
		for boundaryIndex in range(1, numOfBoundaries):
			if y >= boundary[boundaryIndex] and y < boundary[boundaryIndex-1]:
				# print(y, boundary[boundaryIndex])
				listIndex = boundaryIndex - 1
				contourLists[listIndex].append(contour)

	for contourList in contourLists:
		num = len(contourList)
		if not sortedContours:
			sortedContours = contourList
		else:
			if num == 1:
				sortedContours = sortedContours + contourList
			elif num > 1:
				sortedSubContourList = sorted(contourList, key=lambda contour: contour['StartEndGridPoint'][0])
				xPrev = sortedContours[-1]['StartEndGridPoint'][0]
				xFirst = sortedSubContourList[0]['StartEndGridPoint'][0] # samller x
				xLast = sortedSubContourList[-1]['StartEndGridPoint'][0] # larger x
				if abs(xFirst - xPrev) <= abs(xLast - xPrev):
					sortedContours = sortedContours + sortedSubContourList
				else:
					sortedSubContourList.reverse()
					sortedContours = sortedContours + sortedSubContourList		
					
	return sortedContours	


def showImage(pixelArray, saveImg):
	flippedImage = cv2.flip(pixelArray, 0)
	cv2.imwrite(saveImg, flippedImage)
	# cv2.namedWindow('window', cv2.WINDOW_KEEPRATIO)
	# cv2.imshow('window', flippedImage)
	# cv2.waitKey(0)

def covertToNpArrayPoint(points):

	return np.array(points)

def drawPolyline(pixelArray, points, ifEnclosed, color, width):

	cv2.polylines(pixelArray, [points], ifEnclosed, color, width)


# if __name__ == "__main__":
# 	# f = r"C:\Users\eltoshon\Desktop\drawings\housing\hsg_top_notched.dxf"
# 	# saveImgc = r"C:\Users\eltoshon\Desktop\drawings\housing\hsg_top_notchedCon.jpeg"
# 	f = r"C:\Users\eltoshon\Desktop\drawings\housing\housing.dxf"
# 	saveImgc = r"C:\Users\eltoshon\Desktop\drawings\housing\housingContour.jpeg"


# 	m = pixelMap(f)
# 	# img = m.getImageArray()
# 	imgC = m.getDispensedImage()
# 	m.getAndDrawContours()
# 	contours = m.getContours()
# 	_, yLen = m.getArrayDimension()
# 	print('y:',  yLen)
# 	# print(contours)
# 	sortContour(contours, yLen)

# 	showImage(imgC, saveImgc)
# 	# showImage(img, saveImg)