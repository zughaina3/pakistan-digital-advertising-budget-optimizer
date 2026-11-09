"""
Pakistan Digital Advertising Budget Optimizer - Big Data Benchmark Suite
========================================================================
Phase 2: Big Data Simulation & Framework Performance Benchmark

Compares 3 computational paradigms across 4 data scale tiers:
  Tiers: 10,000 | 100,000 | 1,000,000 | 10,000,000 records

Paradigms Compared:
  1. Pandas (In-Memory): Single-node, in-memory vectorized aggregation (C-optimized)
  2. MapReduce Architecture (Simulation): Multi-process streaming Map-Combine-Shuffle-Reduce
  3. Apache Spark Engine (Simulation): Partition-based DAG execution with Catalyst optimization
     and memory-optimized shuffled aggregation

Key Measurement Integrity Features:
  - Process Isolation: Each benchmark run executes in a dedicated fresh Python subprocess,
    preventing lifetime `ru_maxrss` high-water mark bleeding and artificial memory clamping.
  - Pure Aggregation Timing: In the 10M streaming tier, data generation is strictly separated
    from computation timing; the timer measures ONLY engine aggregation and partition reduction.
"""

import os
import gc
import sys
import time
import json
import resource
import argparse
import subprocess
import multiprocessing as mp
from collections import defaultdict
import numpy as np
import pandas as pd

import importlib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
_gen_mod = importlib.import_module('scripts.01_synthetic_data_generator')
generate_batch = _gen_mod.generate_batch
generate_streaming_chunks = _gen_mod.generate_streaming_chunks
PLATFORMS = _gen_mod.PLATFORMS
CITIES = _gen_mod.CITIES


def get_process_peak_rss_mb() -> float:
    """
    Measure peak Resident Set Size (RSS) memory across the main process AND all child worker processes.
    Uses Python's standard library resource module.
    """
    scale = (1024 * 1024) if sys.platform == 'darwin' else 1024.0
    self_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / scale
    child_rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / scale
    return round(self_rss + child_rss, 2)


# ==============================================================================
# 1. PANDAS ENGINE (Single-Node Vectorized In-Memory)
# ==============================================================================

def run_pandas_engine(df: pd.DataFrame) -> pd.DataFrame:
    """Execute aggregation using in-memory vectorized Pandas groupby."""
    agg = df.groupby(['platform', 'city']).agg({
        'spend': 'sum',
        'revenue': 'sum',
        'impressions': 'sum',
        'clicks': 'sum',
        'conversions': 'sum'
    }).reset_index()
    
    agg['roas'] = (agg['revenue'] / agg['spend']).round(2)
    agg['cpa'] = (agg['spend'] / agg['conversions']).round(2)
    agg['ctr'] = ((agg['clicks'] / agg['impressions']) * 100).round(2)
    agg['cvr'] = ((agg['conversions'] / agg['clicks']) * 100).round(2)
    return agg.sort_values('revenue', ascending=False).reset_index(drop=True)


# ==============================================================================
# 2. MAPREDUCE ARCHITECTURE (Multi-Process Streaming Map-Combine-Reduce Simulation)
# ==============================================================================

def _map_reduce_worker(chunk_records):
    """
    Map & Combine Phase (Worker node execution):
    Emits key-value pairs (key = (platform, city)) and locally combines (pre-aggregates)
    to minimize inter-process shuffle bandwidth.
    """
    local_accumulator = defaultdict(lambda: [0.0, 0.0, 0, 0, 0])
    for row in chunk_records:
        key = (row[0], row[1])
        acc = local_accumulator[key]
        acc[0] += row[2]  # spend
        acc[1] += row[3]  # revenue
        acc[2] += row[4]  # impressions
        acc[3] += row[5]  # clicks
        acc[4] += row[6]  # conversions
    return dict(local_accumulator)


def run_mapreduce_engine(df_or_records, num_workers: int = None) -> pd.DataFrame:
    """
    Full MapReduce pipeline simulation:
      Stage 1: Input Split (Chunking data across partitions)
      Stage 2: Map Phase & Combiner (Executed in parallel worker pool)
      Stage 3: Shuffle & Partition Phase (Hash-based aggregation of intermediate pairs)
      Stage 4: Reduce Phase (Global merge & derived metric computation)
    """
    if num_workers is None:
        num_workers = max(2, min(mp.cpu_count(), 4))
        
    if isinstance(df_or_records, pd.DataFrame):
        records = df_or_records[['platform', 'city', 'spend', 'revenue', 'impressions', 'clicks', 'conversions']].values.tolist()
    else:
        records = df_or_records
        
    n = len(records)
    chunk_size = max(1, n // num_workers)
    chunks = [records[i:i + chunk_size] for i in range(0, n, chunk_size)]
    
    # Parallel Map & Combine across worker processes
    with mp.Pool(processes=num_workers) as pool:
        mapped_partitions = pool.map(_map_reduce_worker, chunks)
        
    # Shuffle & Reduce Phase
    global_reduced = defaultdict(lambda: [0.0, 0.0, 0, 0, 0])
    for part in mapped_partitions:
        for key, vals in part.items():
            acc = global_reduced[key]
            acc[0] += vals[0]
            acc[1] += vals[1]
            acc[2] += vals[2]
            acc[3] += vals[3]
            acc[4] += vals[4]
            
    # Final Metric Projection
    rows = []
    for (platform, city), vals in global_reduced.items():
        spend, revenue, impressions, clicks, conversions = vals
        roas = round(revenue / spend, 2) if spend > 0 else 0.0
        cpa = round(spend / conversions, 2) if conversions > 0 else 0.0
        ctr = round((clicks / impressions) * 100, 2) if impressions > 0 else 0.0
        cvr = round((conversions / clicks) * 100, 2) if clicks > 0 else 0.0
        rows.append({
            'platform': platform, 'city': city,
            'spend': spend, 'revenue': revenue,
            'impressions': impressions, 'clicks': clicks,
            'conversions': conversions,
            'roas': roas, 'cpa': cpa, 'ctr': ctr, 'cvr': cvr
        })
        
    res_df = pd.DataFrame(rows)
    return res_df.sort_values('revenue', ascending=False).reset_index(drop=True)


# ==============================================================================
# 3. APACHE SPARK ARCHITECTURE (Partitioned DAG & Shuffled Hash Aggregation)
# ==============================================================================

class SparkCatalystSimulationEngine:
    """
    Simulation of Apache Spark's Catalyst Optimizer & RDD Partitioning Engine.
    Models:
      - Logical to Physical DAG plan creation
      - Partition-level localized execution
      - Intermediate Exchange / Shuffle stage across partitions
      - Lazy evaluation triggered by terminal action (.collect())
    """
    def __init__(self, data, num_partitions: int = 8):
        self.num_partitions = num_partitions
        if isinstance(data, pd.DataFrame):
            self.df = data[['platform', 'city', 'spend', 'revenue', 'impressions', 'clicks', 'conversions']].copy()
        else:
            self.df = pd.DataFrame(data, columns=['platform', 'city', 'spend', 'revenue', 'impressions', 'clicks', 'conversions'])
        self._dag = []
        
    def groupBy(self, *cols):
        self._group_cols = list(cols)
        return self
        
    def agg(self, agg_dict):
        self._agg_dict = agg_dict
        return self
        
    def collect(self) -> pd.DataFrame:
        """Action that triggers DAG pipeline execution across partitions."""
        partition_indices = np.array_split(np.arange(len(self.df)), self.num_partitions)
        partition_results = []
        
        # Local partition aggregation (Catalyst Map stage)
        for idx in partition_indices:
            p_slice = self.df.iloc[idx]
            p_agg = p_slice.groupby(self._group_cols).agg(self._agg_dict).reset_index()
            partition_results.append(p_agg)
            
        # Shuffled Hash Aggregation (Exchange / Reduce stage)
        shuffled = pd.concat(partition_results, ignore_index=True)
        final_agg = shuffled.groupby(self._group_cols).sum().reset_index()
        
        final_agg['roas'] = (final_agg['revenue'] / final_agg['spend']).round(2)
        final_agg['cpa'] = (final_agg['spend'] / final_agg['conversions']).round(2)
        final_agg['ctr'] = ((final_agg['clicks'] / final_agg['impressions']) * 100).round(2)
        final_agg['cvr'] = ((final_agg['conversions'] / final_agg['clicks']) * 100).round(2)
        return final_agg.sort_values('revenue', ascending=False).reset_index(drop=True)


def run_spark_simulation_engine(df: pd.DataFrame) -> pd.DataFrame:
    """Execute aggregation pipeline using Spark Catalyst Partitioned Model."""
    sdf = SparkCatalystSimulationEngine(df, num_partitions=8)
    res = sdf.groupBy('platform', 'city').agg({
        'spend': 'sum',
        'revenue': 'sum',
        'impressions': 'sum',
        'clicks': 'sum',
        'conversions': 'sum'
    }).collect()
    return res


# ==============================================================================
# 4. ISOLATED WORKER PROCESS RUNNER
# ==============================================================================

def execute_isolated_worker(engine: str, tier: str, csv_path: str = None) -> dict:
    """
    Executed inside a dedicated fresh Python process to guarantee zero memory contamination.
    Times strictly the aggregation logic and measures the process's peak RSS.
    """
    gc.collect()
    
    if tier in ['10k', '100k', '1m']:
        if csv_path and os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
        else:
            count = 10000 if tier == '10k' else (100000 if tier == '100k' else 1000000)
            df = generate_batch(count, seed=42)
            
        gc.collect()
        t0 = time.perf_counter()
        if engine == 'pandas':
            res = run_pandas_engine(df)
        elif engine == 'mapreduce':
            res = run_mapreduce_engine(df)
        elif engine == 'spark':
            res = run_spark_simulation_engine(df)
        else:
            raise ValueError(f"Unknown engine: {engine}")
        elapsed = time.perf_counter() - t0
        rows_out = len(res)
        num_records = len(df)
        
    elif tier == '10m':
        total_records = 10_000_000
        chunk_size = 1_000_000
        total_time = 0.0
        acc = None
        
        def iter_10m_chunks(seed):
            if csv_path and os.path.exists(csv_path):
                for c in pd.read_csv(csv_path, chunksize=chunk_size):
                    yield c
            else:
                for c in generate_streaming_chunks(total_records, chunk_size=chunk_size, start_seed=seed):
                    yield c

        if engine == 'pandas':
            for chunk_df in iter_10m_chunks(101):
                t0 = time.perf_counter()
                c_agg = chunk_df.groupby(['platform', 'city']).agg({
                    'spend': 'sum', 'revenue': 'sum', 'impressions': 'sum', 'clicks': 'sum', 'conversions': 'sum'
                }).reset_index()
                acc = c_agg if acc is None else pd.concat([acc, c_agg]).groupby(['platform', 'city']).sum().reset_index()
                total_time += (time.perf_counter() - t0)
            rows_out = len(acc)
            
        elif engine == 'spark':
            for chunk_df in iter_10m_chunks(301):
                t0 = time.perf_counter()
                c_spark = run_spark_simulation_engine(chunk_df)
                acc = c_spark if acc is None else pd.concat([acc, c_spark]).groupby(['platform', 'city']).sum().reset_index()
                total_time += (time.perf_counter() - t0)
            rows_out = len(acc)
            
        elif engine == 'mapreduce':
            mr_global = defaultdict(lambda: [0.0, 0.0, 0, 0, 0])
            for chunk_df in iter_10m_chunks(201):
                t0 = time.perf_counter()
                c_mr = run_mapreduce_engine(chunk_df)
                for _, r in c_mr.iterrows():
                    k = (r['platform'], r['city'])
                    a = mr_global[k]
                    a[0] += r['spend']
                    a[1] += r['revenue']
                    a[2] += r['impressions']
                    a[3] += r['clicks']
                    a[4] += r['conversions']
                total_time += (time.perf_counter() - t0)
            rows_out = len(mr_global)
            
        elapsed = total_time
        num_records = total_records
    else:
        raise ValueError(f"Unknown tier: {tier}")
        
    peak_rss = get_process_peak_rss_mb()
    throughput = int(num_records / elapsed) if elapsed > 0 else 0
    
    engine_display = {
        'pandas': 'Pandas (In-Memory)',
        'mapreduce': 'MapReduce (Multi-Proc)',
        'spark': 'Spark (Partitioned DAG)'
    }[engine]
    
    return {
        'engine': engine_display,
        'records': num_records,
        'tier': tier,
        'elapsed_sec': round(elapsed, 4),
        'peak_mem_mb': round(peak_rss, 2),
        'throughput_rps': throughput,
        'rows_output': rows_out
    }


# ==============================================================================
# 5. BENCHMARK ORCHESTRATOR
# ==============================================================================

def run_full_benchmark(data_dir: str = 'data/raw', output_csv: str = 'data/processed/benchmark_results.csv', include_10m: bool = True):
    """
    Orchestrate isolated execution across 4 tiers:
      - 10K records
      - 100K records
      - 1M records
      - 10M records (Streaming distinct chunks, pure aggregation timing)
    """
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    results = []
    
    tiers = [
        ('10k', 10000, os.path.join(data_dir, 'campaign_data_10k.csv')),
        ('100k', 100000, os.path.join(data_dir, 'campaign_data_100k.csv')),
        ('1m', 1000000, os.path.join(data_dir, 'campaign_data_1m.csv'))
    ]
    
    if include_10m:
        path_10m = os.path.join(data_dir, 'campaign_data_10m.csv')
        tiers.append(('10m', 10000000, path_10m if os.path.exists(path_10m) else None))

        
    print("\n" + "=" * 90)
    print(" 🚀 BIG DATA BENCHMARK: PANDAS vs. MAPREDUCE vs. SPARK ARCHITECTURE")
    print("=" * 90)
    print("Methodological Standards:")
    print("  ✓ Isolated Process Execution: Each engine runs in a fresh process to measure true peak RSS.")
    print("  ✓ Pure Aggregation Timing: 10M tier times computation strictly, excluding data generation.")
    print("  ✓ Standardized Workload: Multi-dimensional group by (platform, city) with metric projections.")
    
    python_bin = sys.executable
    script_path = os.path.abspath(__file__)
    
    for label, count, csv_path in tiers:
        print(f"\n--- Tier: {label.upper()} ({count:,} records) ---")
        for eng in ['pandas', 'mapreduce', 'spark']:
            cmd = [python_bin, script_path, '--worker', '--engine', eng, '--tier', label]
            if csv_path:
                cmd.extend(['--csv', csv_path])
                
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                print(f"❌ Error in worker {eng} ({label}):")
                print(proc.stderr)
                sys.exit(1)
                
            # Parse output json
            out_lines = [l.strip() for l in proc.stdout.split('\n') if l.strip().startswith('{') and l.strip().endswith('}')]
            if not out_lines:
                print(f"❌ Could not parse JSON from worker: {proc.stdout}")
                sys.exit(1)
            res = json.loads(out_lines[-1])
            results.append(res)
            print(f"  {res['engine']:<25} | Time: {res['elapsed_sec']:>7.3f}s | Peak RSS: {res['peak_mem_mb']:>7.1f} MB | Throughput: {res['throughput_rps']:>10,} rec/s")
            
    bench_df = pd.DataFrame(results)
    bench_df.to_csv(output_csv, index=False)
    
    print("\n" + "=" * 90)
    print(" 📊 FINAL BENCHMARK SUMMARY TABLE")
    print("=" * 90)
    print(f"{'Data Tier':<10} {'Records':>12} {'Engine':<25} {'Time (s)':>10} {'Peak RSS (MB)':>15} {'Throughput (rec/s)':>20}")
    print("-" * 90)
    for _, row in bench_df.iterrows():
        print(f"{row['tier'].upper():<10} {row['records']:>12,} {row['engine']:<25} {row['elapsed_sec']:>10.3f} {row['peak_mem_mb']:>15.1f} {row['throughput_rps']:>20,}")
    print("=" * 90)
    print(f"✓ Results exported to: {output_csv}\n")
    return bench_df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Big Data Marketing Framework Benchmark.")
    parser.add_argument('--worker', action='store_true', help="Run single isolated worker process")
    parser.add_argument('--engine', type=str, choices=['pandas', 'mapreduce', 'spark'], help="Target engine")
    parser.add_argument('--tier', type=str, choices=['10k', '100k', '1m', '10m'], help="Target scale tier")
    parser.add_argument('--csv', type=str, default=None, help="Path to CSV dataset")
    parser.add_argument('--include-10m', action='store_true', default=True, help="Include 10M record stress benchmark")
    parser.add_argument('--no-10m', dest='include_10m', action='store_false', help="Exclude 10M record stress benchmark")
    args = parser.parse_args()
    
    if args.worker:
        worker_res = execute_isolated_worker(args.engine, args.tier, args.csv)
        print(json.dumps(worker_res))
    else:
        run_full_benchmark(include_10m=args.include_10m)
