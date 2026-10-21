# Avaloka Systems: Data Structures & Systems Design

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 28 Passed](https://img.shields.io/badge/tests-28%20passed-brightgreen.svg)]()

Technical assessment repository for the **AI / Multi-Agent Systems Intern** role at **Avaloka (Guruvai Sciences)**.

Contains modular, production-ready implementations of:
1. **$O(1)$ LRU Cache** via composite Hash Map & Doubly Linked List.
2. **Event Scheduler** with overlap detection and sweep-line minimum room calculation.
3. **Systems Extensions**: Priority queue room assignment and thread-safe cache wrapper.
4. **Comprehensive Test Suite**: 28 unit tests covering all operational bounds and edge cases.

---

## Repository Structure

```
avaloka-systems/
├── docs/
│   ├── ANALYSIS.md              # Detailed design & complexity discussion
│   └── Aaryav_Chaudhary_Avaloka_Assignment.pdf  # Final submission document
├── src/
│   ├── __init__.py
│   ├── lru_cache.py             # LRUCache & ThreadSafeLRUCache implementations
│   └── event_scheduler.py       # can_attend_all, min_rooms_required, assign_rooms
├── tests/
│   ├── __init__.py
│   ├── test_lru_cache.py        # 10 unit tests (eviction, order, concurrency)
│   └── test_event_scheduler.py  # 18 unit tests (adjacent, nested, room reuse)
├── .gitignore
└── README.md
```

---

## 1. Problem Overview & Solutions

### Problem 1: Least Recently Used (LRU) Cache
- **Requirement**: `get(key)` and `put(key, value)` executing in strict $O(1)$ average time with fixed capacity eviction.
- **Architecture**:
  - **Hash Map** (`dict`): Maps keys directly to internal doubly linked list `Node` instances.
  - **Doubly Linked List**: Bidirectional pointers (`prev`/`next`) enable $O(1)$ node detachment from anywhere in the list and re-insertion at the most recently used (MRU) sentinel head.
  - **Sentinel Nodes**: Permanent pseudo-head and pseudo-tail eliminate conditional branching on empty/single-element bounds.
- **Thread Safety**: `ThreadSafeLRUCache` provides coarse-grained mutual exclusion via `threading.Lock`.

```python
from src.lru_cache import LRUCache

cache = LRUCache(2)
cache.put(1, 10)
cache.put(2, 20)
assert cache.get(1) == 10      # returns 10, marks 1 as MRU
cache.put(3, 30)               # evicts key 2 (least recently used)
assert cache.get(2) == -1      # returns -1 (evicted)
```

---

### Problem 2: Event Scheduler
- **`can_attend_all(events)`**:
  - Sorts intervals chronologically by start time ($O(n \log n)$).
  - Performs a single linear scan ($O(n)$) comparing `current.start < previous.end`.
  - Enforces strict inequality: adjacent intervals (e.g., $(9, 10)$ and $(10, 11)$) are valid and do not collide.
- **`min_rooms_required(events)`**:
  - Models peak concurrent intervals via a **sweep-line algorithm**.
  - Splits each interval into discrete transition points: `(start, +1)` and `(end, -1)`.
  - Chronological sort processes releases (`-1`) before allocations (`+1`) at identical timestamps, ensuring back-to-back meetings seamlessly reuse rooms.
  - Single pass accumulates running concurrency; the peak value is the answer.

```python
from src.event_scheduler import can_attend_all, min_rooms_required

events = [(9, 10), (10, 11), (11, 12)]
assert can_attend_all(events) is True
assert min_rooms_required(events) == 1

overlapping = [(1, 4), (2, 5), (3, 6)]
assert can_attend_all(overlapping) is False
assert min_rooms_required(overlapping) == 3
```

---

### Systems Extension: Stateful Room Assignment
- **`assign_rooms(events)`**:
  - Uses a **min-heap priority queue** storing `(end_time, room_label)` ordered by earliest availability.
  - Reclaims rooms whose meetings have finished into a reusable pool.
  - Minimizes room count while returning specific labels (`"Room A"`, `"Room B"`).

---

## 2. Complexity Analysis Summary

| Component | Function / Method | Time Complexity | Auxiliary Space | Bottleneck |
|---|---|:---:|:---:|---|
| **LRU Cache** | `LRUCache.get` | $O(1)$ | $O(1)$ | Hash lookup & pointer re-link |
| | `LRUCache.put` | $O(1)$ | $O(\text{capacity})$ | Hash insert & tail eviction |
| **Scheduler** | `can_attend_all` | $O(n \log n)$ | $O(n)$ | Timsort on start times |
| | `min_rooms_required` | $O(n \log n)$ | $O(n)$ | Timsort on $2n$ boundary points |
| | `assign_rooms` | $O(n \log n)$ | $O(n)$ | Min-heap operations |

Detailed trade-off comparisons and concurrency architecture analyses are documented in [docs/ANALYSIS.md](docs/ANALYSIS.md).

---

## 3. Running Unit Tests

The test suite uses Python's standard library `unittest` and requires no external dependencies.

```bash
# Clone the repository
git clone https://github.com/Aaryav1130/avaloka-systems.git
cd avaloka-systems

# Run all test suites
python -m unittest discover -s tests -v
```

### Expected Output
```
test_basic_put_and_get (test_lru_cache.TestLRUCache) ... ok
test_eviction_order_on_capacity (test_lru_cache.TestLRUCache) ... ok
test_get_promotes_key_recency (test_lru_cache.TestLRUCache) ... ok
test_adjacent_events_no_conflict (test_event_scheduler.TestCanAttendAll) ... ok
test_adjacent_events_reuse_single_room (test_event_scheduler.TestMinRoomsRequired) ... ok
test_complex_reuse_pattern (test_event_scheduler.TestAssignRooms) ... ok
test_concurrent_read_write (test_lru_cache.TestThreadSafeLRUCache) ... ok
...
Ran 28 tests in 0.007s

OK
```

---

## 4. Author

**Aaryav Chaudhary**  
- **GitHub**: [@Aaryav1130](https://github.com/Aaryav1130)  
- **Target Role**: AI / Multi-Agent Systems Intern — Avaloka (Guruvai Sciences)
