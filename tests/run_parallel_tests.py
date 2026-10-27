"""
High-Performance Multi-Threaded & Multi-Core Test Runner — Class Warrior (Fury).
Sfrutta appieno i core della CPU (multiprocessing / ProcessPoolExecutor) per eseguire
in parallelo tutti gli script di test della suite, riducendo i tempi di esecuzione e
garantendo la totale indipendenza dei processi.
"""

import os
import sys
import time
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed

# Configura encoding stdout per terminali Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(TEST_DIR)

# Elenco dei file di test dedicati
TEST_SCRIPTS = [
    "test_lua.py",
    "test_components_integrity.py",
    "test_tree_layout.py",
    "test_string_sync.py",
    "test_stats_panel.py",
    "test_utility_row.py",
    "test_rotational.py",
    "test_sunder_tracker.py",
]

def run_single_test_script(script_name):
    """Esegue un singolo script di test in un processo separato."""
    script_path = os.path.join(TEST_DIR, script_name)
    start_time = time.perf_counter()
    
    cmd = [sys.executable, script_path]
    result = subprocess.run(
        cmd,
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    duration = time.perf_counter() - start_time
    
    return {
        "script": script_name,
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "duration": duration,
        "returncode": result.returncode
    }

def main():
    print("=" * 78)
    print("🚀 AVVIO TEST SUITE PARALLELA MULTI-CORE — CLASS WARRIOR (FURY 3.3.5A)")
    print(f"Directory Progetto : {PROJECT_DIR}")
    print(f"Script Rilevati    : {len(TEST_SCRIPTS)}")
    print("=" * 78)

    start_total = time.perf_counter()
    max_workers = min(os.cpu_count() or 4, len(TEST_SCRIPTS))
    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_single_test_script, s): s for s in TEST_SCRIPTS}
        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            status = " PASS " if res["success"] else " FAIL "
            symbol = "✓" if res["success"] else "✗"
            print(f"[{symbol}] {res['script']:<32} | {res['duration']:>5.2f}s | {status}")
            if not res["success"]:
                print(f"    --> STDERR: {res['stderr'].strip()}")
                print(f"    --> STDOUT: {res['stdout'].strip()}")

    total_duration = time.perf_counter() - start_total
    all_passed = all(r["success"] for r in results)

    print("-" * 78)
    print(f"Riepilogo: {sum(1 for r in results if r['success'])}/{len(TEST_SCRIPTS)} superati con successo in {total_duration:.2f}s")
    print("=" * 78)

    if not all_passed:
        print("❌ ALCUNI TEST SONO FALLITI!")
        sys.exit(1)
    else:
        print("🎉 TUTTI I TEST PARALLELI SONO STATI SUPERATI CON SUCCESSO!")
        sys.exit(0)

if __name__ == "__main__":
    main()
