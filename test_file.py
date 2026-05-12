"""Test file for VibeDoc."""
import os
from typing import List


class DataProcessor:
    """Processes lists of numbers."""

    def __init__(self, name: str):
        self.name = name
        self.data: List[int] = []

    def add(self, value: int) -> None:
        """Add a value to the data list."""
        self.data.append(value)

    def get_sum(self) -> int:
        """Return the sum of all values."""
        return sum(self.data)

    def get_average(self) -> float:
        """Return the average of all values."""
        if not self.data:
            return 0.0
        return sum(self.data) / len(self.data)


def process_file(filepath: str) -> DataProcessor:
    """Read a file and process its contents."""
    proc = DataProcessor(filepath)

    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                try:
                    proc.add(int(line.strip()))
                except ValueError:
                    pass

    return proc