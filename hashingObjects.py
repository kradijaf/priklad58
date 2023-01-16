class Point:
    __count = 1

    def __init__(self, X : float, Y : float, createID : bool = True) -> None:
        if createID:
            self.__ID = Point.__count
            Point.__count += 1 
        else:
            self.__ID = -1      # pro body, na jejichž ID se program neptá, tj. body jiné, než načtené ze vstupu
        self.__x = X
        self.__y = Y
        self.__hash = -1        # hodnota -1 pro nevypočítané atributy
        self.__ANN = -1

    @property
    def ID(self) -> int:
        return self.__ID

    @property
    def x(self) -> float:
        return self.__x

    @property
    def y(self) -> float:
        return self.__y

    @property
    def hash(self) -> int:
        return self.__hash

    @property
    def ANN(self) -> int:
        return self.__ANN

    @hash.setter
    def hash(self, value : int) -> None:
        self.__hash = value

    @ANN.setter
    def ANN(self, value : int) -> None:
        self.__ANN = value

class Rectangle:
    def __init__(self, X1 : float, X2 : float, Y1 : float, Y2 : float, hash : int) -> None:
        self.__x1 = X1
        self.__x2 = X2
        self.__y1 = Y1
        self.__y2 = Y2
        self.__hash = hash
        self.__points = []
        self.__pointCount = 0
        self.__center = Point((X1 + X2) / 2, (Y1 + Y2) / 2, False)

    @property
    def x1(self) -> float:
        return self.__x1

    @property
    def x2(self) -> float:
        return self.__x2

    @property
    def y1(self) -> float:
        return self.__y1

    @property
    def y2(self) -> float:
        return self.__y2

    @property
    def hash(self) -> int:
        return self.__hash

    @property
    def pointCount(self) -> int:
        return self.__pointCount

    @property
    def center(self) -> Point:
        return self.__center

    @property
    def points(self) -> list:
        return self.__points 

    def __addPoint(self, pnt : Point) -> None:
        """Přidává bod do seznamu bodů."""   
        self.__points.append(pnt)
        self.__pointCount += 1