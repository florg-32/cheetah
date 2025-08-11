import csv
import sys
from bisect import bisect_left 

STEP_SIZE_MILLIS = 500

def next_multiple(val, multiple):
    return ((val + multiple - 1) // multiple) * multiple

times = []
ratings = []
with open(sys.argv[1], "r") as file:
    for row in csv.reader(file):
        times.append(int(row[0][:-2]))
        ratings.append(int(row[1]))

start_time = next_multiple(times[0], STEP_SIZE_MILLIS)
stop_time = next_multiple(times[-1], STEP_SIZE_MILLIS)

output_times = []
output_ratings = [] 
for step in range(start_time, stop_time, STEP_SIZE_MILLIS):
    index = bisect_left(times, step)
    output_times.append(step)
    output_ratings.append(ratings[index-1])

with open(sys.argv[2], "w") as file:
    writer = csv.writer(file, dialect="excel")
    writer.writerows(zip(*[output_times, output_ratings]))

# def plot():
#     import seaborn as sns
#     import matplotlib.pyplot as plt
#     _, ax = plt.subplots()
#     sns.lineplot(x=times, y=ratings, ax=ax, color="blue", marker="X")
#     sns.lineplot(x=output_times, y=output_ratings, marker="X", ax=ax, color="orange")
#     plt.show()
# plot()
