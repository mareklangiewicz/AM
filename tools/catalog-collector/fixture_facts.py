"""Shared helper for offline fixture loaders."""
from datetime import datetime


def utc(value):
    return datetime.fromisoformat(value)
