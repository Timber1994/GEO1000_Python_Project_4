# GEO1000 - Assignment 4
# Authors: Timber Groeneveld
# Student numbers: 4213513

# no other imports allowed than given
import math
from patsy.state import center


class Point:
    """Point, with x- and y-coordinate"""

    def __init__(self, x, y):
        """Constructor

        :param x: x-coordinate of the Point
        :type x: number

        :param y: y-coordinate of the Point
        :type y: number
        """
        self.x = float(x)
        self.y = float(y)

    def __str__(self):
        """string method -- for print function"""
        return "point({0}, {1})".format(self.x, self.y)

    def as_wkt(self):
        """Well Known Text of this point
        """
        return "POINT({} {})".format(self.x, self.y)

    def distance(self, other):
        """Returns distance to the *other* point 
        (assuming Euclidean geometry)

        :param other: the point to compute the distance to
        :type other: Point
        """
        dist=math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        return dist

    def __hash__(self):
        """Allows a Point instance to be used 
        (as key) in a dictionary or in a set (i.e. hashed collections)."""
        return hash((self.x, self.y))

    def __eq__(self, other):
        """Compare Point instances for equivalence 
        (this object instance == other instance?).

        :param other: the point to compare with
        :type other: Point

        Returns True/False
        """
        return self.x == other.x and self.y == other.y


class Circle:
    """Circle, with center and radius"""

    def __init__(self, center, radius):
        """Constructor

        :param center: center of the circle
        :type center: Point

        :param radius: radius of the circle
        :type radius: float
        """
        self.center = center
        self.radius = float(radius)

    def __str__(self):
        """string method -- for print function"""
        return "circle<c:{0}, r:{1}>".format(self.center, self.radius)

    def area(self):
        """Returns the area of the circle"""
        area=math.pi*self.radius**2
        return area

    def perimeter(self):
        """Returns the perimeter of the circle"""
        perimeter=2*math.pi*self.radius
        return perimeter

    def covers(self, pt):
        """Returns True when the circle covers point *pt*, 
        False otherwise

        Note that we consider points that are near to the boundary of the 
        circle also to be covered by the circle (arbitrary epsilon to use: 1e-8).
        """
        dist=self.center.distance(pt)
        if self.radius > dist or dist-self.radius <= abs(1e-8):
            return True
        else:
            return False

    def as_wkt(self):
        """Returns WKT str, discretizing the circle into straight
        line segments
        """
        N = 400  # the number of segments
        step = 2.0 * math.pi / N
        pts = []
        for i in range(N):
            pts.append(
                Point(
                    self.center.x + math.cos(i * step) * self.radius,
                    self.center.y + math.sin(i * step) * self.radius,
                )
            )
        pts.append(pts[0])
        coordinates = ["{0} {1}".format(pt.x, pt.y) for pt in pts]
        coordinates = ", ".join(coordinates)
        return "POLYGON(({0}))".format(coordinates)


class Triangle:
    def __init__(self, p0, p1, p2):
        """Constructor

        Arguments: p0, p1, p2 -- Point instances
        """
        self.p0, self.p1, self.p2 = p0, p1, p2

    def __str__(self):
        return "triangle<p0:{0}, p1:{1}, p2:{2}>".format(self.p0, self.p1, self.p2)

    def as_wkt(self):
        """String representation
        """
        points = [
            "{0.x} {0.y}".format(pt) for pt in (self.p0, self.p1, self.p2, self.p0)
        ]
        return "POLYGON(({0}))".format(", ".join(points))

    def circumcircle(self):
        """Returns Circle instance that intersects the 3 points of the triangle.

        Note, the assignment sheet contains a formula for calculating the 
        center of this Circle.
        """
        ax=self.p0.x
        ay=self.p0.y
        bx=self.p1.x
        by=self.p1.y
        cx=self.p2.x
        cy=self.p2.y

        disc = 2.0*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by))
        if disc == 0:
            raise ValueError("Discriminant cannot be 0")
        ux = ((ax**2+ay**2)*(by-cy)+(bx**2+by**2)*(cy-ay)+(cx**2+cy**2)*(ay-by))/disc
        uy = ((ax**2+ay**2)*(cx-bx)+(bx**2+by**2)*(ax-cx)+(cx**2+cy**2)*(bx-ax))/disc

        center = Point(ux, uy)
        radius = center.distance(self.p0)
        return Circle(center, radius)

    def area(self):
        """Area of this triangle, using Heron's formula.
        
        In case you run into a negative value for taking the square root 
        (which is not possible), and one of the terms is very close to zero,
        it is okay to return 0.0 for the area.
        """
        # Calculate side lengths with distance method from the Point class
        a = self.p0.distance(self.p1)
        b = self.p1.distance(self.p2)
        c = self.p2.distance(self.p0)
        # Use Heron's formula
        s=(a+b+c)/2
        area_squared=(s*(s-a)*(s-b)*(s-c))
        # Check for negatives or values very close to zero
        if area_squared < 0 or abs(area_squared) < 1e-8:
            return 0
        area=math.sqrt(area_squared)
        return area

    def perimeter(self):
        """Perimeter of this triangle (float)"""
        a = self.p0.distance(self.p1)
        b = self.p1.distance(self.p2)
        c = self.p2.distance(self.p0)
        perimeter=a+b+c
        return perimeter

    def covers(self, pt):
        """Returns True when the triangle covers point *pt*, False otherwise

        The implementation of this method should use the fact that a triangle
        covers a point, iff the summed area of the 3 triangles
        formed by (pt0, pt1, pt) and (pt1, pt2, pt) and (pt2, pt0, pt)
        is approximately equal (arbitrary epsilon to use: 1e-8) to the area
        of this triangle formed by its points (pt0, pt1, pt2).
        """
        area_1=Triangle(self.p0, self.p1, pt).area()
        area_2=Triangle(self.p1, self.p2, pt).area()
        area_3=Triangle(self.p2, self.p0, pt).area()
        main_area=self.area()

        tot_area=area_1+area_2+area_3
        if abs(tot_area-main_area) < 1e-8:
            return True
        else:
            return False


def _test():
    """p0 = Point(0, 0)
    p1 = Point(1, 0)
    p2 = Point(0, 1)

    t = Triangle(p0, p1, p2)
    c = t.circumcircle()

    print(c.center)
    print(c.radius)"""


if __name__ == "__main__":
    _test()
