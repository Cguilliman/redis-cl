import redis
import random


class ProbabilisticCacheWrapper:
    def __init__(
        self,
        redis_host="localhost",
        redis_port=6379,
        max_cache_size=100,
        eviction_probability=0.1,
    ):
        self.redis_client = redis.StrictRedis(
            host=redis_host, port=redis_port, decode_responses=True
        )
        self.max_cache_size = max_cache_size
        self.eviction_probability = eviction_probability

    def get(self, key):
        # Attempt to retrieve the value from the cache
        value = self.redis_client.get(key)

        # Update the probability of the key being accessed
        self._update_probability(key)

        return value

    def set(self, key, value):
        # Set the value in the cache
        self.redis_client.set(key, value)

        # Initialize or update the probability of the key being accessed
        self._update_probability(key)

        # Perform probabilistic eviction if the cache is full
        self._probabilistic_eviction()

    def _update_probability(self, key):
        # Increment the access count for the key
        access_count_key = f"{key}:access_count"
        self.redis_client.incr(access_count_key)

    def _probabilistic_eviction(self):
        # Check if the cache size exceeds the maximum
        cache_size = self.redis_client.dbsize()
        if cache_size > self.max_cache_size:
            # Probabilistic eviction: Iterate through keys and evict with a probability
            for key in self.redis_client.keys():
                access_count_key = f"{key}:access_count"
                access_count = int(self.redis_client.get(access_count_key) or 0)

                # Evict with a probability based on access count
                if (
                    random.random()
                    < (1.0 - 1.0 / (access_count + 1)) * self.eviction_probability
                ):
                    self.redis_client.delete(key)
                    self.redis_client.delete(access_count_key)


# Example usage
if __name__ == "__main__":
    # Create an instance of the ProbabilisticCacheWrapper
    cache_wrapper = ProbabilisticCacheWrapper()

    # Set and get values from the cache
    for i in range(200):
        cache_wrapper.set(f"key{i}", f"value{i}")

    for i in range(200):
        print(f"Value for key{i}:", cache_wrapper.get(f"key{i}"))
