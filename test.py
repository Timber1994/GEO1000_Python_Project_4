# no other imports allowed than given
import math, sys
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
        dist = math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
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
        area = math.pi * self.radius ** 2
        return area

    def perimeter(self):
        """Returns the perimeter of the circle"""
        perimeter = 2 * math.pi * self.radius
        return perimeter

    def covers(self, pt):
        """Returns True when the circle covers point *pt*,
        False otherwise

        Note that we consider points that are near to the boundary of the
        circle also to be covered by the circle (arbitrary epsilon to use: 1e-8).
        """
        dist = self.center.distance(pt)
        if self.radius > dist or dist - self.radius <= abs(1e-8):
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
        ax = self.p0.x
        ay = self.p0.y
        bx = self.p1.x
        by = self.p1.y
        cx = self.p2.x
        cy = self.p2.y

        disc = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if disc == 0:
            raise ValueError("Discriminant cannot be 0")
        ux = ((ax ** 2 + ay ** 2) * (by - cy) + (bx ** 2 + by ** 2) * (cy - ay) + (cx ** 2 + cy ** 2) * (
                    ay - by)) / disc
        uy = ((ax ** 2 + ay ** 2) * (cx - bx) + (bx ** 2 + by ** 2) * (ax - cx) + (cx ** 2 + cy ** 2) * (
                    bx - ax)) / disc

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
        s = (a + b + c) / 2
        area_squared = (s * (s - a) * (s - b) * (s - c))
        # Check for negatives or values very close to zero
        if area_squared < 0 or abs(area_squared) < 1e-8:
            return 0
        area = math.sqrt(area_squared)
        return area

    def perimeter(self):
        """Perimeter of this triangle (float)"""
        a = self.p0.distance(self.p1)
        b = self.p1.distance(self.p2)
        c = self.p2.distance(self.p0)
        perimeter = a + b + c
        return perimeter

    def covers(self, pt):
        """Returns True when the triangle covers point *pt*, False otherwise

        The implementation of this method should use the fact that a triangle
        covers a point, iff the summed area of the 3 triangles
        formed by (pt0, pt1, pt) and (pt1, pt2, pt) and (pt2, pt0, pt)
        is approximately equal (arbitrary epsilon to use: 1e-8) to the area
        of this triangle formed by its points (pt0, pt1, pt2).
        """
        area_1 = Triangle(self.p0, self.p1, pt).area()
        area_2 = Triangle(self.p1, self.p2, pt).area()
        area_3 = Triangle(self.p2, self.p0, pt).area()
        main_area = self.area()

        tot_area = area_1 + area_2 + area_3
        if abs(tot_area - main_area) < 1e-8:
            return True
        else:
            return False

class DelaunayTriangulation:
    def __init__(self, points):
        """Constructor"""
        self.triangles = []
        self.points = points

    def triangulate(self):
        """Triangulates the given set of points.

        This method takes the set of points to be triangulated
        (with at least 3 points) and for each 3-group of points instantiates
        a triangle and checks whether the triangle conforms to Delaunay
        criterion. If so, the triangle is added to the triangle list.

        To determine the 3-group of points, the group3 function is used.

        Returns None
        """
        # pre-condition: we should have at least 3 points
        n_of_points = len(self.points)
        assert len(self.points) > 2

        for item in group3(n_of_points):
            i,j,k = item
            tri = Triangle(self.points[i], self.points[j], self.points[k])
            if self.is_delaunay(tri):
                self.triangles.append(tri)

    def is_delaunay(self, tri):
        """Does a triangle *tri* conform to the Delaunay criterion?
        Algorithm:
        Are 3 points of the triangle collinear?
            No:
                Get circumcircle
                Count number of points inside circumcircle
                if number of points inside == 3:
                    Delaunay
                else:
                    not Delaunay
            Yes:
                not Delaunay
        Arguments:
            tri -- Triangle instance
        Returns:
            True/False
        """
        p0, p1, p2 = tri.p0, tri.p1, tri.p2
        if self.are_collinear(p0, p1, p2):
            return False
        circum_circle = tri.circumcircle()
        points_inside = 0
        for point in self.points:
            if circum_circle.covers(point):
                points_inside += 1
        return points_inside == 3

    def are_collinear(self, pa, pb, pc):
        """Orientation test to determine whether 3 points are collinear
        (on straight line).

        Note that we consider points that are nearly collinear also to be on
        a straight line (arbitrary epsilon to use: 1e-8).

        Returns True / False
        """
        ax, ay = pa.x, pa.y
        bx, by = pb.x, pb.y
        cx, cy = pc.x, pc.y
        orientation = ((ax-cx)*(by-cy)-(bx-cx)*(ay-cy))
        if abs(orientation)<1e-8:
            return True
        else:
            return False

    def output_points(self, open_file_obj):
        """Outputs the points of the triangulation to an open file.
        """
        header="wkt"
        open_file_obj.write(header+"\n")
        for pt in self.points:
            open_file_obj.write(pt.as_wkt()+"\n")

    def output_triangles(self, open_file_obj):
        """Outputs the triangles of the triangulation to an open file.
        """
        header="wkt"+"\t"+"triangle_id"+"\t"+"area"+"\t"+"perimeter"
        open_file_obj.write(header+"\n")
        for tri in self.triangles:
            open_file_obj.write(f"{tri.as_wkt()}\t{id(tri)}\t{tri.area()}\t{tri.perimeter()}\n")

    def output_circumcircles(self, open_file_obj):
        """Outputs the circumcircles of the triangles of the triangulation
        to an open file
        """
        header="wkt"+"\t"+"triangle_id"+"\t"+"area"+"\t"+"perimeter"
        open_file_obj.write(header+"\n")
        for tri in self.triangles:
            circle=tri.circumcircle()
            open_file_obj.write(f"{circle.as_wkt()}\t{id(tri)}\t{circle.area()}\t{circle.perimeter()}\n")


def group3(N):
    """Returns generator with 3-tuples with indices to form 3-groups
    of a list of length N.

    Total number of tuples that is generated: N! / (3! * (N-3)!)

    For N = 3: [(0, 1, 2)]
    For N = 4: [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    For N = 5: [(0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 3),
                (0, 2, 4), (0, 3, 4), (1, 2, 3), (1, 2, 4),
                (1, 3, 4), (2, 3, 4)]

    Example use:

        for item in group3(3):
            print(item)

            (0, 1, 2)

    """
    for i in range(N - 2):
        for j in range(i + 1, N - 1):
            for k in range(j + 1, N):
                yield i, j, k


def make_random_points(n):
    """Makes n points distributed randomly in x,y between [0,1000]

    Note, no duplicate points will be created, but might result in slightly
    less than the n number of points requested.
    """
    import random

    # seed the random generator, so we still get a random set of points,
    # but each time the same set of randomized ones
    random.seed(2023)
    pts = list(
        set([Point(random.randint(0, 1000), random.randint(0, 1000)) for i in range(n)])
    )
    return pts


def main(n):
    """Perform triangulation of n points and write the resulting geometries
    to text files, where the geometry is stored as well-known text strings.
    """
    pts = make_random_points(n)
    dt = DelaunayTriangulation(pts)
    dt.triangulate()
    # using the with statement, we do not need to close explicitly the file
    with open("points.wkt", "w") as fh:
        dt.output_points(fh)
    with open("triangles.wkt", "w") as fh:
        dt.output_triangles(fh)
    with open("circumcircles.wkt", "w") as fh:
        dt.output_circumcircles(fh)


def print_error():
    """Prints an eror when a script parameter is missing on the command line"""
    print("ERROR: Call this script with an integer as script parameter")
    print("to set the number of points for the triangulation.")
    print(f"Example: $ python {sys.argv[0]} 100")


def test():
    a = Point(0, 0)
    b = Point(1, 0)
    c = Point(0, 1)
    d = Point(0.5, 0.5)
    e = Point(2,2)
    f = Point(0,0)
    g = Point(1,1)
    h = Point(2,2)

    dt1 = DelaunayTriangulation([a,b,c,d])
    triangle1=Triangle(a,b,c)

    dt2 = DelaunayTriangulation([a,b,e])
    triangle2=Triangle(a,b,e)

    dt3 = DelaunayTriangulation([f,g,h])
    triangle3 = Triangle(f,g,h)

    print(dt1.is_delaunay(triangle1))
    print(dt2.is_delaunay(triangle2))
    print(dt3.is_delaunay(triangle3))


if __name__ == "__main__":
    print("This is the name of the Python script:", sys.argv[0])
    print("Number of arguments:", len(sys.argv))
    print("The arguments are:" , str(sys.argv))
    if len(sys.argv) != 2:
        print_error()
    else:
        try:
            point_count = int(sys.argv[1])
            print("Running triangulation...")
            main(point_count)
            print("done.")
        except ValueError:
            print_error()
            raise

