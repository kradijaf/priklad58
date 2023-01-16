try:
    from hashingObjects import *
    from argparse import ArgumentParser, Namespace
except ImportError:
    raise SystemExit('Problém při importu knihoven.')

def parse() -> Namespace:
    """Do proměnné typu argparse.Namespace přiřazuje parametry programu, ty mohou být zadány v libovolném pořadí,
    pokud některé nejsou zadány, program hledá hodnotu proměnné "default" ve složce, ve které se nachází."""
    parser = ArgumentParser()
    parser.add_argument('-p', action = 'store', nargs = '?', default = 'body.txt', dest = 'points')        # argument -p <názevSouboru> pro soubor se vstupními body  
    parser.add_argument('-op', action = 'store', nargs = '?', default = 'hashovaneBody.txt', dest = 'outputPoints')     # argument -op <názevSouboru> pro soubor pro výstupní body  
    parser.add_argument('-oh', action = 'store', nargs = '?', default = 'hraniceHashu.txt', dest = 'outputHashes')      # argument -oh <názevSouboru> pro soubor pro výstupní hashe
    return parser.parse_args()

def control(pointInput : str, pointOutput : str, hashOutput : str) -> None:
    """Kontroluje existenci souborů a právo s nimi pracovat, a jejich formát."""
    for file in (pointInput, pointOutput, hashOutput):      # test formátu souborů
        if '.txt' not in file:
            raise SystemExit(f'Soubor "{file}" není textový soubor.')
    try:
        with open(pointInput) as p,\
        open(pointOutput, 'w') as po,\
        open(hashOutput, 'w') as ho:
            try:        # testování souboru se vstupními body
                if not p.readable():
                    raise SystemExit('Soubor se vstupními body nelze číst.')     
            except Exception as e:      
                raise SystemExit(f'Neočekávaná chyba v souboru se vstupními body: {e}.')

            try:        # testování souboru pro výstupní body
                if not po.writable():
                    raise SystemExit('Do souboru pro výstupní body nelze zapisovat.')    
            except Exception as e:
                raise SystemExit(f'Neočekávaná chyba v souboru pro výstupní body: {e}.')

            try:        # testování souboru pro výstupní hashe
                if not ho.writable():
                    raise SystemExit('Do souboru pro výstupní prostorové hashe nelze zapisovat.')    
            except Exception as e:
                raise SystemExit(f'Neočekávaná chyba v souboru pro výstupní prostorové hashe: {e}.')
    except FileNotFoundError as e:
        raise SystemExit(f'Vstupní soubor neexistuje: {e}.')
    except PermissionError as e:
        raise SystemExit(f'Program nemá právo pracovat se vstupním souborem: {e}.')
    except OSError as e:
        raise SystemExit(f'Neočekávaná chyba při kontrole souborů vyvolaná Vaším počítačem: {e}.')

def rowToPoint(line : str) -> Point:
    """Pokud je to možné, převádí vstupní řetězec na objekt třídy Point."""
    l2 = line.replace(',', '.').split()     # čísla mohou být oddělena čárkou nebo tečkou
    try:
        return Point(float(l2[0]), float(l2[1]))
    except:
        line = line.strip()
        print(f'Pro řádek "{line}" nejde vytvořit bod.')

def appendPoint(row : str, pointList : list, xMinimum : float, xMaximum : float, yMinimum : float, yMaximum : float):       
    """Na konec zadaného seznamu, pokud možno, přidává řetězec převedený na objekt třídy Point, pokud byl převod 
    na bod úspěšný, porovná jeho souřadnice s nejvyššími a nejnižšími zaznamenanými, ty případně přepíše. 
    Vrací rozšířený vstupní seznam a celkově nejvyšší a nejnižší souřadnice."""
    # není vhodné appendovat ve vnořené funkci a upravený vstupní seznam vracet, takto kód méně porušuje DRY
    pnt = rowToPoint(row)
    if pnt != None:     # pokud převod na bod uspěl:
        pointList.append(pnt)
        if len(pointList) == 0:
            xMinimum = pnt.x
            xMaximum = pnt.x
            yMinimum = pnt.y
            yMaximum = pnt.y
        else:
            tmp = pnt.x
            if tmp < xMinimum:
                xMinimum = tmp
            elif tmp > xMaximum:
                xMaximum = tmp

            tmp = pnt.y
            if tmp < yMinimum:
                yMinimum = tmp
            elif tmp > yMaximum:
                yMaximum = tmp
    return pointList, xMinimum, xMaximum, yMinimum, yMaximum

def loadPoints(inputFile : str):
    """Z každého korektního řádku vstupního souboru vytváří objekt třídy Point,
    vrací seznam načtených bodů a nejvyšší a nejnižší souřadnice načtených bodů."""
    with open(inputFile, 'r') as f:
        l = f.readline()
        points = []
        minimalX = 0.0; maximalX = 0.0; minimalY = 0.0; maximalY = 0.0
        points, minimalX, maximalX, minimalY, maximalY = appendPoint(l, points, minimalX, maximalX, minimalY, maximalY)
        while l:
            l = f.readline()
            if l.strip() != '':
                points, minimalX, maximalX, minimalY, maximalY = appendPoint(l, points, minimalX, maximalX, minimalY, maximalY)
    if points == []:
        raise SystemExit('Neexistují body, se kterými lze pracovat')   
    return points, minimalX, maximalX, minimalY, maximalY

def createHashes(points : list, xMinimum : float, xMaximum : float, yMinimum : float, yMaximum : float):
    """Z extrémů souřadnic vytvoří ohraničující obdélník, ten rozdělí na prostorové hashe. Vrací počet prostorových hashů, tvořící 
    délku strany obdélníku, seznam objektů třídy Rectangle (prostorové hashe) a seznam hranic x a y souřadnic hashů."""
    bins = []       # proměnné pro vytváření prostorových hashů: 
    binIndex = 1
    borders = ([], [])     # kolekce pro hranice prostorových hashů
            # proměnné určující prostorový rozsah, pro který budou vytvořeny prostorové hashe:
    xLen = abs(xMaximum - xMinimum)     # šířka a výška obálky korektních vstupních bodů    
    yLen = abs(yMaximum - yMinimum)    
    sideDivisions = round(len(points) ** (1/4))        # počet stran, na které bude rozdělena strana ohraničujícího obdélníku, počet prostorových hashů = 2. mocnina této hodnoty
    xInterval = xLen / sideDivisions        # šířka a výška prostorového hashe
    yInterval = yLen / sideDivisions   

    bYMin = yMinimum        # proměnné určující rozsah konkrétního prostorového hashe
    bYMax = yMinimum + yInterval
            # rozdělení ohraničujícího obdélníku na jednotlivé prostorové hashe: 
    for i in range(1, sideDivisions + 1):       # tvorba sloupců
        bXMin = xMinimum
        bXMax = xMinimum + xInterval
        for j in range(1, sideDivisions + 1):       # tvorba řádků
            bin = Rectangle(bXMin, bXMax, bYMin, bYMax, binIndex)

            for border in (bXMin, bXMax):       # přiřazení hranic prostorových hashů do kolekce jejich hranic (později jednodušší práce, oproti zjišťování z atributů třídy Rectangle)
                if border not in borders[0]:
                    borders[0].append(border)
            for border in (bYMin, bYMax):
                if border not in borders[1]:  
                    borders[1].append(border)

            bins.append(bin)
            binIndex += 1
            bXMin += xInterval
            if (binIndex % sideDivisions != 0):     
                bXMax += xInterval
            else:
                bXMax = xMaximum        # přiřazení hodnoty načtené ze vstupu místo přičítaní hodnoty ze vstupů vypočtené může způsobit menší odchylku
        bYMin += yInterval
        if i != (sideDivisions - 1):
            bYMax += yInterval
        else:
            bYMax = yMaximum        
    return sideDivisions, bins, borders

def hashPoints(sideDivisions : int, points : list, bins : list, borders : tuple):
    """Každému bodu ze vstupního seznamu přiřadí prostorový hash, vrací seznam bodů se 
    zapsaným indexem prostorového hashe a prostorové hashe s přiřazenými body do nich spadajících."""
    for point in points:
        colIndex = 1        # nastavení indexů prostorového hashe
        rowIndex = 1

        for i in range(len(borders[0]) - 1):        # určení sloupcového indexu
            colRange = (borders[0][i], borders[0][i + 1])
            if colIndex == sideDivisions and point.x >= colRange[0]:        # sideDivisions pro sloupec na pravém okraji ohraničujícího obdélníku
                break
            elif point.x >= colRange[0] and point.x < colRange[1]:
                break
            colIndex += 1

        for i in range(len(borders[1]) - 1):        # určení řádkového indexu
            rowRange = (borders[1][i], borders[1][i + 1])
            if rowIndex == sideDivisions and point.y >= rowRange[0]:        # sideDivisions pro řádek na horním okraji ohraničujícího obdélníku
                break
            elif point.y >= rowRange[0] and point.y < rowRange[1]:
                break
            rowIndex += 1

        binIndex = colIndex + ((rowIndex - 1) * sideDivisions)        # výpočet indexu prostorového hashe bodu
        point.hash = binIndex       # přiřazení indexu do bodu
        bins[binIndex - 1]._Rectangle__addPoint(point)      # přidání bodu do prostorového hashe
    return points, bins

def pointDistance(p1 : Point, p2 : Point) -> float:
    """Vrací vzdálenost dvou bodů počítanou Pythagorovou větou."""
    return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2)**(1/2)

def approximateNearestNeighbor(points : list, bins : list) -> list:
    """Pokud v seznamu bodů je více, jak 1 bod, každému bodu v seznamu přiřadí ID 
    odhadovaného nejbližšího bodu do atributu "ANN". Vrací takto upravený seznam bodů."""
    for point in points:
        currentBin = bins[point.hash - 1]
        if currentBin.pointCount > 1:     # pokud prostorový hash bodu obsahuje další body
            minDistance = (-1, -1)
            for pnt in currentBin.points:
                dist = pointDistance(point, pnt)
                recordedDist = minDistance[0]
                if point.ID != pnt.ID and (recordedDist == -1 or dist < recordedDist):      # pokud nebyla přiřazena vzdálenost k žádnému bodu nebo je aktuální vzdálenost menší
                    minDistance = (dist, pnt.ID)
            if minDistance[0] > -1:     # pokud došlo ke změně
                point.ANN = minDistance[1]

        else:       # aproximace nejbližšího souseda z nejbližších prostorových hashů
            nearestBins = []
            for bin in bins:        # hledání nejbližšího souseda mimo vlastní prostorový hash pro hashe obsahující body
                if bin.pointCount > 0:      
                    dist = pointDistance(currentBin.center, bin.center)
                    NBLen = len(nearestBins)
                    if bin.hash != currentBin.hash:     # určení nejbližších prostorových hashů
                        if NBLen == 0 or (NBLen > 0 and dist < nearestBins[0][0]):      # pokud nebyla přiřazena vzdálenost k žádnému hashi nebo je aktuální vzdálenost menší
                            nearestBins = [(dist, bin.hash)]
                        elif NBLen > 0 and dist == nearestBins[0][0]:      # pokud byla přiřazena vzdálenost k hashi a aktuální vzdálenost je stejná
                            nearestBins.append((dist, bin.hash))

            ANN = (-1, -1)        
            for bin in nearestBins:     # určení nejbližšího bodu z nejbližších prostorových hashů
                for pnt in bins[bin[1] - 1].points:
                    dist = pointDistance(point, pnt)
                    recordedDist = ANN[0]
                    if recordedDist == -1 or (recordedDist > -1 and recordedDist > dist):       # pokud nebyla přiřazena vzdálenost k žádnému bodu nebo je aktuální vzdálenost menší
                        ANN = (dist, pnt.ID)
            if ANN[0] > -1:     # pokud došlo ke změně
                point.ANN = ANN[1]
    return points

def output(pntOutput : str, points : list, binsOutput : str, bins : list) -> None:
    """Do výstupních souborů zapíše vybrané atributy položek v 
    seznamech tak, aby první znak atributu vždy začínal stejným sloupcem."""
    xStart = (len(str(points[-1].ID)) // 4 + 1) * 4     # pozice dalšího tabulátoru po nejdelším ID hashovaného bodu
    ANNgap = (len(str(bins[-1].hash)) // 4 + 1) * 4
    with open(pntOutput, 'w') as f:     # výpis bodů s určeným hashem a ANN
        for point in points:
            ID = point.ID
            IDtoX = xStart - len(str(ID))       # počet mezer mezi danými atributy
            X = point.x
            XtoY = 20 - len(str(X))
            Y = point.y
            YtoHash = 20 - len(str(Y))
            hash = point.hash
            hashToANN = ANNgap - len(str(hash))

            rowStr = f'{ID}{IDtoX * " "}{X}{XtoY * " "}{Y}{YtoHash * " "}{hash}{hashToANN * " "}{point.ANN}'        
            if ID != points[-1].ID:
                rowStr = f'{rowStr}\n'      # nový řádek, pokud se nejedná o poslední řádek
            f.write(rowStr)
    
    with open(binsOutput, 'w') as f:        # výpis prostorových hashů
        for bin in bins:        
            hash = bin.hash
            hashToX1 = xStart - len(str(hash))
            X1 = bin.x1
            X1toX2 = 20 - len(str(X1))
            X2 = bin.x2
            X2toY1 = 20 - len(str(X2))
            Y1 = bin.y1
            Y1toY2 = 20 - len(str(Y1))

            rowStr = f'{hash}{hashToX1 * " "}{X1}{X1toX2 * " "}{X2}{X2toY1 * " "}{Y1}{Y1toY2 * " "}{bin.y2}'
            if hash != bins[-1].hash:
                rowStr = f'{rowStr}\n'
            f.write(rowStr)

def workflow(pntInput : str, pntOutput : str, hashOutput : str) -> None:
    """S využitím všech funkcí, kromě parse(), vykonává celý proces."""
    control(pntInput, pntOutput, hashOutput)
    loadedPnts, xMin, xMax, yMin, yMax = loadPoints(pntInput)
    divisionCount, hashes, hashBorders = createHashes(loadedPnts, xMin, xMax, yMin, yMax)
    hashedPnts, filledBins = hashPoints(divisionCount, loadedPnts, hashes, hashBorders)
    ANNPnts = approximateNearestNeighbor(hashedPnts, filledBins)
    output(pntOutput, ANNPnts, hashOutput, filledBins)

try:
    args = parse()
    workflow(args.points, args.outputPoints, args.outputHashes)
except MemoryError:
    print('Ukončení kvůli nedostaku paměti RAM.')
except KeyboardInterrupt:
    print('Program ukončen uživatelem.')
except OSError as e:
    raise SystemExit(f'Neočekávaná chyba vyvolaná Vaším počítačem: {e}.')
except Exception as e:
    print(f'Neočekávaná chyba: {e}.')