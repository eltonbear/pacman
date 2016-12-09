import time
import link
import imageMap
import cv2


if __name__ == "__main__":
	start_time = time.time()
	# f = r"C:\Users\eltoshon\Desktop\drawings\housing\hsg_top_notched.dxf"
	# saveImg = r"C:\Users\eltoshon\Desktop\drawings\housing\hsg_top_notched.jpeg"
	# saveImgc = r"C:\Users\eltoshon\Desktop\drawings\housing\hsg_top_notched_contour.jpeg"
	f = r"C:\Users\eltoshon\Desktop\drawings\housing\housing.dxf"
	saveImg = r"C:\Users\eltoshon\Desktop\drawings\housing\housing.jpeg"
	saveImgc = r"C:\Users\eltoshon\Desktop\drawings\housing\housingContour.jpeg"
	m = imageMap.pixelMap(f)
	img = m.getCalculationImage()
	imgC = m.getDispensedImage()
	m.getAndDrawContours('u')
	xLen, yLen = m.getArrayDimension()
	# print((xLen, yLen))
	# print(yLen/2, xLen/2)
	c = m.getContours()
	contours = imageMap.sortContour(c, yLen) 
	# linkContoursTest(contours, m)
	# output = link.linkContours(contours, m)
	# i = cv2.resize(img, (0,0), None, fx=.01, fy=.01, interpolation = cv2.INTER_AREA)

	# imageMap.showImage(i, r"C:\Users\eltoshon\Desktop\drawings\housing\hsg_top_notched_contour_resizedA.jpeg")
	# print((xLen, yLen), i.shape)
	imageMap.showImage(img, saveImg)
	imageMap.showImage(imgC, saveImgc)

	end_time = time.time()
	print(end_time- start_time)