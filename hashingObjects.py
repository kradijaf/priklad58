class Point:
    __count = 1

    def __init__(self, X : float, Y : float, createID : bool = True) -> None:
        if createID:
            self.__ID = Point.__count      # only points loaded from input need an ID
            Point.__count += 1 
        else:
            self.__ID = -1      # for points other than loaded from the input
        self.__x = X
        self.__y = Y
        self.__hash = -1        # value -1 for uncalculated attributes
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

class Rectangle:        # used for spatial hashes
    def __init__(self, X1 : float, X2 : float, Y1 : float, Y2 : float, hash : int) -> None:
        self.__x1 = X1
        self.__x2 = X2
        self.__y1 = Y1
        self.__y2 = Y2
        self.__hash = hash      # ID of a spatial hash
        self.__points = []      # list for points inside the spatial hash

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
    def points(self) -> list:
        return self.__points

    def __addPoint(self, pnt : Point) -> None:
        """Pushes point into list of points."""   
        self.__points.append(pnt)

    def __center(self) -> Point:
        """Returns Point representing center of gravity of given instance of Rectangle."""
        return Point((self.__x1 + self.__x2) / 2, (self.__y1 + self.__y2) / 2, False)

    def __pointCount(self) -> int:
        """Returns number of points in list of points."""
        return len(self.__points)