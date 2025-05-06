import numpy as np
import ray

@ray.remote(num_returns="dynamic", num_cpus=1)
def split(array, chunk_size):
    while len(array) > 0:
        yield array[:chunk_size]
        array = array[chunk_size:]


array_ref = ray.put(np.zeros(np.random.randint(1000_000)))
block_size = 1000

# Returns an ObjectRef[DynamicObjectRefGenerator].
dynamic_ref = split.remote(array_ref, block_size)
print(dynamic_ref)
# ObjectRef(c8ef45ccd0112571ffffffffffffffffffffffff0100000001000000)

i = -1
ref_generator = ray.get(dynamic_ref)
print(ref_generator)
# <ray._raylet.DynamicObjectRefGenerator object at 0x7f7e2116b290>
for i, ref in enumerate(ref_generator):
    # Each DynamicObjectRefGenerator iteration returns an ObjectRef.
    assert len(ray.get(ref)) <= block_size
num_blocks_generated = i + 1
array_size = len(ray.get(array_ref))
assert array_size <= num_blocks_generated * block_size
print(f"Split array of size {array_size} into {num_blocks_generated} blocks of "
      f"size {block_size} each.")
# Split array of size 63153 into 64 blocks of size 1000 each.

print(ray.cluster_resources())

# NOTE: The dynamic_ref points to the generated ObjectRefs. Make sure that this
# ObjectRef goes out of scope so that Ray can garbage-collect the internal
# ObjectRefs.
del dynamic_ref