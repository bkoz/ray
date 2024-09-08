import ray

#
# Will use RAY_ADDRESS if set.
#
r = ray.init()
print()
print(r)
print()
print(ray.available_resources())
