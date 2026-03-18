from __future__ import annotations

import json
from pathlib import Path
from typing import Any


Record = dict[str, Any]


class StudentRecordSystem:
    """In-memory record manager backed by JSON persistence.

    Data structures:
    - list: stores all student records
    - dict (hash table): maps student_id -> index in list
    """

    def __init__(self, storage_path: str | Path | None = None) -> None:
        default_path = Path(__file__).resolve().parent.parent / "data" / "student_records.json"
        self.storage_path = Path(storage_path or default_path)
        self.records: list[Record] = []
        self.id_index: dict[int, int] = {}
        self.load()

    def load(self) -> None:
        if self.storage_path.exists():
            with self.storage_path.open("r", encoding="utf-8") as handle:
                loaded = json.load(handle)
                if isinstance(loaded, list):
                    self.records = [self._normalize_record(record) for record in loaded if isinstance(record, dict)]
                else:
                    self.records = []
        else:
            self.records = []
        self._rebuild_index()

    def save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self.storage_path.open("w", encoding="utf-8") as handle:
            json.dump(self.records, handle, indent=2)

    def _normalize_record(self, record: Record) -> Record:
        return {
            "student_id": int(record["student_id"]),
            "name": str(record["name"]).strip(),
            "course": str(record["course"]).strip(),
            "cwa": float(record["cwa"]),
        }

    def _rebuild_index(self) -> None:
        self.id_index = {}
        deduplicated: list[Record] = []
        for record in self.records:
            student_id = int(record["student_id"])
            if student_id in self.id_index:
                continue
            self.id_index[student_id] = len(deduplicated)
            deduplicated.append(record)
        self.records = deduplicated

    def _validate_name(self, name: str) -> str:
        cleaned = name.strip()
        if not cleaned:
            raise ValueError("Student name is required.")
        return cleaned

    def _validate_course(self, course: str) -> str:
        cleaned = course.strip()
        if not cleaned:
            raise ValueError("Course is required.")
        return cleaned

    def _validate_cwa(self, cwa: float) -> float:
        value = float(cwa)
        if value < 0 or value > 100:
            raise ValueError("CWA/GPA must be between 0 and 100.")
        return value

    def add_student(self, *, student_id: int, name: str, course: str, cwa: float) -> None:
        student_id = int(student_id)
        if student_id in self.id_index:
            raise ValueError("A student with that ID already exists.")

        record = {
            "student_id": student_id,
            "name": self._validate_name(name),
            "course": self._validate_course(course),
            "cwa": self._validate_cwa(cwa),
        }
        self.records.append(record)
        self.id_index[student_id] = len(self.records) - 1
        self.save()

    def update_student(self, *, student_id: int, name: str, course: str, cwa: float) -> None:
        student_id = int(student_id)
        index = self.id_index.get(student_id)
        if index is None:
            raise ValueError("Student ID not found.")

        self.records[index]["name"] = self._validate_name(name)
        self.records[index]["course"] = self._validate_course(course)
        self.records[index]["cwa"] = self._validate_cwa(cwa)
        self.save()

    def delete_student(self, *, student_id: int) -> None:
        student_id = int(student_id)
        index = self.id_index.get(student_id)
        if index is None:
            raise ValueError("Student ID not found.")

        self.records.pop(index)
        self._rebuild_index()
        self.save()

    def list_students(self) -> list[Record]:
        return [record.copy() for record in self.records]

    def hash_lookup_by_id(self, student_id: int) -> tuple[Record | None, int]:
        student_id = int(student_id)
        index = self.id_index.get(student_id)
        if index is None:
            return None, 1
        return self.records[index].copy(), 1

    def linear_search_by_id(self, student_id: int) -> tuple[Record | None, int]:
        target = int(student_id)
        comparisons = 0
        for record in self.records:
            comparisons += 1
            if int(record["student_id"]) == target:
                return record.copy(), comparisons
        return None, comparisons

    def linear_search_by_name(self, name: str) -> tuple[list[Record], int]:
        query = name.strip().lower()
        comparisons = 0
        matches: list[Record] = []

        if not query:
            return [], 0

        for record in self.records:
            comparisons += 1
            if query in str(record["name"]).lower():
                matches.append(record.copy())
        return matches, comparisons

    def binary_search_by_id(self, student_id: int) -> tuple[Record | None, int]:
        target = int(student_id)
        ordered, _ = self.merge_sort(by="student_id", reverse=False)

        low = 0
        high = len(ordered) - 1
        comparisons = 0

        while low <= high:
            mid = (low + high) // 2
            comparisons += 1
            mid_value = int(ordered[mid]["student_id"])
            if mid_value == target:
                return ordered[mid].copy(), comparisons
            if mid_value < target:
                low = mid + 1
            else:
                high = mid - 1
        return None, comparisons

    def sort_students(self, *, by: str, algorithm: str, reverse: bool = False) -> tuple[list[Record], int]:
        if by not in {"name", "cwa", "student_id"}:
            raise ValueError("Sort key must be one of: name, cwa, student_id.")
        if algorithm == "bubble":
            return self.bubble_sort(by=by, reverse=reverse)
        if algorithm == "insertion":
            return self.insertion_sort(by=by, reverse=reverse)
        if algorithm == "merge":
            return self.merge_sort(by=by, reverse=reverse)
        raise ValueError("Sort algorithm must be bubble, insertion, or merge.")

    def _to_sort_value(self, record: Record, by: str) -> str | float | int:
        value = record[by]
        if by == "name":
            return str(value).lower()
        return value

    def _in_correct_order(self, left: Record, right: Record, by: str, reverse: bool) -> bool:
        left_value = self._to_sort_value(left, by)
        right_value = self._to_sort_value(right, by)
        if reverse:
            return left_value >= right_value
        return left_value <= right_value

    def bubble_sort(self, *, by: str, reverse: bool = False) -> tuple[list[Record], int]:
        items = [record.copy() for record in self.records]
        comparisons = 0
        n = len(items)

        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                comparisons += 1
                if not self._in_correct_order(items[j], items[j + 1], by, reverse):
                    items[j], items[j + 1] = items[j + 1], items[j]
                    swapped = True
            if not swapped:
                break
        return items, comparisons

    def insertion_sort(self, *, by: str, reverse: bool = False) -> tuple[list[Record], int]:
        items = [record.copy() for record in self.records]
        comparisons = 0

        for i in range(1, len(items)):
            current = items[i]
            j = i - 1

            while j >= 0:
                comparisons += 1
                if self._in_correct_order(items[j], current, by, reverse):
                    break
                items[j + 1] = items[j]
                j -= 1
            items[j + 1] = current
        return items, comparisons

    def merge_sort(self, *, by: str, reverse: bool = False) -> tuple[list[Record], int]:
        items = [record.copy() for record in self.records]
        sorted_records, comparisons = self._merge_sort_recursive(items, by, reverse)
        return sorted_records, comparisons

    def _merge_sort_recursive(self, items: list[Record], by: str, reverse: bool) -> tuple[list[Record], int]:
        if len(items) <= 1:
            return items, 0

        midpoint = len(items) // 2
        left, left_comparisons = self._merge_sort_recursive(items[:midpoint], by, reverse)
        right, right_comparisons = self._merge_sort_recursive(items[midpoint:], by, reverse)

        merged: list[Record] = []
        i = 0
        j = 0
        comparisons = left_comparisons + right_comparisons

        while i < len(left) and j < len(right):
            comparisons += 1
            if self._in_correct_order(left[i], right[j], by, reverse):
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1

        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged, comparisons

