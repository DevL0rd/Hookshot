# Playthrough fixes

This branch uses the accepted main snapshot plus one pending PR, #1377, and the existing local texture-quality opt-in policy. Passing source checks alone does not establish a performance improvement.

Base: `8c359bca1192d9c68d802bc99163be3b70156265`. The original `NotRexed/Hookshot` GitHub repository returned 404 over Git HTTPS, Git SSH and the API on 2026-11-13. The user accepted the snapshot from [the mirror](https://issues.sakul-flee.de/Mirrors/Hookshot), which reports synchronization on 2026-11-13. It contains 148 commits beyond the previous base `ef81aee767f848255ca08171bba33b8c40c79347`. This identifies the accepted snapshot; it does not assert that it is current official upstream.

## Remaining pending PR

| PR | Purpose | Integration and evidence limits |
|---|---|---|
| [#1377](https://github.com/NotRexed/Hookshot/pull/1377) | Prefer hot memory pools for VRAM mirrors | Adapt the selected head `59edbbe50200e595f3977145cefff282e3522f00` to newer upstream pool management. Keep GPU-only and GPU-written mirrors protected, inherited flags, smaller imports, live-pool trimming and mirror-keep behavior. Prior real-game evidence showed reduced memory traffic and synchronization; no FPS improvement is established on this Linux laptop. |

## Changes now supplied by main

The snapshot supplies the four other previously retained PRs, so no separate fork patch is reapplied:

- #2306: native NVIDIA float atomic adds (`de819234`).
- #2093: correct day-clock progression above 60 FPS (`f0c40fc9`).
- #2540: keep builder-launched Linux games in their own scope (`50c81bb8`), with upstream handoff correction `bc0ecd84`.
- #2575: honor disabled high-FPS logging switches (`7dfb853b`).

Previously removed PRs #2114, #2134 and #2545 have also landed in the accepted snapshot. Their upstream implementations are included as part of the new base; old fork removals must not erase them. #1541, #1946, #2433 and #2487 remain excluded as separate pending bundles. Independent upstream fixes are preserved even where they address related areas.

## Texture-quality policy

The existing local adjustment for upstream #1009 remains: additional low-VRAM texture reduction is explicit opt-in with `RX_VK_LOW_VRAM_MIPS=1`. Unset or disabled values preserve previous texture limits. Keep upstream's Minimum and new Auto-preset-at-Minimum eligibility and its nonzero budget at or below 4.5 GiB; this fork does not apply additional mip cuts automatically. This is a local policy adjustment, not another pending PR.

## Updating this branch

Exact source inputs, upstreamed changes and historical removals are recorded in [playthrough-prs.json](playthrough-prs.json). Preserve published history while reconstructing from the selected main tree plus still-needed deltas. Historical merge ancestry alone cannot show whether a previously removed implementation is present.

## Validation

Refresh verification is in progress. The installed game remains the previously verified `af7ffa0740b97209ac3af43045fe142e19ae8394` runtime. Updating this Git branch does not install a new game build, alter saves/settings/caches, or establish a gameplay performance change.
