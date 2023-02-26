try:        # importing own classes and libraries
    from hashingObjects import *
    from argparse import ArgumentParser, Namespace
except ImportError:
    raise SystemExit('Error while importing.')

def parse() -> Namespace:
    """Assigns programme parameters into argparse.Namespace–type variable, they may be entered in any order,
    if some aren´t entered, programme searches value of "default" variable in its folder."""
    parser = ArgumentParser()
    parser.add_argument('-p', action = 'store', nargs = '?', default = 'body.txt', dest = 'points')        # argument -p <fileName> for input points file
    parser.add_argument('-op', action = 'store', nargs = '?', default = 'hashovaneBody.txt', dest = 'outputPoints')     # argument -op <fileName> for output points file  
    parser.add_argument('-oh', action = 'store', nargs = '?', default = 'hraniceHashu.txt', dest = 'outputHashes')      # argument -oh <fileName> for output hashes file
    return parser.parse_args()

def control(pointInput : str, pointOutput : str, hashOutput : str) -> None:
    """Checks if file addresses, their format and usage rights are correct."""
    for file in (pointInput, pointOutput, hashOutput):      # files format test
        if '.txt' not in file:
            raise SystemExit(f'File "{file}" isn´t a text file.')
    try:
        with open(pointInput) as p,\
        open(pointOutput, 'w') as po,\
        open(hashOutput, 'w') as ho:        # input files opening     
            try:        # input points file testing
                if not p.readable():
                    raise SystemExit('Input points file isn´t readable.')     
            except Exception as e:      
                raise SystemExit(f'Unexpected error in input points file: {e}.')

            try:        # output points file testing
                if not po.writable():
                    raise SystemExit('Output points file isn´t writable.')    
            except Exception as e:
                raise SystemExit(f'Unexpected error in output points file: {e}.')

            try:        # output hashes file testing
                if not ho.writable():
                    raise SystemExit('Output hashes file isn´t writable.')    
            except Exception as e:
                raise SystemExit(f'Unexpected error in output hashes file: {e}.')
    except FileNotFoundError as e:      # errors while trying to open files
        raise SystemExit(f'Input file doesn´t exist: {e}.')
    except PermissionError as e:
        raise SystemExit(f'Programme isn´t permissioned to work with input file: {e}.')
    except OSError as e:
        raise SystemExit(f'Unexpected error caused by your PC while checking inout files: {e}.')

def rowToPoint(line : str) -> Point:
    """If possible, converts input string to Point object."""
    l2 = line.replace(',', '.').split()     # numbers may be separated by a comma or a dot
    try:
        return Point(float(l2[0]), float(l2[1]))        
    except:     # wrong input string format
        line = line.strip()
        print(f'Line "{line}" can´t be converted to Point object.')

def appendPoint(row : str, pointList : list, xMinimum : float, xMaximum : float, yMinimum : float, yMaximum : float):
    """If conversion succeeds, pushes string converted to Point object into input list and compares its 
    coordinates with highest and lowest recorded coordinates and rewrites them if necessary.\n 
    Returns expanded input list and highest and lowest coordinates in it."""
    # pushing into output list in nested function is inappropriate but the code breaks DRY appropriate less this way
    pnt = rowToPoint(row)
    if pnt != None:     # if conversion to Point succeeds:
        pointList.append(pnt)
        if len(pointList) == 0:     # input list is empty:
            xMinimum = pnt.x
            xMaximum = pnt.x
            yMinimum = pnt.y
            yMaximum = pnt.y
        else:       # input list isn´t empty:
            tmp = pnt.x     # coordinates check and rewrite for x–coordinate
            if tmp < xMinimum:
                xMinimum = tmp
            elif tmp > xMaximum:
                xMaximum = tmp

            tmp = pnt.y     # the same for y–coordinate
            if tmp < yMinimum:
                yMinimum = tmp
            elif tmp > yMaximum:
                yMaximum = tmp
    return pointList, xMinimum, xMaximum, yMinimum, yMaximum

def loadPoints(inputFile : str):
    """Converts input file´s each correct row to Point object.\n
    Returns list of loaded points and and highest and lowest coordinates in it."""
    with open(inputFile, 'r') as f:
        l = f.readline()        # first row in input file, creation of while–cycle´s condition
        points = []     # empty list of points
        minimalX = 0.0; maximalX = 0.0; minimalY = 0.0; maximalY = 0.0      
        points, minimalX, maximalX, minimalY, maximalY = appendPoint(l, points, minimalX, maximalX, minimalY, maximalY)     
        while l:    
            l = f.readline()
            if l.strip() != '':     # processes each not empty row
                points, minimalX, maximalX, minimalY, maximalY = appendPoint(l, points, minimalX, maximalX, minimalY, maximalY)
    if points == []:        # all rows couldn´t be converted to Point
        raise SystemExit('Correct input rows don´t exist.')   
    return points, minimalX, maximalX, minimalY, maximalY

def createHashes(points : list, xMinimum : float, xMaximum : float, yMinimum : float, yMaximum : float):
    """Creates bounding box from highest and lowest coordinates in loaded points, divides it into spatial hashes.\n
    Returns spatial hashes count, number of spatial hashes per bounding box´s edge, list of spatial hashes (Rectangle object) 
    and list of spatial hashes´s borders."""
    bins = []       # variables for creation of spatial hashes: 
    binIndex = 1        # spatial hashes´s index
    borders = ([], [])     # collection for spatial hashes´s borders
            # variables determining spatial hashes´s range:
    xLen = abs(xMaximum - xMinimum)     # bounding box´s width
    yLen = abs(yMaximum - yMinimum)     # bounding box´s height  
    sideDivisions = round(len(points) ** (1/4))        # number of spatial hashes per bounding box´s edge, spatial hashes count = 2nd power of this value
    xInterval = xLen / sideDivisions        # spatial hashes´s width
    yInterval = yLen / sideDivisions        # spatial hashes´s height
        # variables determining current spatial hash´s range:
    bYMin = yMinimum        # spatial hash´s min. y–coordinate
    bYMax = yMinimum + yInterval        # spatial hashes max. y–coordinate
            #  division of the bounding box into individual spatial hashes: 
    for i in range(1, sideDivisions + 1):       # creation of columns
        bXMin = xMinimum        # spatial hash´s min. x–coordinate
        bXMax = xMinimum + xInterval        # spatial hash´s max. x–coordinate
        for j in range(1, sideDivisions + 1):       # creation of rows
            bin = Rectangle(bXMin, bXMax, bYMin, bYMax, binIndex)
                # assigning of spatial hash´s borders into collection for spatial hashes´s borders (makes following work easier than getting the attributes from Rectangle objects):
            for border in (bXMin, bXMax):       # x–coordinate borders
                if border not in borders[0]:
                    borders[0].append(border)
            for border in (bYMin, bYMax):       # y–coordinate borders
                if border not in borders[1]:  
                    borders[1].append(border)

            bins.append(bin)
            binIndex += 1
            bXMin += xInterval      # x–coordinates increasing
            if (binIndex % sideDivisions != 0):     # next spatial hash isn´t the last in the row 
                bXMax += xInterval
            else:       # next spatial hash is the last in the row 
                bXMax = xMaximum        # assigning of value loaded from loaded data instead of value calculated from loaded data can lead to better accuracy
        bYMin += yInterval      # y–coordinates increasing
        if i != (sideDivisions - 1):        # next spatial hash isn´t the last in the column 
            bYMax += yInterval
        else:       # next spatial hash is the last in the column 
            bYMax = yMaximum        
    return sideDivisions, bins, borders

def hashPoints(sideDivisions : int, points : list, bins : list, borders : tuple):
    """Assigns spatial hash to each point in input list.\n
    Returns list of points with assigned spatial hash index and list of spatial hashes assigned with points located in them."""
    for point in points:
        colIndex = 1        # initial spatial hash´s indices
        rowIndex = 1    

        for i in range(len(borders[0]) - 1):        # assigning of column index
            colRange = (borders[0][i], borders[0][i + 1])
            if (colIndex == sideDivisions and point.x >= colRange[0]) or (point.x >= colRange[0] and point.x < colRange[1]):        # sideDivisions for bounding box´s rightmost column
                break
            colIndex += 1

        for i in range(len(borders[1]) - 1):        # assigning of row index
            rowRange = (borders[1][i], borders[1][i + 1])
            if (rowIndex == sideDivisions and point.y >= rowRange[0]) or (point.y >= rowRange[0] and point.y < rowRange[1]):        # sideDivisions for bounding box´s top row
                break
            rowIndex += 1

        binIndex = colIndex + ((rowIndex - 1) * sideDivisions)        # calculation of point´s spatial hash index
        point.hash = binIndex       # assigning of index into the point
        bins[binIndex - 1]._Rectangle__addPoint(point)      # adding the point into spatial hash
    return points, bins

def pointDistance(p1 : Point, p2 : Point) -> float:
    """Returns the distance between two points calculated using Pythagorean Theorem."""
    return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2)**(1/2)

def approximateNearestNeighbor(points : list, bins : list) -> list:
    """If input list of points contains more than one, assigns ID of approximate nearest 
    neighbor to "ANN" attribute. \n Returns the adjusted input list."""
    for point in points:
        currentBin = bins[point.hash - 1]
        if currentBin._Rectangle__pointCount() > 1:     # if spatial hash contains more points
            minDistance = (-1, -1)
            for pnt in currentBin.points:
                dist = pointDistance(point, pnt)
                recordedDist = minDistance[0]
                if point.ID != pnt.ID and (recordedDist == -1 or dist < recordedDist):      # if distance to a point wasn´t assigned or current distance is shorter
                    minDistance = (dist, pnt.ID)
            if minDistance[0] > -1:     # if a change occured
                point.ANN = minDistance[1]

        else:       # nearest neighbor approximation out of closest spatial hashes
            nearestBins = []
            for bin in bins:        # nearest neighbor search outside point´s spatial hash for hashes containing points       
                if bin._Rectangle__pointCount() > 0:      
                    dist = pointDistance(currentBin._Rectangle__center(), bin._Rectangle__center())
                    NBLen = len(nearestBins)
                    if bin.hash != currentBin.hash:     # identification of nearest spatial hashes
                        if NBLen == 0 or (NBLen > 0 and dist < nearestBins[0][0]):      # if distance to any spatial hash wasn´t assigned or current distance is smaller
                            nearestBins = [(dist, bin.hash)]
                        elif NBLen > 0 and dist == nearestBins[0][0]:      # if distance to spatial hash was assigned and current distance is equal
                            nearestBins.append((dist, bin.hash))

            ANN = (-1, -1)        
            for bin in nearestBins:     # identification of nearest point out of nearest spatial hashes containing points
                for pnt in bins[bin[1] - 1].points:
                    dist = pointDistance(point, pnt)
                    recordedDist = ANN[0]
                    if recordedDist == -1 or (recordedDist > -1 and recordedDist > dist):       # if distance to any point wasn´t assigned or current distance is smaller
                        ANN = (dist, pnt.ID)
            if ANN[0] > -1:     # if a change occured
                point.ANN = ANN[1]
    return points

def output(pntOutput : str, points : list, binsOutput : str, bins : list) -> None:
    """Writes chosen attributes of objects in input lists into output 
    files so first character of each attribute is in same column."""
    xStart = (len(str(points[-1].ID)) // 4 + 1) * 4     # position of next tab following highest ID of the hashed point
    ANNgap = (len(str(bins[-1].hash)) // 4 + 1) * 4
    with open(pntOutput, 'w') as f:     # writing of points with assigned spatial hash and ANN into output file
        for point in points:
            ID = point.ID
            IDtoX = xStart - len(str(ID))       # number of spaces between given attributes
            X = point.x
            XtoY = 20 - len(str(X))
            Y = point.y
            YtoHash = 20 - len(str(Y))
            hash = point.hash
            hashToANN = ANNgap - len(str(hash))

            rowStr = f'{ID}{IDtoX * " "}{X}{XtoY * " "}{Y}{YtoHash * " "}{hash}{hashToANN * " "}{point.ANN}'        # stringing of selected point´s attributes into a row         
            if ID != points[-1].ID:
                rowStr = f'{rowStr}\n'      # new row unless it´s the last row
            f.write(rowStr)
    
    with open(binsOutput, 'w') as f:        # writing of spatial hashes 
        for bin in bins:        
            hash = bin.hash
            hashToX1 = xStart - len(str(hash))
            X1 = bin.x1
            X1toX2 = 20 - len(str(X1))
            X2 = bin.x2
            X2toY1 = 20 - len(str(X2))
            Y1 = bin.y1
            Y1toY2 = 20 - len(str(Y1))

            rowStr = f'{hash}{hashToX1 * " "}{X1}{X1toX2 * " "}{X2}{X2toY1 * " "}{Y1}{Y1toY2 * " "}{bin.y2}'        # stringing of selected hash´s attributes into a row
            if hash != bins[-1].hash:
                rowStr = f'{rowStr}\n'
            f.write(rowStr)

def workflow(pntInput : str, pntOutput : str, hashOutput : str) -> None:
    """Using all functions above, except parse(), exucutes the whole process."""
    control(pntInput, pntOutput, hashOutput)
    loadedPnts, xMin, xMax, yMin, yMax = loadPoints(pntInput)
    divisionCount, hashes, hashBorders = createHashes(loadedPnts, xMin, xMax, yMin, yMax)
    hashedPnts, filledBins = hashPoints(divisionCount, loadedPnts, hashes, hashBorders)
    ANNPnts = approximateNearestNeighbor(hashedPnts, filledBins)
    output(pntOutput, ANNPnts, hashOutput, filledBins)

try:        
    args = parse()      # assignment of programme parameters
    workflow(args.points, args.outputPoints, args.outputHashes)     # the whole process
except MemoryError:     # errors while computing not caused by content of programme parameters
    print('Ukončení kvůli nedostaku paměti RAM.')
except KeyboardInterrupt:
    print('Program ukončen uživatelem.')
except OSError as e:
    raise SystemExit(f'Neočekávaná chyba vyvolaná Vaším počítačem: {e}.')
except Exception as e:
    print(f'Neočekávaná chyba: {e}.')