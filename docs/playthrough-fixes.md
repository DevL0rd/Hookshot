# Playthrough fixes

This branch combines current upstream main with selected pending pull requests for playthrough testing. It is separate from the fork's main and is not an upstream release.

Upstream base (2026-11-12): `ef81aee767f848255ca08171bba33b8c40c79347`.

The exact PR input heads, merge commits, upstreamed changes and local integration adjustments are recorded in [playthrough-prs.json](playthrough-prs.json). Existing history is preserved; this update does not rewrite the published branch.

## Pending PRs carried by this branch

| PR | Purpose | Merge |
|---|---|---|
| [#2114](https://github.com/NotRexed/Hookshot/pull/2114) | Linux video conversion and SIMD interleave | `8aee507e3d6b` |
| [#1541](https://github.com/NotRexed/Hookshot/pull/1541) | Renderer CPU reuse, affinity and bounded diagnostics | `a6361e64b8b8` |
| [#1377](https://github.com/NotRexed/Hookshot/pull/1377) | Prefer hot memory pools for VRAM mirrors | `ef21bd010a4a` |
| [#1946](https://github.com/NotRexed/Hookshot/pull/1946) | Quick pipelines and Shader compile option | `4409b418059b` |
| [#2134](https://github.com/NotRexed/Hookshot/pull/2134) | Plain-variant preparation and additional pipeline states | `6f1deac09e77` |
| [#2306](https://github.com/NotRexed/Hookshot/pull/2306) | Native NVIDIA float atomic adds | `d7ea6951a005` |
| [#2433](https://github.com/NotRexed/Hookshot/pull/2433) | Guarded fast float regions in translated CPU code | `874b2aa8f5a8` |
| [#2487](https://github.com/NotRexed/Hookshot/pull/2487) | Linux condition-variable and priority fast paths | `3ef735f23d82` |
| [#2545](https://github.com/NotRexed/Hookshot/pull/2545) | Asynchronous writeback of drawn terrain tiles | `7afd483fc8ec` |
| [#2540](https://github.com/NotRexed/Hookshot/pull/2540) | Keep Linux launcher game processes in their own scope | `7023ab015caf` |
| [#2093](https://github.com/NotRexed/Hookshot/pull/2093) | Correct day-clock progression above 60 FPS | `e2bf4d31d759` |
| [#2575](https://github.com/NotRexed/Hookshot/pull/2575) | Honor disabled high-FPS logging switches | `bd0e8694f6ae` |

## Incorporated upstream

#1961 (pipeline-cache lookup) and #2133 (converted pipeline records) are now in upstream main. Their original merge history remains, but they need no separate application during a future clean reconstruction.

## Quality and integration policies

Upstream now includes #1009. In this fork its additional low-VRAM texture reduction is opt-in: unset or disabled `RX_VK_LOW_VRAM_MIPS` preserves the previous texture limits. Explicit `RX_VK_LOW_VRAM_MIPS=1` still requires Minimum and a nonzero driver budget at or below 4.5 GiB.

The updated #1946 defaults to Wait where needed. Saved player choices remain intact. Unknown translations and memory-writing draws retain upstream safety rules; the explicit legacy mode retains its own documented behavior. Cleared targets are treated as fresh targets. Quick stand-in pipelines stay outside persistent caches.

The fast-float startup enable cache uses atomic accesses so parallel guest threads do not race. Renderer on/off switches, timestamp ordering and extracted-source fixtures have been reconciled with current upstream. These small local adjustments are listed separately in the manifest.

## Updating the combination

Fetch current upstream main and check each listed PR's state and equivalent code before updating. A future clean reconstruction should start from that main and apply only PRs still needed, using current heads. A closed PR does not prove its change was merged. Keep local corrections until equivalent fixes land, and update the manifest after resolving overlaps against current upstream.

Run the existing full test suite and a matching native game/renderer build before publishing. Preserve player saves, options and caches; keep game-derived files local.

## Validation and measurement

Upstream benchmarks concern their stated hardware and scenes; they are not measurements of this combination. CPU microbenchmarks and GPU-time changes do not imply an additive FPS gain. Gameplay, visual quality and long-session behavior remain player validation.

Validated source: `043e2e290e54bfe4d3a260ba4cd1b459285e2d33`. The existing full suite passed with 478 passed, 0 failed and 20 skipped; CPU and renderer reviews accepted the combination. The official Linux native release build completed in 15 minutes 7 seconds, with matching game/renderer binaries and no missing dynamic libraries. Shader preparation and gameplay were not run during installation.

The bundle ships 41,673 pipeline states. The translator changed, so the next normal launch prepares the updated shaders; existing saves, options and caches are retained. An explicit preparation run is available with `hookshot --prepare-shaders`.
