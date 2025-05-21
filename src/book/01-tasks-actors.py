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

# Call the actor 5 times.
obj_ref = [counter.increment.remote() for _ in range(5)]

# Optionally, wait for the actor to finish using ray.wait()
# This will block until the actor has finished with num_returns tasks.
# Note: This will not block if the actor is already finished.
obj_ref, _ = ray.wait(obj_ref, num_returns=3)

# Get the results of the actor.
print(f'Counter: {ray.get(obj_ref)}')
