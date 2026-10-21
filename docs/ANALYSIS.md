# Systems Design & Algorithmic Analysis

**Candidate:** Aaryav Chaudhary  
**Assessment:** Data Structures & Systems Design  
**Target Role:** AI / Multi-Agent Systems Intern — Avaloka (Guruvai Sciences)

---

## 1. Time & Space Complexity

### LRU Cache (`LRUCache`)

| Operation | Time Complexity | Space Complexity |
|---|:---:|:---:|
| `__init__(capacity)` | $O(1)$ | $O(\text{capacity})$ |
| `get(key)` | $O(1)$ | $O(1)$ |
| `put(key, value)` | $O(1)$ | $O(1)$ amortized |

**Analysis:**
- **Key Lookups**: The hash map (`dict`) provides expected $O(1)$ retrieval and mutation.
- **Node Reordering**: Unlinking and reattaching nodes at the sentinel head requires updating 4 pointers, executing in deterministic $O(1)$ time without traversal.
- **Eviction**: Removing the node at `tail.prev` and deleting its hash entry is strictly $O(1)$.
- **Space Complexity**: The auxiliary space is bounded by $O(\text{capacity})$ to store up to `capacity` doubly linked list `Node` instances and corresponding hash map references.

---

### Event Scheduler (`event_scheduler.py`)

| Function | Time Complexity | Space Complexity |
|---|:---:|:---:|
| `can_attend_all(events)` | $O(n \log n)$ | $O(n)$ |
| `min_rooms_required(events)` | $O(n \log n)$ | $O(n)$ |
| `assign_rooms(events)` | $O(n \log n)$ | $O(n)$ |

**Analysis:**
- **Sorting Bottleneck**: For all functions, the computational ceiling is determined by sorting intervals or boundary points in $O(n \log n)$ using Timsort.
- **Linear Passes**:
  - `can_attend_all`: Once sorted, a single $O(n)$ linear scan verifies non-overlapping bounds.
  - `min_rooms_required`: After sorting $2n$ points, the sweep-line aggregates concurrency in $O(n)$ time.
  - `assign_rooms`: Processing $n$ events through the min-heap performs at most $n$ insertions and $n$ deletions, yielding $O(n \log k)$ where $k \le n$ is the maximum concurrent rooms.
- **Space Overhead**: $O(n)$ auxiliary memory to maintain sorted copies and event timeline structures.

---

## 2. Architectural Trade-offs: Why HashMap + Doubly Linked List?

Implementing an LRU cache requires satisfying two concurrent constraints in $O(1)$ time:
1. Fast random lookup by key.
2. Fast positional mutation to maintain strict temporal recency.

Evaluating alternative data structures reveals why the composite approach is optimal:

| Structure | Lookup | Eviction / Promotion | Reason for Rejection |
|---|:---:|:---:|---|
| **Hash Map Alone** | $O(1)$ | $O(n)$ | Unordered; locating the least recently accessed item requires a full linear scan of timestamps. |
| **Array / Dynamic List** | $O(n)$ | $O(n)$ | Maintaining order is possible, but promoting an accessed item to the front requires shifting elements ($O(n)$). |
| **Singly Linked List** | $O(n)$ | $O(n)$ | Unlinking an arbitrary node requires finding its predecessor, which mandates an $O(n)$ traversal from the head. |
| **Hash Map + Doubly Linked List** | **$O(1)$** | **$O(1)$** | **Optimal**: Hash map maps keys to node pointers; bidirectional pointers (`prev`/`next`) enable $O(1)$ extraction and re-insertion without traversal. |

### The Trade-off
We accept an auxiliary memory trade-off: each node carries two extra pointer fields (`prev` and `next`), and the hash map duplicates key storage. In high-throughput caching tiers, trading modest memory overhead to eliminate latency spikes on hot read/write paths is the industry-standard choice.

---

## 3. Future-Proofing: Stateful Room Assignment

To progress from determining the peak room requirement to assigning explicit room names (e.g., `"Room A"`, `"Room B"`):

### Algorithm: Greedy Min-Heap Allocation
1. **Index Annotation**: Pair events with their original indices to ensure results match input ordering.
2. **Chronological Sorting**: Sort events by start time.
3. **Priority Queue State**: Maintain a min-heap storing `(end_time, room_identifier)` tuples, ordered by the earliest release time.
4. **Reclamation & Reuse**:
   - For an event starting at $T_{\text{start}}$, pop all rooms from the heap where $\text{end\_time} \le T_{\text{start}}$ and return their labels to an `available_rooms` pool.
   - If `available_rooms` is non-empty, reuse the most recently liberated room (minimizing total room proliferation).
   - If no room is free, instantiate a new label (`Room A`, `Room B`, ...).
   - Push `(event.end, room_identifier)` back into the heap.

```python
import heapq

def assign_rooms(events):
    if not events:
        return []

    indexed = sorted(enumerate(events), key=lambda x: x[1][0])
    assignments = [None] * len(events)
    room_counter = 0
    available_rooms = []
    occupied = []  # (end_time, room_name)

    for orig_idx, (start, end) in indexed:
        while occupied and occupied[0][0] <= start:
            _, freed_room = heapq.heappop(occupied)
            available_rooms.append(freed_room)

        if available_rooms:
            room = available_rooms.pop()
        else:
            room = f"Room {chr(65 + room_counter)}"
            room_counter += 1

        assignments[orig_idx] = room
        heapq.heappush(occupied, (end, room))

    return [(events[i], assignments[i]) for i in range(len(events))]
```

---

## 4. Concurrency: Thread-Safe LRU Cache Architecture

In concurrent applications, unguarded operations on an LRU cache produce fatal race conditions:
- **Pointer Corruption**: Simultaneous node extractions corrupt `prev` and `next` references, creating orphaned cycles or memory leaks.
- **Hash Table Collisions**: Concurrent writes cause lost updates or stale key-to-node pointers.
- **Capacity Drift**: Multiple threads evicting concurrently can decrement cache size below zero or exceed capacity bounds.

### Concurrency Strategies

1. **Coarse-Grained Mutex (Implemented)**:
   - Synchronize all public entry points (`get` and `put`) via `threading.Lock`.
   - **Trade-off**: High simplicity and zero race conditions. Contention can become a bottleneck under extreme concurrent loads.

2. **The Read-Write Lock Fallacy in LRU**:
   - Many developers assume an `RWLock` solves cache contention by allowing multiple readers.
   - **Critical Caveat**: In an LRU cache, `get()` **is a mutating write operation** because it unlinks and repoints nodes to maintain recency. Thus, an `RWLock` still forces exclusive locking on every read, providing no concurrency gain over a mutex.

3. **Production High-Throughput Patterns**:
   - **Cache Sharding**: Partition the keyspace across $N$ independent `LRUCache` instances using consistent hashing (e.g., `hash(key) % N`). This reduces lock contention by an order of magnitude.
   - **Read Buffering (Guava / Caffeine Architecture)**: `get()` only reads from the hash map under a shared lock and appends the access event to a lock-free ring buffer. A dedicated maintenance thread asynchronously drains the buffer to reorder the linked list in batches.
