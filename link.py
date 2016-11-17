import cv2
import time
import imageMap
import pathFinding

def linkContours(contours, imageMapObject):
	dispenseSeq = []
	calculationImage = imageMapObject.getCalculationImage()
	presentationImage = imageMapObject.getDispensedImage()
	offset = imageMapObject.getOffset()
	resolution = imageMapObject.getResolutionPower()
	for index in range(0, len(contours)):
		dispenseSeq.append(contours[index])
		if index == 0:
			p = contours[index]['StartEndGridPoint']
		else:
			pNext = contours[index]['StartEndGridPoint']
			comesFrom, costSoFar = pathFinding.aStarSearch(imageMapObject, p, pNext)
			path = pathFinding.reconstructPath(comesFrom, p, pNext)
			points = imageMap.covertToNpArrayPoint(path)
			epsilon = 0.005*cv2.arcLength(points, True)
			approxPoints = cv2.approxPolyDP(points, epsilon, True)
			# mark dots
			imageMap.drawPolyDots(calculationImage, approxPoints, 200)
			dispenseSeq.append({'Shape':'POLYDOTS', 'Points': [imageMap.gridPointToRealPoint(point[0], offset, resolution) for point in approxPoints]})
			# Show paths on an output image
			imageMap.drawPolyline(presentationImage, approxPoints, False, 200, 1)

			p = pNext

	return dispenseSeq

def linkContoursTest(contours, imageMapObject):
	dispenseSeq = []
	calculationImage = imageMapObject.getCalculationImage()
	presentationImage = imageMapObject.getDispensedImage()
	offset = imageMapObject.getOffset()
	resolution = imageMapObject.getResolutionPower()
	stop = 1
	for index in range(stop-1, len(contours)):
		dispenseSeq.append(contours[index])
		if index == stop -1:
			p = contours[index]['StartEndGridPoint']
		else:
			pNext = contours[index]['StartEndGridPoint']
			comesFrom, costSoFar = pathFinding.aStarSearch(imageMapObject, p, pNext)
			path = pathFinding.reconstructPath(comesFrom, p, pNext)
			points = imageMap.covertToNpArrayPoint(path)
			epsilon = 0.005*cv2.arcLength(points, True)
			approxPoints = cv2.approxPolyDP(points, epsilon, True)
			dispenseSeq.append({'Shape':'POLYDOTS', 'Points': [imageMap.gridPointToRealPoint(point[0], offset, resolution) for point in approxPoints]})
			p = pNext

		if index > stop -1:
			# mark dots
			imageMap.drawPolyDots(calculationImage, approxPoints, 200)
			# Only draw the last path
			imageMap.drawPolyline(presentationImage, approxPoints, False, 200, 1)

		if index == stop:
			print(approxPoints)
			print(dispenseSeq[-1])
			print(len(approxPoints))
			break

# if __name__ == "__main__":
# 	start_time = time.time()

# 	f = r"C:\Users\eltoshon\Desktop\drawings\housing\housing.dxf"
# 	saveImg = r"C:\Users\eltoshon\Desktop\drawings\housing\housing.jpeg"
# 	saveImgc = r"C:\Users\eltoshon\Desktop\drawings\housing\housingContour.jpeg"
# 	m = imageMap.pixelMap(f)
# 	img = m.getCalculationImage()
# 	imgC = m.getDispensedImage()
# 	m.getAndDrawContours()
# 	_, yLen = m.getArrayDimension()
# 	c = m.getContours()
# 	contours = imageMap.sortContour(c, yLen) 
# 	# linkContoursTest(contours, m)
# 	output = linkContours(contours, m)

# 	imageMap.showImage(img, saveImg)
# 	imageMap.showImage(imgC, saveImgc)

# 	end_time = time.time()
# 	print(end_time- start_time)