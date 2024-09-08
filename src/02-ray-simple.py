import ray
import time

ray.init()

print(ray.available_resources())

# Define the square task.
@ray.remote
def square(x):
    return x * x

# Launch N parallel square tasks.
futures = [square.remote(i) for i in range(4)]

# Retrieve results.
print(ray.get(futures))
# -> [0, 1, 4, 9]

# print("Sleeping for 60 seconds")
# time.sleep(60)


