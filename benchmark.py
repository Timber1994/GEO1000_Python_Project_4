# GEO1000 - Assignment 4
# Authors: Timber Groeneveld
# Student numbers: 4213513


# feel free to import modules you need
import geometry, delaunay
import os
import time
import matplotlib.pyplot as plt

# Number of points for the input
point_sizes = [100, 200, 400, 800]
# 3 runs for accurate measurements
n_runs = 3

# Store results
results = {
    "Python": {n: [] for n in point_sizes},
    "C++ Debug": {n: [] for n in point_sizes},
    "C++ Release": {n: [] for n in point_sizes},
}

def runtime(command):
    """Run a command and return the elapsed time"""
    start = time.perf_counter()
    os.system(command)
    end = time.perf_counter()
    return end - start

def main():
    for n in point_sizes:
        print(f"Benchmarking for n = {n}...")
        # Python
        for _ in range(n_runs):
            t = runtime(r'python "D:\Werk\Studie\Master Geomatics\Python Assignment 4\py\delaunay.py" {n}'.format(n=n))
            results["Python"][n].append(t)

        # C++ Debug
        for _ in range(n_runs):
            t = runtime(r'"D:\Werk\Studie\Master Geomatics\Python Assignment 4\cpp\cmake-build-debug\triangulate.exe" {n}'.format(n=n))
            results["C++ Debug"][n].append(t)

        # C++ Release
        for _ in range(n_runs):
            t = runtime(r'"D:\Werk\Studie\Master Geomatics\Python Assignment 4\cpp\cmake-build-release\triangulate.exe" {n}'.format(n=n))
            results["C++ Release"][n].append(t)

    # Plot results
    plot_results()

def plot_results():
    plt.figure(figsize=(10, 6))
    for version in results:
        sizes = point_sizes
        avg_times = [sum(results[version][size])/n_runs for size in sizes]

        plt.plot(point_sizes, avg_times, label=version, marker='o')

    plt.xlabel("Number of Points (n)")
    plt.ylabel("Average Runtime (seconds)")
    plt.title("Runtime Comparison: Python vs C++ Debug vs C++ Release")
    plt.legend()
    plt.grid(True)
    plt.savefig("runtime_comparison.png")
    plt.show()


if __name__ == "__main__":
    main()


