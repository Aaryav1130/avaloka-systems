"""
Unit tests for Event Scheduler functions: can_attend_all, min_rooms_required, assign_rooms.
"""

import unittest
from src.event_scheduler import can_attend_all, min_rooms_required, assign_rooms


class TestCanAttendAll(unittest.TestCase):
    def test_empty_and_single_event(self):
        self.assertTrue(can_attend_all([]))
        self.assertTrue(can_attend_all([(9, 10)]))

    def test_strictly_disjoint_events(self):
        self.assertTrue(can_attend_all([(9, 10), (11, 12), (13, 14)]))

    def test_adjacent_events_no_conflict(self):
        # Crucial edge case: (9, 10) and (10, 11) do NOT overlap
        self.assertTrue(can_attend_all([(9, 10), (10, 11), (11, 12)]))

    def test_unsorted_adjacent_events(self):
        self.assertTrue(can_attend_all([(11, 12), (9, 10), (10, 11)]))

    def test_overlapping_events(self):
        self.assertFalse(can_attend_all([(9, 11), (10, 12)]))

    def test_nested_event_overlap(self):
        self.assertFalse(can_attend_all([(9, 15), (10, 12)]))

    def test_identical_intervals(self):
        self.assertFalse(can_attend_all([(9, 10), (9, 10)]))


class TestMinRoomsRequired(unittest.TestCase):
    def test_empty_events(self):
        self.assertEqual(min_rooms_required([]), 0)

    def test_single_event(self):
        self.assertEqual(min_rooms_required([(9, 10)]), 1)

    def test_sequential_disjoint_events(self):
        self.assertEqual(min_rooms_required([(9, 10), (11, 12), (13, 14)]), 1)

    def test_adjacent_events_reuse_single_room(self):
        # Back-to-back meetings reuse the same room
        self.assertEqual(min_rooms_required([(9, 10), (10, 11), (11, 12)]), 1)

    def test_all_overlapping_events(self):
        self.assertEqual(min_rooms_required([(9, 10), (9, 10), (9, 10)]), 3)

    def test_partial_concurrency(self):
        events = [(1, 4), (2, 5), (3, 6), (7, 8)]
        # At time 3.5: (1,4), (2,5), (3,6) all active -> 3 rooms
        self.assertEqual(min_rooms_required(events), 3)

    def test_two_consecutive_overlapping_clusters(self):
        # (1,3) & (2,4) need 2 rooms; then (5,7) & (6,8) need 2 rooms. Peak = 2
        events = [(1, 3), (2, 4), (5, 7), (6, 8)]
        self.assertEqual(min_rooms_required(events), 2)

    def test_unsorted_intervals(self):
        events = [(7, 8), (1, 4), (3, 6), (2, 5)]
        self.assertEqual(min_rooms_required(events), 3)


class TestAssignRooms(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual(assign_rooms([]), [])

    def test_adjacent_events_reuse_room(self):
        events = [(9, 10), (10, 11), (11, 12)]
        assignments = assign_rooms(events)
        # All three should be assigned to the same room (e.g. Room A)
        room_names = [room for _, room in assignments]
        self.assertEqual(len(set(room_names)), 1)
        self.assertEqual(room_names[0], "Room A")

    def test_overlapping_events_receive_different_rooms(self):
        events = [(9, 11), (10, 12)]
        assignments = assign_rooms(events)
        room_names = [room for _, room in assignments]
        self.assertEqual(len(set(room_names)), 2)
        self.assertIn("Room A", room_names)
        self.assertIn("Room B", room_names)

    def test_complex_reuse_pattern(self):
        # (1, 4) in Room A
        # (2, 5) in Room B
        # (4, 6) can reuse Room A because (1, 4) finished at 4
        events = [(1, 4), (2, 5), (4, 6)]
        assignments = assign_rooms(events)
        room_map = dict(assignments)
        self.assertEqual(room_map[(1, 4)], "Room A")
        self.assertEqual(room_map[(2, 5)], "Room B")
        self.assertEqual(room_map[(4, 6)], "Room A")


if __name__ == "__main__":
    unittest.main()
