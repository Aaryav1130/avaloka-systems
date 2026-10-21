"""
Unit tests for LRUCache and ThreadSafeLRUCache.
"""

import threading
import unittest
from src.lru_cache import LRUCache, ThreadSafeLRUCache


class TestLRUCache(unittest.TestCase):
    def test_initialization_invalid_capacity(self):
        with self.assertRaises(ValueError):
            LRUCache(0)
        with self.assertRaises(ValueError):
            LRUCache(-3)

    def test_basic_put_and_get(self):
        cache = LRUCache(2)
        cache.put(1, "val1")
        cache.put(2, "val2")
        self.assertEqual(cache.get(1), "val1")
        self.assertEqual(cache.get(2), "val2")

    def test_missing_key_returns_negative_one(self):
        cache = LRUCache(2)
        self.assertEqual(cache.get(99), -1)
        cache.put(1, 100)
        self.assertEqual(cache.get(2), -1)

    def test_eviction_order_on_capacity(self):
        cache = LRUCache(2)
        cache.put(1, 10)
        cache.put(2, 20)
        cache.put(3, 30)  # Evicts 1

        self.assertEqual(cache.get(1), -1)
        self.assertEqual(cache.get(2), 20)
        self.assertEqual(cache.get(3), 30)

    def test_get_promotes_key_recency(self):
        cache = LRUCache(2)
        cache.put(1, 10)
        cache.put(2, 20)
        # Access 1 -> 1 becomes MRU, 2 becomes LRU
        self.assertEqual(cache.get(1), 10)
        # Adding 3 should evict 2 (not 1)
        cache.put(3, 30)
        self.assertEqual(cache.get(2), -1)
        self.assertEqual(cache.get(1), 10)
        self.assertEqual(cache.get(3), 30)

    def test_put_updates_existing_key_in_place(self):
        cache = LRUCache(2)
        cache.put(1, 10)
        cache.put(2, 20)
        cache.put(1, 100)  # Update 1 -> value changes, 1 is MRU
        self.assertEqual(cache.get(1), 100)
        self.assertEqual(len(cache), 2)
        # Adding 3 should evict 2
        cache.put(3, 30)
        self.assertEqual(cache.get(2), -1)
        self.assertEqual(cache.get(1), 100)

    def test_capacity_one(self):
        cache = LRUCache(1)
        cache.put(1, "A")
        self.assertEqual(cache.get(1), "A")
        cache.put(2, "B")
        self.assertEqual(cache.get(1), -1)
        self.assertEqual(cache.get(2), "B")
        cache.put(2, "C")
        self.assertEqual(cache.get(2), "C")

    def test_canonical_leetcode_sequence(self):
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        self.assertEqual(cache.get(1), 1)
        cache.put(3, 3)  # evicts 2
        self.assertEqual(cache.get(2), -1)
        cache.put(4, 4)  # evicts 1
        self.assertEqual(cache.get(1), -1)
        self.assertEqual(cache.get(3), 3)
        self.assertEqual(cache.get(4), 4)


class TestThreadSafeLRUCache(unittest.TestCase):
    def test_concurrent_read_write(self):
        cache = ThreadSafeLRUCache(50)
        errors = []

        def worker(start_key: int):
            try:
                for k in range(start_key, start_key + 200):
                    cache.put(k, k * 2)
                    _ = cache.get(k)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i * 100,)) for i in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Encountered thread errors: {errors}")
        self.assertLessEqual(len(cache), 50)


if __name__ == "__main__":
    unittest.main()
