import time
import ray

database = ["Learning", "Ray", "Flexible", "Distributed", "Python", "for", "Machine", "Learning"]

@ray.remote
def retrieve(item):
    time.sleep(item / 10.)
    return item, database[item]

def print_runtime(input_data, start_time):
    print(f'Runtime: {time.time() - start_time:.2f} seconds, data:')
    print(*input_data, sep="\n")

ray.init()

start = time.time()
refs = [retrieve.remote(item) for item in range(8)]
data = ray.get(refs)
print_runtime(data, start)

@ray.remote
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1
        return self.value

    def get_counter(self):
        return self.value

# Create an actor from this class.
counter = Counter.remote()

# Call the actor a few times.
obj_ref = [counter.increment.remote() for _ in range(5)]

print(ray.get(obj_ref))