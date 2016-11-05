import imageMap
import util
import time

def aStarSearch(imageMapObject, startP, endP):
	frontier = util.PriorityQueue()
	frontier.push(startP , 0)
	cameFrom = {startP: None}
	costSoFar = {startP: 0}
    
	while not frontier.isEmpty():
		currentPoint= frontier.pop()
        
		if currentPoint == endP:
			break
		neighbors, neighborCosts = imageMapObject.getNeighbors1(currentPoint)
		for nextpoint in neighbors:
			newGCost = costSoFar[currentPoint] + neighborCosts[nextpoint]
			if nextpoint not in costSoFar or newGCost < costSoFar[nextpoint]:
				costSoFar[nextpoint] = newGCost
				priority = newGCost + heuristicM(endP, nextpoint)
				frontier.push(nextpoint, priority)
				cameFrom[nextpoint] = currentPoint
    
	return cameFrom , costSoFar

# Manhattan distance for only horizontal and vertical movements
def heuristicM(p1, p2):
	D = 1
	return D*(abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]))

def heuristicD(p1, p2):
    dx = abs(p1[0] - p2[0])
    dy = abs(p1[1] - p2[1])
    D1, D2 = 1, math.sqrt(2)
    return D1 * (dx + dy) + (D2 - 2 * D1) * min(dx, dy)

def reconstructPath(cameFrom, startP, goalP):
    current = goalP
    path = [current]
    while current != startP:
        current = cameFrom[current]
        path.append(current)
    path.append(startP) # optional
    path.reverse() # optional
    return path


if __name__ == "__main__":
	start_time = time.time()

	dxf = r"C:\Users\eltoshon\Desktop\drawings\housingPathFindTest\housingPathFindTest10.dxf"
	save = r"C:\Users\eltoshon\Desktop\drawings\housingPathFindTest\housingPathFindTest10.jpeg"
	housing = imageMap.pixelMap(dxf)
	housingPixelArray = housing.getPixelArray()
	startPoint = (600, 5000)
	endPoint = (3700, 2600)
	comesFrom, costSoFar = aStarSearch(housing, startPoint, endPoint)
	path = reconstructPath(comesFrom, startPoint, endPoint)
	# print(path)
	# print(len(path))
	points = imageMap.covertToNpArrayPoint(path)
	# print(comesFrom)
	imageMap.drawPolyline(housingPixelArray, points)
	imageMap.showImage(housingPixelArray, save)
	end_time = time.time()
	print(end_time- start_time)


