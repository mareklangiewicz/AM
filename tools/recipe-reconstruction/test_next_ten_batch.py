"""Exercise the next ten recipes through the retained batch verification seam."""
import test_large_batch


class NextTenBatch(test_large_batch.LargeBatch):
    receipt_path = test_large_batch.RESEARCH/'next-ten-evidence.json'
