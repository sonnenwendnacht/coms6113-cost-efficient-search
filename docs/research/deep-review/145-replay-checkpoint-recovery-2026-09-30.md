# Replay checkpoint recovery record

Updated: 2026-09-30 15:04 ET

The verifier-proxy similarity replay wrote a durable JSONL checkpoint after each selector seed. A second resume process was accidentally started while the original parent process still owned the same output directory. The duplicate was stopped before it could finish. Three complete rows had been written by both processes; their selection results, costs, and recommendations matched, with only runtime fields differing. The original checkpoint was preserved, a byte-for-byte backup was kept under the ignored run directory, and the duplicate keys were reduced to one copy before the original resumed.

The recovered checkpoint now contains exactly 56 unique settings: seven fractions (`0.01`, `0.025`, `0.05`, `0.1`, `0.2`, `0.3`, `0.5`) times eight registered seeds. The report was regenerated in report-only mode. No search or audit cells were changed by this recovery.

The replay runner now creates an advisory process lock at `<output-dir>/.replay.lock`, uses an OS-held exclusive lock while running, and fails before opening the checkpoint when another writer owns the directory. The lock is released by the operating system when the process exits. The checkpoint loader still rejects duplicate complete records and truncates only an incomplete final JSON line.
