import time
import link
import imageMap


if __name__ == "__main__":
	start_time = time.time()

	f = r"C:\Users\eltoshon\Desktop\drawings\housing\housing.dxf"
	saveImg = r"C:\Users\eltoshon\Desktop\drawings\housing\housing.jpeg"
	saveImgc = r"C:\Users\eltoshon\Desktop\drawings\housing\housingContour.jpeg"
	m = imageMap.pixelMap(f)
	img = m.getCalculationImage()
	imgC = m.getDispensedImage()
	m.getAndDrawContours()
	_, yLen = m.getArrayDimension()
	c = m.getContours()
	contours = imageMap.sortContour(c, yLen) 
	# linkContoursTest(contours, m)
	output = link.linkContours(contours, m)

	imageMap.showImage(img, saveImg)
	imageMap.showImage(imgC, saveImgc)

	end_time = time.time()
	print(end_time- start_time)