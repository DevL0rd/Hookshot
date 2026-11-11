# Playthrough fixes

This branch combines selected pending upstream pull requests for playthrough testing. It is separate from the fork's `main`; it is not an upstream release.

Upstream base: `ddafc1f9df3c34e6971d29b12ab6de5d55696685`. Fork: [DevL0rd/Hookshot](https://github.com/DevL0rd/Hookshot/tree/playthrough-fixes).

Each PR has its own merge commit. Exact input heads and merge commits are recorded in [playthrough-prs.json](playthrough-prs.json).

| PR | Purpose | Merge |
|---|---|---|
| [#2114](https://github.com/NotRexed/Hookshot/pull/2114) | Linux video conversion and SIMD interleave | `8aee507e3d6b` |
| [#1541](https://github.com/NotRexed/Hookshot/pull/1541) | Renderer CPU reuse, affinity and bounded diagnostics | `061d067a53b4` |
| [#1377](https://github.com/NotRexed/Hookshot/pull/1377) | Prefer hot memory pools for VRAM mirrors | `ef21bd010a4a` |
| [#1961](https://github.com/NotRexed/Hookshot/pull/1961) | Prepared stage-library lookup and cache-save policy | `568dd7ba90c3` |
| [#1946](https://github.com/NotRexed/Hookshot/pull/1946) | Quick pipelines and Shader compile option | `8e302f2cf516` |
| [#2133](https://github.com/NotRexed/Hookshot/pull/2133) | Converted pipeline-state contribution | `910c7ff86bf8` |
| [#2134](https://github.com/NotRexed/Hookshot/pull/2134) | Plain-variant preparation and additional pipeline states | `c702e314d224` |

PR #1009 is excluded: its low-VRAM policy reduces texture detail. No quality-reducing configuration changes are part of this combination.

## Updating the combination

Fetch the current upstream main and check the status of every listed PR before updating. A fresh reconstruction should start from that main and merge only the PRs still needed, using their current heads. Keep requested changes absent from upstream, remove entries superseded by upstream, and update the manifest with the new base and merge commits. Resolve overlaps against current upstream code rather than restoring older whole files.

A PR being closed does not prove its change is present upstream. Check its merge status and code before dropping it. Re-run the existing full test suite and source build before publishing an updated combination.

## Verification and limits

The imported PRs have different validation scopes. This branch needs its own combined source checks and native Linux build; upstream benchmark claims are not measurements of this combination. Gameplay, visual quality and long-session behavior remain player validation.

The Shader compile choice from #1946 defaults to Asynchronous and can omit draws until compilation completes. The menu also provides Wait where needed. #1377 primarily targets VRAM pressure; #2114 primarily targets video playback. No additive FPS gain is claimed.

Builds, extracted game files, shader/program caches and saves stay local and are not part of this repository.

Combined Linux validation on 2026-11-11: the existing full suite passed **384 checks, 0 failed, 10 skipped**. Skips are declared platform/device or game-dependent checks. Native game and renderer built successfully; the bundle carries **38,697 shipped pipeline states**. The build used the merged runtime at `c702e31`; subsequent fixture and ledger commits do not change that runtime. Gameplay remains unverified for this combination.
