"""
LRU Cache Implementation
========================
Provides constant-time O(1) key-value access and recency tracking using
a composite Hash Map and Doubly Linked List data structure.

Includes:
- `Node`: Doubly linked list node storing (key, value) pairs.
- `LRUCache`: Classic O(1) single-threaded LRU cache.
- `ThreadSafeLRUCache`: Thread-safe extension using mutex locking.
"""

import threading
from typing import Any, Optional


class Node:
    """A node in a doubly linked list.
    
    Attributes:
        key: The lookup key associated with the cached value.
        value: The payload cached under the key.
        prev: Pointer to the previous node (towards MRU / head).
        next: Pointer to the next node (towards LRU / tail).
    """

    def __init__(self, key: Any, value: Any):
        self.key = key
        self.value = value
        self.prev: Optional["Node"] = None
        self.next: Optional["Node"] = None


class LRUCache:
    """Least Recently Used (LRU) Cache with deterministic O(1) operations.
    
    Achieves O(1) time complexity by coupling a hash map (for direct node lookup)
    with a doubly linked list (for constant-time node promotion and eviction).
    
    Attributes:
        capacity (int): Maximum number of key-value pairs the cache can retain.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer.")
        self.capacity: int = capacity
        self.cache: dict[Any, Node] = {}

        # Sentinel pseudo-nodes: eliminate boundary checks during unlinking/insertion
        self.head: Node = Node(0, 0)
        self.tail: Node = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        """Unlink an existing node from its current position in O(1) time."""
        prev_node = node.prev
        next_node = node.next
        if prev_node and next_node:
            prev_node.next = next_node
            next_node.prev = prev_node

    def _add_to_front(self, node: Node) -> None:
        """Insert a node immediately following the sentinel head (MRU position) in O(1) time."""
        node.prev = self.head
        node.next = self.head.next
        if self.head.next:
            self.head.next.prev = node
        self.head.next = node

    def get(self, key: Any) -> Any:
        """Retrieve the value mapped to `key`, or return -1 if not present.
        
        Promotes the accessed key to the most recently used (MRU) position.
        
        Complexity:
            Time: O(1) average.
            Space: O(1).
        """
        if key not in self.cache:
            return -1

        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key: Any, value: Any) -> None:
        """Insert or update a key-value pair.
        
        If the cache exceeds capacity, the least recently used item (immediately
        preceding the sentinel tail) is evicted.
        
        Complexity:
            Time: O(1) average.
            Space: O(1) auxiliary per call; O(capacity) total.
        """
        if key in self.cache:
            self._remove(self.cache[key])
            del self.cache[key]

        new_node = Node(key, value)
        self._add_to_front(new_node)
        self.cache[key] = new_node

        if len(self.cache) > self.capacity:
            lru_node = self.tail.prev
            if lru_node and lru_node != self.head:
                self._remove(lru_node)
                del self.cache[lru_node.key]

    def __len__(self) -> int:
        return len(self.cache)

    def __contains__(self, key: Any) -> bool:
        return key in self.cache


class ThreadSafeLRUCache(LRUCache):
    """Thread-safe variant of `LRUCache` protected by a mutual exclusion lock.
    
    Note on design:
        Because `get()` in an LRU cache modifies internal node pointers to record
        recency, it is fundamentally a mutating write operation. Consequently,
        coarse-grained mutual exclusion ensures correctness without the false
        promise of standard read-write locks.
    """

    def __init__(self, capacity: int):
        super().__init__(capacity)
        self._lock: threading.Lock = threading.Lock()

    def get(self, key: Any) -> Any:
        with self._lock:
            return super().get(key)

    def put(self, key: Any, value: Any) -> None:
        with self._lock:
            return super().put(key, value)

    def __len__(self) -> int:
        with self._lock:
            return super().__len__()
