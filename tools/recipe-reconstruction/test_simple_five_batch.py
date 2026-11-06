"""Reuse the maintained exact-source, selector and inert lifecycle batch gates."""
import test_large_batch


class SimpleFive(test_large_batch.LargeBatch):
    receipt_path = test_large_batch.RESEARCH/'simple-five-evidence.json'
