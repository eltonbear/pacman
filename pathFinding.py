import imageMap
import util

def aStarSearch(imageMapObject, startP, endP):
	frontier = util.PriorityQueue()
	frontier.push(startP , 0)
	cameFrom = {startP: None}
	costSoFar = {startP: 0}
    
	while not frontier.isEmpty():
		currentPoint= frontier.pop()
        
		if currentPoint == endP:
			break
		neighbors, neighborCosts = imageMapObject.getNeighbors(currentPoint)
		for nextpoint in neighbors:
			newGCost = costSoFar[currentPoint] + neighborCosts[nextpoint]
			if nextpoint not in costSoFar or newGCost < costSoFar[nextpoint]:
				costSoFar[nextpoint] = newGCost
				priority = newGCost + heuristic(endP, nextpoint)
				frontier.push(nextpoint, priority)
				cameFrom[nextpoint] = currentPoint
    
	return cameFrom , costSoFar

# Manhattan distance for only horizontal and vertical movements
def heuristic(p1, p2):
	return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

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
	dxf = r"C:\Users\eltoshon\Desktop\drawings\housingPathFindTest\housingPathFindTest.dxf"
	save = r"C:\Users\eltoshon\Desktop\drawings\housingPathFindTest\housingPathFindTest.jpeg"
	housing = imageMap.pixelMap(dxf)
	housingPixelArray = housing.getPixelArray()
	comesFrom, costSoFar = aStarSearch(housing, (900, 500), (1500, 1200))
	path = reconstructPath(comesFrom, (900, 500), (1500, 1200))
	points = imageMap.covertToNpArrayPoint(path)
	# print(comesFrom)
	imageMap.drawPolyline(housingPixelArray, points)
	imageMap.showImage(housingPixelArray, save)


