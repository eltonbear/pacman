import cv2
import numpy as np
import dxfgrabber
import math
import imageMap
import util

# http://www.adammil.net/blog/v126_A_More_Efficient_Flood_Fill.html
# http://will.thimbleby.net/scanline-flood-fill/

def scanFill(image, x, y)
	if test(image[y][x]):
		return
	else:
		iamge[y][x] = true

	xLen, yLen = image.getArrayDimension()
	stack = util.stack()
	stack.push(lineRange(x, x+1, y, 0, True, True))

	while not stack.isEmpty():
		lineSeg = stack.pop()
		startX, endX = lineSeg.startX, lineSeg.endX
		yValue = lineSeg.y
		direction = lineSeg.direction
		if lineSeg.scanLeft:
			while startX > 0 and test(image[y][startX-1]):
				startX -= 1
				image[y][startX] = True
		if lineSeg.scanRight:
			while endX < xLen and test(image[y][endX]):
				image[y][endX] = True
				endX += 1

		lineSeg.startX = lineSeg.startX - 1
		lineSeg.endX = lineSeg.endX + 1

		if yValue > 0:
			addLine(image, stack, startX, endX, yValue-1, lineSeg.startX, lineSeg.EndX, -1, direction <= 0)
		if yValue < yLen - 1:
		 	addLine(image, stack, startX, endX, yValue+1, lineSeg.startX, lineSeg.EndX, 1, direction >= 0)

def addLine():




class lineRange:

	def __init__(self, startX, endX, y, direction, scanLeft, scanRight):
		self.startX    = startX
	    self.endX      = endX
	    self.y         = y
	    self.direction = direction ### -1:above the previous segment, 1:below the previous segment, 0:no previous segment
	    self.scanLeft  = scanLeft
	    self.scanRight = scanRight
################

public static void ScanlineFill(bool[,] array, int x, int y)
{
  if(test(array[y, x])) return;
  array[y, x] = true;

  int height = array.GetLength(0), width = array.GetLength(1);
  Stack<Segment> stack = new Stack<Segment>();
  stack.Push(new Segment(x, x+1, y, 0, true, true));
  do
  {
    Segment r = stack.Pop();
    int startX = r.StartX, endX = r.EndX;
    if(r.ScanLeft) // if we should extend the segment towards the left...
    {
      while(startX > 0 && !test(array[r.Y, startX-1])) array[r.Y, --startX] = true; // do so, and fill cells as we go
    }
    if(r.ScanRight)
    {
      while(endX < width && !test(array[r.Y, endX])) array[r.Y, endX++] = true;
    }
    // at this point, the segment from startX (inclusive) to endX (exclusive) is filled. compute the region to ignore
    r.StartX--; // since the segment is bounded on either side by filled cells or array edges, we can extend the size of
    r.EndX++;   // the region that we're going to ignore in the adjacent lines by one
    // scan above and below the segment and add any new segments we find
    if(r.Y > 0) AddLine(array, stack, startX, endX, r.Y-1, r.StartX, r.EndX, -1, r.Dir <= 0);
    if(r.Y < height-1) AddLine(array, stack, startX, endX, r.Y+1, r.StartX, r.EndX, 1, r.Dir >= 0);
  } while(stack.Count != 0);
}

static void AddLine(bool[,] array, Stack<Segment> stack, int startX, int endX, int y,
                    int ignoreStart, int ignoreEnd, sbyte dir, bool isNextInDir)
{
  int regionStart = -1, x;
  for(x=startX; x<endX; x++) // scan the width of the parent segment
  {
    if((isNextInDir || x < ignoreStart || x >= ignoreEnd) && !test(array[y, x])) // if we're outside the region we
    {                                                                            // should ignore and the cell is clear
      array[y, x] = true; // fill the cell
      if(regionStart < 0) regionStart = x; // and start a new segment if we haven't already
    }
    else if(regionStart >= 0) // otherwise, if we shouldn't fill this cell and we have a current segment...
    {
      stack.Push(new Segment(regionStart, x, y, dir, regionStart == startX, false)); // push the segment
      regionStart = -1; // and end it
    }
    if(!isNextInDir && x < ignoreEnd && x >= ignoreStart) x = ignoreEnd-1; // skip over the ignored region
  }
  if(regionStart >= 0) stack.Push(new Segment(regionStart, x, y, dir, regionStart == startX, true));
} The second scanline varia

if __name__ == "__main__":
	f = r"C:\Users\eltoshon\Desktop\drawings\housing\testttt.jpeg"
	x = np.zeros((20, 20), np.uint8)
	cv2.circle(x, (5,5), 0, 255, 1)
	imageMap.showImage(x, f)