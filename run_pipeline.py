"""
Pakistan Digital Advertising Budget Optimizer - Master Execution Pipeline
==========================================================================
Phase 2: End-to-End Orchestrator

Executes:
  1. Synthetic Big Data Generation (10K, 100K, 1M tiers)
  2. Multi-Dimensional Marketing Metrics Engineering (CTR, CPC, CPA, CVR, ROAS)
  3. Big Data Benchmark (Pandas vs. MapReduce vs. Apache Spark)
  4. Ad Budget Recommendation Engine (Allocation of the next Rs. 1 Million)
  5. Publication-Grade Visualization Suite (10 high-res charts at 300 DPI)
  6. Interactive Google Colab Notebook Compilation (.ipynb)
  7. SQL Analytics Suite Verification
"""

import os
import sys
import time
import argparse
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)


def log_step(step_num: int, total_steps: int, title: str):
    print("\n" + "=" * 80)
    print(f" [{step_num}/{total_steps}] {title.upper()}")
    print("=" * 80)


def run_command(cmd, desc):
    print(f"Executing: {desc}...")
    t0 = time.time()
    res = subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT, capture_output=True, text=True)
    elapsed = time.time() - t0
    if res.returncode != 0:
        print(f"❌ Error during: {desc}")
        print(res.stderr)
        sys.exit(1)
    else:
        print(res.stdout.strip())
        print(f"✓ Completed in {elapsed:.2f}s")


def main():
    parser = argparse.ArgumentParser(description="Master Execution Pipeline for Pakistan Ad Budget Optimizer.")
    parser.add_argument('--skip-gen', action='store_true', help="Skip data generation if CSVs exist")
    parser.add_argument('--include-10m', action='store_true', default=True, help="Include 10M record stress benchmark")
    args = parser.parse_args()

    python_bin = sys.executable

    print("\n" + "#" * 80)
    print(" 🇵🇰 PAKISTAN DIGITAL ADVERTISING BUDGET OPTIMIZER (PHASE 2)")
    print(" Big Data Analytics, Performance Benchmarking & Ad Budget Reallocation")
    print("#" * 80)

    total_steps = 7

    # Step 1: Data Generation
    log_step(1, total_steps, "Synthetic Big Data Generation")
    raw_100k = os.path.join(PROJECT_ROOT, 'data/raw/campaign_data_100k.csv')
    if args.skip_gen and os.path.exists(raw_100k):
        print("✓ Raw datasets already exist. Skipping generation.")
    else:
        run_command(f'"{python_bin}" scripts/01_synthetic_data_generator.py --tier all',
                    "Generating multi-tier datasets (10K, 100K, 1M)")

    # Step 2: Marketing Metrics Engine
    log_step(2, total_steps, "Marketing Metrics & KPI Engineering")
    run_command(f'"{python_bin}" scripts/02_marketing_metrics_engine.py --input data/raw/campaign_data_100k.csv',
                "Computing CTR, CPC, CPA, CVR, ROAS across platforms & demographics")

    # Step 3: Big Data Benchmark
    log_step(3, total_steps, "Big Data Benchmark (Pandas vs. MapReduce vs. Spark)")
    flag_10m = "--include-10m" if args.include_10m else ""
    run_command(f'"{python_bin}" scripts/03_big_data_benchmark.py {flag_10m}',
                "Benchmarking execution time, peak RAM, and throughput across 10K to 10M records")

    # Step 4: Ad Budget Recommendation Engine (Rs. 1M)
    log_step(4, total_steps, "Marketing Budget Recommendation Engine")
    run_command(f'"{python_bin}" scripts/04_budget_recommendation_engine.py --budget 1000000',
                "Solving optimal allocation for Rs. 1 Million marketing spend")

    # Step 5: Visualizations (10 publication charts)
    log_step(5, total_steps, "Publication-Grade Visualization Suite (300 DPI)")
    run_command(f'"{python_bin}" scripts/05_visualizer.py',
                "Generating 10 publication charts in reports/figures/")

    # Step 6: Google Colab Notebook Compiler
    log_step(6, total_steps, "Interactive Google Colab Notebook Compilation")
    run_command(f'"{python_bin}" scripts/build_notebook.py',
                "Building notebooks/Pakistan_Ad_Budget_Optimizer_Phase2.ipynb")

    # Step 7: Executive PDF Report Generation
    log_step(7, total_steps, "Executive PDF Report Generation")
    run_command(f'"{python_bin}" scripts/generate_pdf_report.py',
                "Compiling reports/Pakistan_Digital_Advertising_Budget_Optimizer_Report.pdf")

    print("\n" + "#" * 80)
    print(" 🎉 PIPELINE EXECUTION COMPLETE!")
    print(" All datasets, benchmarks, models, charts, notebooks, and PDF reports generated.")
    print(" Review deliverables in:")
    print("   - Executive PDF Report: reports/Pakistan_Digital_Advertising_Budget_Optimizer_Report.pdf")
    print("   - Reports & Figures: reports/figures/")
    print("   - Recommendation Brief: reports/budget_recommendation_brief.json")
    print("   - SQL Suite: queries.sql")
    print("   - Google Colab Notebook: notebooks/Pakistan_Ad_Budget_Optimizer_Phase2.ipynb")
    print("#" * 80 + "\n")


if __name__ == '__main__':
    main()
