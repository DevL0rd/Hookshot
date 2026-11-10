"""Cumulative thread reports must not be double-counted or mixed across runs."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    'diagnostics', Path(__file__).resolve().parents[1] / 'scripts/analyze_submitted_reads.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
def row(stream, calls):
    return (module.MARKER + f'stream={stream} calls={calls} requested_bytes={calls*4} '
            f'collision={calls//2} empty=0 view_changed=0 stamp_changed=0 refill_bytes={calls*4096}')
result = module.analyze(['unrelated', row(1, 65536), row(2, 65536), row(1, 131072)])
assert result['totals']['calls'] == 196608
assert result['streams'] == 2 and result['reports'] == 3
assert result['refill_bytes_per_requested_byte'] == 1024
assert result['collision_fraction_of_misses'] == 1
assert not result['report_limit_reached']
assert module.analyze([])['refill_bytes_per_requested_byte'] is None
try:
    module.analyze([row(1, 131072), row(1, 65536)])
except ValueError:
    pass
else:
    raise AssertionError('mixed process counters accepted')
print('PASS: cumulative aggregation, independent streams, empty input, reset rejection')
