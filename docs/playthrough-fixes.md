# Playthrough fixes

This branch combines official upstream main with a small set of pending changes supported by concrete gameplay evidence or a reproducible validated bug fix. Passing source checks alone is not evidence of a performance improvement.

Official upstream base: `ef81aee767f848255ca08171bba33b8c40c79347` (2026-11-12). Exact inputs, historical merge provenance, removals and integration policy are in [playthrough-prs.json](playthrough-prs.json).

## Retained pending changes

| PR | Purpose | Evidence and limits |
|---|---|---|
| [#1377](https://github.com/NotRexed/Hookshot/pull/1377) | Prefer hot memory pools for VRAM mirrors | Real-game traffic and memory-sync reduction; reviewed safety corrections. No measured FPS gain on this Linux laptop. |
| [#2306](https://github.com/NotRexed/Hookshot/pull/2306) | Native NVIDIA float atomic adds | RTX4090 game A/B reduced GPU time about 7%; NVIDIA-only default. Does not establish the same gain here. |
| [#2093](https://github.com/NotRexed/Hookshot/pull/2093) | Correct day-clock progression above 60 FPS | Live clock before/after evidence and independent review. Preserve official water, sound and timing fixes. |
| [#2540](https://github.com/NotRexed/Hookshot/pull/2540) | Keep builder-launched Linux games in their own scope | Independent actual-game process lifetime test. Direct launcher behavior is unchanged. |
| [#2575](https://github.com/NotRexed/Hookshot/pull/2575) | Honor disabled high-FPS logging switches | Deterministic parsing bug reproduced by existing source tests. |

## Removed pending changes

Full current descriptions, comments and reviews were rechecked before this conservative reduction.

- #2114: no measured cutscene gameplay run; unresolved video conversion and decoder-thread concerns.
- #1541: no isolated game gain for the broad bundle; affinity and cache changes remain disputed.
- #1946: reported gameplay did not exercise the stand-in pipeline path; current cold-cache behavior lacks validation.
- #2134: extra predicted pipelines have no demonstrated gameplay-use count and increase preparation work.
- #2433: promising final-head result, but only one confounded static-scene comparison; insufficient representative validation.
- #2487: real priority issue bundled with an optimization supported mainly by microbenchmarks; whole PR removed.
- #2545: terrain-writeback hypothesis has positive-path evidence, but the paired experiment did not reproduce the faulty case and independent confirmation is absent.

Removal does not establish that a PR is broken or caused the local performance regression. The smaller combination still needs gameplay validation.

## Official fixes and quality policy

#1961 and #2133 are supplied by official main. Official synchronization fixes remain, including the complete-submission fence mapping. The temporary old-fence diagnostic and launcher catch-up override are removed.

Upstream #1009 is present. Its additional low-VRAM texture reduction remains opt-in: unset or disabled `RX_VK_LOW_VRAM_MIPS` preserves previous texture limits. Explicit `RX_VK_LOW_VRAM_MIPS=1` still requires Minimum and a nonzero driver budget at or below 4.5 GiB. Player options, saves and caches are preserved.

## Updating this branch

The source was reconstructed from pinned official main and selected inputs while preserving published history. Removed PR heads remain ancestors, so ancestry alone no longer establishes that their code is present. For future updates reconstruct from the new official main plus only pending inputs still needed; do not rely on an ordinary merge to restore a previously removed implementation that has since landed upstream.

Build matching game and renderer binaries and run required checks before publishing. Keep game-derived files local. No FPS improvement is claimed for this combination without a comparable gameplay run.

## Validation

The conservative source passed independent composition review and the existing full suite: 455 passed, 0 failed, 20 skipped (175 seconds). The removed PRs' own checks were removed with their source; official-main checks and retained changes remain covered. The official Linux release build completed in 565 seconds (426-second compile phase), reusing 327 objects and compiling 159, with no failures or missing dynamic libraries. It ships 29,688 pipeline states. Matching game and renderer binaries were built from `af7ffa0740b97209ac3af43045fe142e19ae8394`. Shader preparation and gameplay were not run during this work. The changed translator triggers preparation at the next normal launch.
