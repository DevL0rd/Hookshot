"""Summarize bounded submitted-read diagnostics from one process log.

Cumulative per-thread counters cover only complete reporting batches; they are
not frame timings. Never concatenate different process logs for this analysis.
"""
import argparse
import json
import re
from pathlib import Path

MARKER = 'vk: submitted-read counters cumulative-thread '


def analyze(lines):
    streams = {}
    reports = 0
    for line in lines:
        if MARKER not in line:
            continue
        values = {key: int(value) for key, value in
                  re.findall(r'(\w+)=(\d+)', line.split(MARKER, 1)[1])}
        stream = values.pop('stream')
        previous = streams.get(stream)
        if previous and any(values[key] < previous[key] for key in previous):
            raise ValueError('Counters decreased: input must contain one process only')
        streams[stream] = values
        reports += 1
    totals = {}
    for values in streams.values():
        for key, value in values.items():
            totals[key] = totals.get(key, 0) + value
    misses = sum(totals.get(key, 0) for key in
                 ('empty', 'collision', 'view_changed', 'stamp_changed'))
    return {
        'reports': reports, 'streams': len(streams), 'totals': totals,
        'single_page_misses': misses,
        'collision_fraction_of_misses': totals.get('collision', 0) / misses if misses else None,
        'refill_bytes_per_requested_byte': (
            totals.get('refill_bytes', 0) / totals['requested_bytes']
            if totals.get('requested_bytes') else None),
        'report_limit_reached': reports >= 256,
        'proof': 'Complete cumulative batches only; trailing reads omitted. '
                 'Miss reasons are exclusive, ordered empty/collision/view/stamp. '
                 'Counters measure traffic, not CPU or GPU time.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    args = parser.parse_args()
    with args.log.open(errors='replace') as lines:
        print(json.dumps(analyze(lines), indent=2))
