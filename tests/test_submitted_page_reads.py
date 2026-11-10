"""Exercise production snapshot reads across alternating pages and invalidations."""
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / 'gpu/vk/vk_memory.cpp').read_text()
begin = src.index('bool submitted_page_reuse(')
end = src.index('\nuint64_t memory_capture_view()', begin)
production = src[begin:end]
PREFIX = r'''
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <unordered_map>
constexpr unsigned kPageShift = 12;
bool capture_enabled = true, readable = true;
bool capture_on() { return capture_enabled; }
std::atomic<bool> captures_seen{true};
std::atomic<uint64_t> cap_view_gen{1};
uint32_t generations[64];
uint32_t page_gen(uint64_t page) { return generations[page]; }
struct CapEntry { uint32_t gen, slot; };
CapEntry entries[64];
CapEntry cap_entry(uint64_t page) { return entries[page]; }
struct CapBuf { void* map; };
std::unordered_map<uint32_t, CapBuf> cap_bufs;
std::mutex pools_mu;
uint8_t live_bytes[64*4096], captured_bytes[64*4096];
int reads = 0;
struct Host {
    uint64_t gpu_guest(uint64_t gpu) { return gpu - (1ull << 40); }
    bool gpu_read(uint64_t gpu, void* dst, uint64_t n) {
        ++reads;
        if (!readable) return false;
        if (gpu >= (1ull<<40)) gpu = gpu_guest(gpu);
        assert(gpu+n <= sizeof live_bytes);
        std::memcpy(dst, live_bytes+gpu, n);
        return true;
    }
} instance, *host = &instance;
void logf(const char*, ...) {}
'''
SUFFIX = r'''
uint32_t word(uint64_t address) {
    uint32_t out;
    assert(memory_read_as_submitted(address, &out, 4));
    return out;
}
int main() {
    SubmittedReadDiagnostic diagnostic(0);
    auto* counters = diagnostic.stats;
    assert(bool(counters) == bool(std::getenv("RX_VK_SUBMITTED_DIAGNOSTICS")));
    SubmittedReadStats reasons;
    SubmittedPage cached;
    reasons.miss(1, 2, cached);
    cached.view = 1; cached.page = 2;
    reasons.miss(1, 2, cached);
    cached.page = 1;
    reasons.miss(1, 2, cached);
    cached.view = 2;
    reasons.miss(1, 2, cached);
    assert(reasons.empty == 1 && reasons.collision == 1 &&
           reasons.view_changed == 1 && reasons.stamp_changed == 1);
    if (std::getenv("RX_VK_SUBMITTED_BLOCK_COPY")) {
        assert(submitted_block_mask(4096, 1) == 1);
        assert(submitted_block_mask(4096+4095, 1) == (1u << 15));
        assert(submitted_block_mask(4096+255, 2) == 3);
        assert(submitted_block_mask(4096, 4096) == 0xffff);
    }
    const bool single = std::getenv("RX_VK_SUBMITTED_CACHE_SINGLE");
    std::memset(live_bytes, 0xaa, sizeof live_bytes);
    std::memset(captured_bytes, 0xbb, sizeof captured_bytes);
    for (unsigned i=0; i<64; ++i) { generations[i]=1; entries[i]={1,i}; }
    cap_bufs[1]={captured_bytes};
    assert(word(4096)==0xbbbbbbbb && word(8192)==0xbbbbbbbb);
    assert(word(4100)==0xbbbbbbbb && word(8196)==0xbbbbbbbb);
    assert(reads==(single ? 4 : 2)); // alternating pages no longer recopy on every word
    assert(word((1ull<<40)+8196)==0xbbbbbbbb); // same physical page through GPU VA
    assert(word(4096+1024)==0xbbbbbbbb); // another block in the same page
    uint8_t blocks[600];
    assert(memory_read_as_submitted(4096+250, blocks, sizeof blocks));
    for (auto b : blocks) assert(b == 0xbb); // crossing multiple block boundaries
    std::memset(captured_bytes+4096,0xcc,4096);
    ++cap_view_gen;
    assert(word(4096)==0xcccccccc); // newer submission replaces old cached bytes
    assert(word(4096+1024)==0xcccccccc); // invalidate previously filled distant block too
    ++generations[1];
    assert(word(4096)==0xaaaaaaaa); // write stamp makes older capture ineligible
    cap_bufs[2]={captured_bytes};entries[1].gen=2;
    ++cap_view_gen;
    assert(word(4096)==0xcccccccc);
    uint8_t crossing[8];
    assert(memory_read_as_submitted(8190,crossing,8));
    assert(crossing[0]==0xcc && crossing[1]==0xcc && crossing[2]==0xbb && crossing[7]==0xbb);
    // A colliding slot must still check the page identity, not just its generation.
    uint64_t collision = 3;
    while (&submitted_page_for(collision) != &submitted_page_for(1)) ++collision;
    std::memset(captured_bytes+collision*4096,0xdd,4096);
    assert(word(collision*4096)==0xdddddddd);
    assert(word(4096)==0xcccccccc);
    cap_bufs.clear(); ++cap_view_gen;
    assert(word(4096)==0xaaaaaaaa); // retired capture is not reused
    readable=false; ++cap_view_gen;
    uint32_t out=0;
    assert(!memory_read_as_submitted(4096,&out,4));
    readable=true; capture_enabled=false;
    assert(word(8192)==0xaaaaaaaa);
    if (counters) {
        assert(counters->overlay_hits >= 1);
        assert(counters->refill_bytes >= 256 && counters->refill_bytes % 256 == 0);
        assert(counters->view_changed >= 1 && counters->stamp_changed == 1);
        assert(counters->collision >= 1 && counters->crossing == 1 && counters->failures == 1);
    }
}
'''
with tempfile.TemporaryDirectory() as tmp:
    source=Path(tmp)/'test.cpp'
    exe=Path(tmp)/('test.exe' if os.name=='nt' else 'test')
    source.write_text(PREFIX+production+SUFFIX)
    subprocess.run([os.environ.get('CXX','g++'),'-std=c++20','-Wall','-Wextra','-Werror',str(source),'-o',str(exe)],check=True)
    env={k:v for k,v in os.environ.items() if k not in ('RX_VK_SUBMITTED_CACHE_SINGLE', 'RX_VK_SUBMITTED_DIAGNOSTICS', 'RX_VK_SUBMITTED_BLOCK_COPY')}
    subprocess.run([str(exe)],env=env,check=True)
    subprocess.run([str(exe)],env=dict(env,RX_VK_SUBMITTED_CACHE_SINGLE='1'),check=True)
    subprocess.run([str(exe)],env=dict(env,RX_VK_SUBMITTED_DIAGNOSTICS='1'),check=True)
    subprocess.run([str(exe)],env=dict(env,RX_VK_SUBMITTED_DIAGNOSTICS='1',RX_VK_SUBMITTED_CACHE_SINGLE='1'),check=True)
    subprocess.run([str(exe)],env=dict(env,RX_VK_SUBMITTED_DIAGNOSTICS='1',RX_VK_SUBMITTED_BLOCK_COPY='1'),check=True)
    subprocess.run([str(exe)],env=dict(env,RX_VK_SUBMITTED_DIAGNOSTICS='1',RX_VK_SUBMITTED_BLOCK_COPY='1',RX_VK_SUBMITTED_CACHE_SINGLE='1'),check=True)
print('PASS: alternating pages, aliases, new submissions, stamps, collisions, cross-page reads, retired captures, failures')
