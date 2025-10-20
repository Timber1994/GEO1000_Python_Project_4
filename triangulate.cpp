#if _MSC_VER
// pre-processor directive
// if the compiler is MSVC, we need to add this #define directive to get
// access to the various math constants (like M_PI)
// https://docs.microsoft.com/en-us/cpp/c-runtime-library/math-constants?view=msvc-160
#define _USE_MATH_DEFINES
#endif // _MSC_VER

#include <cmath>
#include <algorithm>
#include <iostream>
#include <fstream>
#include <random>
#include <vector>


// epsilon for checking whether values are close
const double EPSILON = 1e-8;


// Point class
class Point {
public:
    double x, y;
};


// Triangle class
class Triangle {
public:
    Point a, b, c;
};


// Function to calculate the distance between two points
double distance(const Point &a, const Point &b) {
    return std::sqrt(std::pow(b.x - a.x, 2) + std::pow(b.y - a.y, 2));
}


// Function to check if 3 points are collinear
bool areCollinear(const Point &pa, const Point &pb, const Point &pc) {
    double det_left = (pa.x - pc.x) * (pb.y - pc.y);
    double det_right = (pa.y - pc.y) * (pb.x - pc.x);
    double det = det_left - det_right;
    return fabs(det) <= EPSILON;
}


// Circle class based on center point and radius
class Circle {
public:
    Point center;
    double radius;

    // Method to check if a point p is inside the circle c
    bool covers(const Point &p) const {
        return distance(p, this->center) <= this->radius + EPSILON;
    }
};


// Function to calculate the circumcircle of a triangle
Circle circumcircle(Triangle t) {
    double D = 2.0 * (t.a.x * (t.b.y - t.c.y) + t.b.x * (t.c.y - t.a.y) + t.c.x * (t.a.y - t.b.y));
    Point center = {
        (
            (t.a.x * t.a.x + t.a.y * t.a.y) * (t.b.y - t.c.y)
            + (t.b.x * t.b.x + t.b.y * t.b.y) * (t.c.y - t.a.y)
            + (t.c.x * t.c.x + t.c.y * t.c.y) * (t.a.y - t.b.y)
        ) / D,
        (
            (t.a.x * t.a.x + t.a.y * t.a.y) * (t.c.x - t.b.x)
            + (t.b.x * t.b.x + t.b.y * t.b.y) * (t.a.x - t.c.x)
            + (t.c.x * t.c.x + t.c.y * t.c.y) * (t.b.x - t.a.x)
        ) / D
    };

    // The radius of the circumcircle is the distance from the center to any of the triangle's vertices
    double radius = distance(center, t.a);

    return {center, radius};
}

// Function to print a circle in WKT format
void printCircleWKT(const Circle &c, std::ostream& stream, int num_segments = 100) {
    stream << "POLYGON ((";
    stream << c.center.x + c.radius << " " << c.center.y; // first point
    for (int i = 1; i < num_segments; ++i) {
        double theta = 2.0 * M_PI * i / num_segments;
        double dx = c.radius * std::cos(theta);
        double dy = c.radius * std::sin(theta);
        stream << ", ";
        stream << c.center.x + dx << " " << c.center.y + dy;
    }
    stream << ", ";
    stream << c.center.x + c.radius << " " << c.center.y; // last
    stream << "))" << std::endl;
}

// Function to print a triangle in WKT format
void printTriangleWKT(const Triangle &t, std::ostream& stream) {
    stream << "POLYGON (("
              << t.a.x << " " << t.a.y << ", "
              << t.b.x << " " << t.b.y << ", "
              << t.c.x << " " << t.c.y << ", "
              << t.a.x << " " << t.a.y
              << "))" << std::endl;
}

// Function to print a point in WKT format
void printPointWKT(const Point &p, std::ostream& stream) {
    stream << "POINT ("
              << p.x << " " << p.y
              << ")" << std::endl;
}


// the triangulation happens in this function
void triangulate(int number_of_points) {
    // Use default random number generator
    std::default_random_engine generator;
    // seed the random generator
    // it will be random points, but always the same ones
    generator.seed(2023); 
    std::uniform_int_distribution<int> distribution(0, 100);

    // Generate random points
    std::vector<Point> points(number_of_points);
    for (int i = 0; i < number_of_points; ++i) {
        auto x = distribution(generator);
        auto y = distribution(generator);
        points[i] = {static_cast<double>(x), static_cast<double>(y)};
    }

    // Check all possible combinations of triangles
    std::vector<Triangle> triangles;
    for (int i = 0; i < number_of_points; ++i) {
        for (int j = i + 1; j < number_of_points; ++j) {
            for (int k = j + 1; k < number_of_points; ++k) {
                // orientation test; skip if points are on a line
                if (areCollinear(points[i], points[j], points[k]) == true) {
                    continue;
                }
                Triangle t = {points[i], points[j], points[k]};
                Circle c = circumcircle(t);
                // Check if any other point is inside this circle
                int cover_count = 0;
                for (int l = 0; l < number_of_points; ++l) {
                    if (c.covers(points[l])) { // if so, increase the count
                        cover_count += 1;
                    }
                }
                // if we have exactly 3 points covered (the 3 corners)
                // it's a valid delaunay triangle
                if (cover_count == 3) {
                    triangles.push_back(t);
                }
            }
        }
    }

    // Print all Delaunay triangles
    for (const Triangle &t: triangles) {
        printTriangleWKT(t, std::cout);
    }

    // Print all circles
    for (const Triangle &t: triangles) {
        Circle c = circumcircle(t);
        printCircleWKT(c, std::cout);
    }

    // Print all points
    for (const Point &p: points) {
        printPointWKT(p, std::cout);
    }

    // It is also possible to store the output in a file
    // std::ofstream point_file;
    // point_file.open("points.wkt");
    // for (const Point &p: points) {
    //     printPointWKT(p, point_file);
    // }
    // point_file.close();

}

int main(int argc, char **argv) {
    // for Clion, check:
    // https://www.jetbrains.com/help/clion/run-debug-configuration-application.html#config-tab
    // on how to set the number of points as program argument
    if (argc != 2) {
        // when the program is run for the terminal and does not receive
        // enough arguments, stop and explain the necessary input
        std::cout << "This is " << argv[0] << std::endl;
        std::cout << "Call this program with an integer as program argument" << std::endl;
        std::cout << "(to set the number of points for the triangulation)." << std::endl;
        return EXIT_FAILURE;
    } else {
        // otherwise, generate the random number of points and triangulate
        const int point_count = atoi(argv[1]);
        triangulate(point_count);
        return EXIT_SUCCESS;
    }
}

