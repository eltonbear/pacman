import imageMap
import util

def aStarSearch(pixelArray, p0, p1):
	frontier = util.PriorityQueue()
	frontier.push(p0 , 0)
	cameFrom = {p0: None}
	costSoFar = {p0: 0}
    
	while not frontier.empty():
		current = frontier.get()
        
		if current == goal:
			break
        
		for next in graph.neighbors(current):
			new_cost = cost_so_far[current] + graph.cost(current, next)
			if next not in cost_so_far or new_cost < cost_so_far[next]:
				cost_so_far[next] = new_cost
				priority = new_cost + heuristic(goal, next)
				frontier.put(next, priority)
				came_from[next] = current
    
	return came_from, cost_so_far





def heuristic(p1, p2):
	return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
















if __name__ == "__main__":
	img, firstPoint = imageMap.createMap(r"C:\Users\eltoshon\Desktop\drawings\housingPathFindTest\housingPathFindTest.dxf")
	imageMap.showImage(img,  r"C:\Users\eltoshon\Desktop\drawings\housingPathFindTest\housingPathFindTest.jpeg")
	# aStarSearch()
