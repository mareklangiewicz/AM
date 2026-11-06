"""Replay the next ten sources from their exact former enrollment scope."""
import test_large_batch_enrollment


class NextTenEnrollment(test_large_batch_enrollment.LargeBatchEnrollment):
    receipt_name = 'next-ten-evidence.json'
    baseline_revision = '10a4c03eca229434a346fb3e3303f19621484a80'
