"""
Event Scheduler Implementation
==============================
Provides algorithms for calendar conflict detection, minimum concurrent
room capacity calculation, and stateful room assignment.

Includes:
- `can_attend_all`: Determines whether intervals are pairwise disjoint.
- `min_rooms_required`: Finds the peak concurrency via a timeline sweep.
- `assign_rooms`: Greedily assigns specific room identifiers using a min-heap.
"""

import heapq
from typing import List, Tuple, Optional


def can_attend_all(events: List[Tuple[int, int]]) -> bool:
    """Determine whether a single attendee can attend all events without conflicts.
    
    Adjacent events (where an end time equals a start time) are valid and do not
    constitute a collision.
    
    Algorithm:
        1. Sort events chronologically by start time: O(n log n).
        2. Linearly scan consecutive pairs to verify whether any event begins
           strictly before the previous one concludes: O(n).
           
    Args:
        events: List of (start, end) time intervals.
        
    Returns:
        True if all events can be attended without overlap, False otherwise.
        
    Complexity:
        Time: O(n log n) due to sorting.
        Space: O(n) for the sorted list.
    """
    if len(events) <= 1:
        return True

    sorted_events = sorted(events, key=lambda e: e[0])

    for i in range(1, len(sorted_events)):
        prev_end = sorted_events[i - 1][1]
        curr_start = sorted_events[i][0]

        # Strict inequality: adjacent intervals (e.g. 10 == 10) are valid
        if curr_start < prev_end:
            return False

    return True


def min_rooms_required(events: List[Tuple[int, int]]) -> int:
    """Calculate the minimum number of meeting rooms required to host all events.
    
    Algorithm (Sweep-Line):
        1. Decompose each interval into two discrete events:
           - (start, +1): meeting begins, consuming one room.
           - (end, -1): meeting concludes, liberating one room.
        2. Sort timeline chronologically. If an end time and start time coincide,
           process the conclusion (-1) before the start (+1). This ensures that
           consecutive back-to-back meetings reuse the liberated room.
        3. Sweep chronologically, tracking cumulative active rooms and recording
           the global peak.
           
    Args:
        events: List of (start, end) time intervals.
        
    Returns:
        The peak number of rooms concurrently occupied.
        
    Complexity:
        Time: O(n log n) due to sorting 2n boundary points.
        Space: O(n) auxiliary space for the timeline.
    """
    if not events:
        return 0

    timeline: List[Tuple[int, int]] = []
    for start, end in events:
        timeline.append((start, 1))
        timeline.append((end, -1))

    # Sort primarily by timestamp; secondarily by event delta (-1 before +1)
    timeline.sort(key=lambda pt: (pt[0], pt[1]))

    active_rooms: int = 0
    peak_rooms: int = 0

    for _, delta in timeline:
        active_rooms += delta
        if active_rooms > peak_rooms:
            peak_rooms = active_rooms

    return peak_rooms


def assign_rooms(events: List[Tuple[int, int]]) -> List[Tuple[Tuple[int, int], str]]:
    """Assign specific room identifiers (e.g., 'Room A', 'Room B') to each event.
    
    Algorithm (Priority Queue / Min-Heap):
        1. Preserve input ordering by annotating events with their original index.
        2. Sort events chronologically by start time.
        3. Maintain a min-heap storing (end_time, room_identifier) tuples.
        4. When scheduling an event, reclaim any rooms whose end time <= current start,
           returning their labels to an available pool.
        5. Assign a label from the pool (reusing earliest freed) or instantiate
           a new label if no rooms are currently free.
           
    Args:
        events: List of (start, end) time intervals.
        
    Returns:
        List of ((start, end), "Room X") pairs matching original input order.
        
    Complexity:
        Time: O(n log n).
        Space: O(n).
    """
    if not events:
        return []

    # Track original indices to restore order in output
    indexed_events = sorted(enumerate(events), key=lambda x: x[1][0])
    assignments: List[Optional[str]] = [None] * len(events)

    room_counter: int = 0
    available_rooms: List[str] = []
    occupied_heap: List[Tuple[int, str]] = []  # (end_time, room_name)

    for orig_idx, (start, end) in indexed_events:
        # Reclaim rooms whose meetings have finished
        while occupied_heap and occupied_heap[0][0] <= start:
            _, freed_room = heapq.heappop(occupied_heap)
            available_rooms.append(freed_room)

        # Allocate from pool or generate new room label
        if available_rooms:
            room = available_rooms.pop()
        else:
            room = f"Room {chr(65 + room_counter)}"
            room_counter += 1

        assignments[orig_idx] = room
        heapq.heappush(occupied_heap, (end, room))

    return [(events[i], assignments[i]) for i in range(len(events))]
