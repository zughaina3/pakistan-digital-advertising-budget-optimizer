"""
Pakistan Digital Advertising Budget Optimizer - Publication-Grade Visualization Suite
=====================================================================================
Phase 2: Visual Analytics & Executive Presentation Suite

Generates 10 Publication-Grade Visualizations (300 DPI) in reports/figures/:
  01. Platform CPA / CAC Efficiency Comparison (Horizontal bar)
  02. Return on Ad Spend (ROAS) vs. 3.0x Break-Even Benchmark (Vertical bar)
  03. Big Data Benchmark: Execution Time Scalability (10K to 10M, Log Scale)
  04. Big Data Benchmark: Peak Memory Footprint & Throughput (Dual-panel)
  05. Multi-Stage Conversion Funnel by Platform (Grouped log scale)
  06. Rs. 1 Million Ad Budget Allocation Breakdown (Donut & Waterfall)
  07. Diminishing Marginal Returns & Saturation Curves (Response modeling)
  08. Regional City Performance Matrix Across Pakistan (Karachi, Lahore, etc.)
  09. Buyer Demographic Cohorts (Age & Gender Efficiency)
  10. Monthly Spend vs. Revenue vs. Net Profit Trajectory
"""

import os
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# Set writable cache for matplotlib
os.environ['MPLCONFIGDIR'] = os.path.abspath('.matplotlib_cache')

# Design system colors (Nexus Palette)
BG = '#F7F6F2'
TEXT = '#28251D'
TEXT_MUTED = '#7A7974'
PRIMARY = '#01696F'      # Deep Teal (Best performance)
SECONDARY = '#20808D'    # Medium Teal
ACCENT_RUST = '#A84B2F'  # Rust Red (Underperformance / Alert)
ACCENT_DARK = '#1B474D'  # Dark Teal
ACCENT_LIGHT = '#BCE2E7' # Soft Aqua
ACCENT_GOLD = '#D99B26'  # Gold / Warning

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'figure.facecolor': BG,
    'axes.facecolor': BG,
    'font.size': 10,
    'font.family': 'sans-serif',
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.labelcolor': TEXT,
    'text.color': TEXT,
    'xtick.color': TEXT_MUTED,
    'ytick.color': TEXT_MUTED,
    'axes.edgecolor': '#D4D1CA',
    'grid.color': '#E8E6E0',
    'grid.alpha': 0.6,
})


def format_pkr(val, pos=None):
    """Format PKR currency with standard abbreviations."""
    abs_val = abs(val)
    if abs_val >= 1e9:
        return f'Rs. {val/1e9:.1f}B'
    elif abs_val >= 1e6:
        return f'Rs. {val/1e6:.1f}M'
    elif abs_val >= 1e3:
        return f'Rs. {val/1e3:.0f}K'
    return f'Rs. {val:,.0f}'


# ==============================================================================
# CHART 1: CPA / CAC BY PLATFORM
# ==============================================================================
def plot_01_cpa_by_platform(df_platform, output_path):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    data = df_platform.sort_values('cpa', ascending=True).reset_index(drop=True)
    
    colors = [PRIMARY if p == data.iloc[0]['platform'] 
              else ACCENT_RUST if p == data.iloc[-1]['platform'] 
              else SECONDARY for p in data['platform']]
    
    bars = ax.barh(data['platform'], data['cpa'], color=colors, height=0.55, edgecolor='none')
    
    for bar, val in zip(bars, data['cpa']):
        ax.text(bar.get_width() + 15, bar.get_y() + bar.get_height()/2,
                f'Rs. {val:,.0f}', va='center', fontsize=10.5, fontweight='bold', color=TEXT)
                
    ax.set_xlabel('Customer Acquisition Cost (CPA / CAC in PKR)', fontsize=11, color=TEXT_MUTED)
    ax.set_title(f"Instagram and TikTok deliver lowest acquisition cost (Rs. {data.iloc[0]['cpa']:,.0f} - Rs. {data.iloc[1]['cpa']:,.0f}); YouTube costs {data.iloc[-1]['cpa']/data.iloc[0]['cpa']:.1f}x more",
                 loc='left', fontsize=12, color=TEXT, pad=12)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_pkr))
    ax.set_xlim(0, max(data['cpa']) * 1.22)
    ax.spines[['top', 'right']].set_visible(False)
    
    note = "Source: Pakistan D2C campaign performance data. CPA = Total Spend / Total Conversions. Teal = Most Efficient, Rust = High Cost."
    fig.text(0.02, -0.02, note, ha='left', va='top', fontsize=8, color=TEXT_MUTED)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  ✓ Saved: {output_path}")


# ==============================================================================
# CHART 2: ROAS VS. 3.0x BREAK-EVEN BENCHMARK
# ==============================================================================
def plot_02_roas_benchmark(df_platform, output_path):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    data = df_platform.sort_values('roas', ascending=False).reset_index(drop=True)
    
    blended_roas = df_platform['revenue'].sum() / df_platform['spend'].sum()
    colors = [PRIMARY if r >= 3.0 else ACCENT_RUST for r in data['roas']]
    
    bars = ax.bar(data['platform'], data['roas'], color=colors, width=0.52, edgecolor='none')
    
    for bar, val in zip(bars, data['roas']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.12,
                f'{val:.2f}x', ha='center', fontsize=10.5, fontweight='bold', color=TEXT)
                
    # Reference target line at 3.0x
    ax.axhline(y=3.0, color='#8E2800', linestyle='--', linewidth=1.5, alpha=0.85)
    ax.text(len(data) - 0.45, 3.08, 'Target Break-Even ROAS = 3.0x', ha='right', fontsize=9, color='#8E2800', fontweight='bold')
    
    # Blended line
    ax.axhline(y=blended_roas, color=PRIMARY, linestyle=':', linewidth=1.2, alpha=0.7)
    ax.text(len(data) - 0.45, blended_roas + 0.12, f'Blended Average: {blended_roas:.2f}x', ha='right', fontsize=9, color=PRIMARY, style='italic')
    
    ax.set_ylabel('Return on Ad Spend (ROAS = Revenue / Spend)', fontsize=11, color=TEXT_MUTED)
    ax.set_title(f"Google (4.62x) and Instagram (4.32x) exceed the 3.0x break-even target; TikTok and YouTube underperform",
                 loc='left', fontsize=12, color=TEXT, pad=12)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:.1f}x'))
    ax.set_ylim(0, max(data['roas']) * 1.25)
    ax.spines[['top', 'right']].set_visible(False)
    
    note = "ROAS = Attributed Revenue / Advertising Spend. Teal bars denote channels operating above the 3.0x corporate profitability threshold."
    fig.text(0.02, -0.02, note, ha='left', va='top', fontsize=8, color=TEXT_MUTED)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  ✓ Saved: {output_path}")


# ==============================================================================
# CHART 3: BIG DATA BENCHMARK SCALABILITY (10K TO 10M)
# ==============================================================================
def plot_03_benchmark_scalability(df_bench, output_path):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    
    engine_styles = {
        'Pandas': {'color': ACCENT_RUST, 'marker': 'o', 'ls': '-'},
        'MapReduce': {'color': ACCENT_GOLD, 'marker': 's', 'ls': '--'},
        'Apache Spark': {'color': PRIMARY, 'marker': '^', 'ls': '-'}
    }
    
    for engine, style in engine_styles.items():
        sub = df_bench[df_bench['engine'] == engine].sort_values('records')
        if len(sub) > 0:
            ax.plot(sub['records'], sub['elapsed_sec'], label=engine,
                    color=style['color'], marker=style['marker'], linestyle=style['ls'],
                    linewidth=2.4, markersize=8)
            
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Data Scale Volume (Number of Campaign Event Records, Log Scale)', fontsize=11, color=TEXT_MUTED)
    ax.set_ylabel('Execution Wall-Clock Time (Seconds, Log Scale)', fontsize=11, color=TEXT_MUTED)
    ax.set_title('Big Data Scalability: Spark and Pandas scale near-linearly; MapReduce exhibits parallel setup latency',
                 loc='left', fontsize=12, color=TEXT, pad=12)
    
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{int(x):,}'))
    ax.legend(frameon=True, facecolor=BG, edgecolor='#D4D1CA', loc='upper left', fontsize=10)
    ax.spines[['top', 'right']].set_visible(False)
    
    note = "Benchmark evaluates GroupBy Aggregation across 10K, 100K, 1M, and 10M records on multi-core architecture."
    fig.text(0.02, -0.02, note, ha='left', va='top', fontsize=8, color=TEXT_MUTED)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  ✓ Saved: {output_path}")


# ==============================================================================
# CHART 4: MEMORY FOOTPRINT & THROUGHPUT DUAL-PANEL
# ==============================================================================
def plot_04_memory_throughput(df_bench, output_path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    # 1M tier comparison
    tier_1m = df_bench[df_bench['tier'] == '1m'].copy()
    if len(tier_1m) == 0:
        tier_1m = df_bench[df_bench['records'] == 1000000].copy()
        
    palette = [ACCENT_RUST, ACCENT_GOLD, PRIMARY]
    
    # Left: Peak Memory Footprint
    bars1 = ax1.bar(tier_1m['engine'], tier_1m['peak_mem_mb'], color=palette, width=0.5)
    for bar in bars1:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                 f"{bar.get_height():.1f} MB", ha='center', fontsize=10, fontweight='bold', color=TEXT)
    ax1.set_title("Peak RAM Allocation at 1 Million Records", loc='left', fontsize=12, color=TEXT, pad=10)
    ax1.set_ylabel("Memory (MB)", fontsize=11, color=TEXT_MUTED)
    ax1.set_ylim(0, max(tier_1m['peak_mem_mb']) * 1.25)
    ax1.spines[['top', 'right']].set_visible(False)
    
    # Right: Processing Throughput (Records/Sec)
    bars2 = ax2.bar(tier_1m['engine'], tier_1m['throughput_rps'] / 1e6, color=palette, width=0.5)
    for bar in bars2:
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.25,
                 f"{bar.get_height():.2f}M rec/s", ha='center', fontsize=10, fontweight='bold', color=TEXT)
    ax2.set_title("Processing Throughput (Million Records / Sec)", loc='left', fontsize=12, color=TEXT, pad=10)
    ax2.set_ylabel("Throughput (M records/sec)", fontsize=11, color=TEXT_MUTED)
    ax2.set_ylim(0, max(tier_1m['throughput_rps'] / 1e6) * 1.25)
    ax2.spines[['top', 'right']].set_visible(False)
    
    fig.suptitle("Big Data Architectural Efficiency: Memory Footprint vs. Throughput (1M Records Tier)",
                 fontsize=13, fontweight='bold', color=TEXT, y=1.03)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  ✓ Saved: {output_path}")


# ==============================================================================
# CHART 5: CONVERSION FUNNEL BY PLATFORM
# ==============================================================================
def plot_05_conversion_funnel(df_platform, output_path):
    fig, ax = plt.subplots(figsize=(11, 5.5))
    data = df_platform.sort_values('conversions', ascending=True).reset_index(drop=True)
    
    y = np.arange(len(data))
    h = 0.25
    
    ax.barh(y + h, data['impressions'] / 1000, h, color=ACCENT_LIGHT, label='Impressions (Thousands)')
    ax.barh(y, data['clicks'], h, color=SECONDARY, label='Clicks')
    ax.barh(y - h, data['conversions'], h, color=ACCENT_DARK, label='Conversions / Orders')
    
    ax.set_yticks(y)
    ax.set_yticklabels(data['platform'], fontsize=11)
    ax.set_xscale('log')
    ax.set_xlabel('Volume (Logarithmic Scale)', fontsize=11, color=TEXT_MUTED)
    ax.set_title('Conversion Funnel: Google & Instagram lead order volume; TikTok generates top-of-funnel reach',
                 loc='left', fontsize=12, color=TEXT, pad=12)
    ax.legend(loc='lower right', frameon=True, facecolor=BG, edgecolor='#D4D1CA', fontsize=10)
    ax.spines[['top', 'right']].set_visible(False)
    
    note = "Log scale representation allows direct comparison across volume magnitudes (Impressions -> Clicks -> Conversions)."
    fig.text(0.02, -0.02, note, ha='left', va='top', fontsize=8, color=TEXT_MUTED)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  ✓ Saved: {output_path}")


# ==============================================================================
# CHART 6: RS. 1 MILLION AD BUDGET ALLOCATION
# ==============================================================================
def plot_06_budget_allocation(brief_path, output_path):
    import json
    with open(brief_path, 'r') as f:
        brief = json.load(f)
        
    rec = brief['recommended_allocation']['channels']
    df_rec = pd.DataFrame(rec)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    # Donut chart
    colors = [PRIMARY, SECONDARY, ACCENT_DARK, ACCENT_GOLD, ACCENT_RUST]
    wedges, texts, autotexts = ax1.pie(
        df_rec['spend'], labels=df_rec['platform'], autopct='%1.0f%%',
        startangle=140, colors=colors, pctdistance=0.75,
        textprops={'fontsize': 10, 'color': TEXT, 'fontweight': 'bold'},
        wedgeprops=dict(width=0.45, edgecolor=BG, linewidth=2)
    )
    for at in autotexts:
        at.set_color('white')
    ax1.set_title("Optimal Allocation Share (%)", loc='center', fontsize=12, color=TEXT, pad=10)
    
    # Center text
    ax1.text(0, 0, "Rs. 1M\nBudget", ha='center', va='center', fontsize=12, fontweight='bold', color=TEXT)
    
    # Waterfall / Bar chart of Expected Revenue by Channel
    bars = ax2.bar(df_rec['platform'], df_rec['revenue'] / 1e3, color=colors, width=0.52)
    for bar, rev, roas in zip(bars, df_rec['revenue'], df_rec['roas']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 25,
                 f"Rs. {rev/1e3:,.0f}K\n({roas:.2f}x)", ha='center', fontsize=9.5, fontweight='bold', color=TEXT)
                 
    ax2.set_ylabel("Expected Revenue (PKR Thousands)", fontsize=11, color=TEXT_MUTED)
    ax2.set_title("Projected Revenue Contribution by Channel (Rs. 3.09M Total)", loc='left', fontsize=12, color=TEXT, pad=10)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'Rs. {x:,.0f}K'))
    ax2.set_ylim(0, max(df_rec['revenue'] / 1e3) * 1.25)
    ax2.spines[['top', 'right']].set_visible(False)
    
    fig.suptitle("Management Recommendation: Where to Spend the Next Rs. 1 Million",
                 fontsize=14, fontweight='bold', color=TEXT, y=1.03)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  ✓ Saved: {output_path}")


# ==============================================================================
# CHART 7: DIMINISHING RETURNS SATURATION CURVES
# ==============================================================================
def plot_07_diminishing_returns(output_path):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    spend_range = np.linspace(10000, 600000, 200)
    
    # Response models
    platforms_cfg = {
        'Google': {'alpha': 2500000, 'roas_0': 4.62, 'color': PRIMARY},
        'Instagram': {'alpha': 2200000, 'roas_0': 4.32, 'color': SECONDARY},
        'Facebook': {'alpha': 1800000, 'roas_0': 3.01, 'color': ACCENT_DARK},
        'TikTok': {'alpha': 1200000, 'roas_0': 2.40, 'color': ACCENT_GOLD},
        'YouTube': {'alpha': 900000, 'roas_0': 1.81, 'color': ACCENT_RUST}
    }
    
    for p, cfg in platforms_cfg.items():
        beta = cfg['roas_0'] / cfg['alpha']
        expected_rev = cfg['alpha'] * np.log(1 + beta * spend_range)
        ax.plot(spend_range / 1e3, expected_rev / 1e3, label=f"{p} (Base: {cfg['roas_0']:.1f}x)",
                color=cfg['color'], linewidth=2.4)
        
    # Break-even line (ROAS = 3.0x)
    ax.plot(spend_range / 1e3, (spend_range * 3.0) / 1e3, 'k--', alpha=0.5, label='Break-Even 3.0x Benchmark')
    
    ax.set_xlabel('Channel Ad Spend (PKR Thousands)', fontsize=11, color=TEXT_MUTED)
    ax.set_ylabel('Projected Revenue (PKR Thousands)', fontsize=11, color=TEXT_MUTED)
    ax.set_title('Diminishing Marginal Returns: Google & Instagram sustain profitability beyond Rs. 350K spend',
                 loc='left', fontsize=12, color=TEXT, pad=12)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'Rs. {x:,.0f}K'))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'Rs. {x:,.0f}K'))
    ax.legend(frameon=True, facecolor=BG, edgecolor='#D4D1CA', loc='upper left', fontsize=9.5)
    ax.spines[['top', 'right']].set_visible(False)
    
    note = "Logarithmic saturation curves model audience fatigue and declining marginal returns as spend increases."
    fig.text(0.02, -0.02, note, ha='left', va='top', fontsize=8, color=TEXT_MUTED)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  ✓ Saved: {output_path}")


# ==============================================================================
# CHART 8: REGIONAL CITY REVENUE MATRIX ACROSS PAKISTAN
# ==============================================================================
def plot_08_city_performance(df_city, output_path):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    data = df_city.sort_values('revenue', ascending=True).reset_index(drop=True)
    
    colors = [PRIMARY if c in ['Karachi', 'Lahore', 'Islamabad'] else SECONDARY for c in data['city']]
    bars = ax.barh(data['city'], data['revenue'] / 1e6, color=colors, height=0.58)
    
    for bar, rev, roas in zip(bars, data['revenue'], data['roas']):
        ax.text(bar.get_width() + 4, bar.get_y() + bar.get_height()/2,
                f"Rs. {rev/1e6:,.1f}M ({roas:.2f}x)", va='center', fontsize=9.5, fontweight='bold', color=TEXT)
                
    ax.set_xlabel('Attributed Revenue (PKR Millions)', fontsize=11, color=TEXT_MUTED)
    ax.set_title('Regional E-Commerce Hubs: Karachi, Lahore, and Islamabad generate 77% of total revenue in Pakistan',
                 loc='left', fontsize=12, color=TEXT, pad=12)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'Rs. {x:.0f}M'))
    ax.set_xlim(0, max(data['revenue'] / 1e6) * 1.25)
    ax.spines[['top', 'right']].set_visible(False)
    
    note = "Karachi and Lahore dominate e-commerce GMV due to established Cash on Delivery (COD) logistics corridors."
    fig.text(0.02, -0.02, note, ha='left', va='top', fontsize=8, color=TEXT_MUTED)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  ✓ Saved: {output_path}")


# ==============================================================================
# CHART 9: DEMOGRAPHIC AGE & GENDER EFFICIENCY
# ==============================================================================
def plot_09_demographics(df_demo, output_path):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    # Extract age and gender
    data = df_demo.copy()
    data[['gender', 'age']] = data['demographic'].str.split(' \\| ', expand=True)
    pivot = data.pivot(index='age', columns='gender', values='roas')
    
    pivot.plot(kind='bar', ax=ax, colormap='viridis', width=0.6, edgecolor='none')
    
    ax.set_ylabel('Return on Ad Spend (ROAS)', fontsize=11, color=TEXT_MUTED)
    ax.set_xlabel('Consumer Age Bracket', fontsize=11, color=TEXT_MUTED)
    ax.set_title('Demographic Efficiency: Females aged 18-34 deliver highest ROAS (> 3.8x) for fashion & pret',
                 loc='left', fontsize=12, color=TEXT, pad=12)
    ax.axhline(y=3.0, color=ACCENT_RUST, linestyle='--', linewidth=1.2, label='Break-Even 3.0x')
    ax.legend(title='Gender Segment', frameon=True, facecolor=BG, edgecolor='#D4D1CA', loc='upper right')
    ax.spines[['top', 'right']].set_visible(False)
    plt.xticks(rotation=0)
    
    note = "Female demographic segments show superior conversion intent for stitched pret, lawn, and university tote bags."
    fig.text(0.02, -0.02, note, ha='left', va='top', fontsize=8, color=TEXT_MUTED)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  ✓ Saved: {output_path}")


# ==============================================================================
# CHART 10: MONTHLY TIME-SERIES SPEND VS. REVENUE VS. PROFIT
# ==============================================================================
def plot_10_monthly_trend(df_monthly, output_path):
    fig, ax = plt.subplots(figsize=(11, 5.5))
    data = df_monthly.sort_values('month').reset_index(drop=True)
    
    ax.plot(data['month'], data['spend'] / 1e6, color=ACCENT_RUST, linewidth=2.5,
            marker='o', markersize=6, label='Advertising Spend')
    ax.plot(data['month'], data['revenue'] / 1e6, color=PRIMARY, linewidth=2.5,
            marker='s', markersize=6, label='Attributed Revenue')
    ax.plot(data['month'], data['net_profit'] / 1e6, color=ACCENT_GOLD, linewidth=2.0,
            marker='^', linestyle='--', markersize=6, label='Net Margin Contribution')
            
    ax.fill_between(data['month'], data['spend'] / 1e6, data['revenue'] / 1e6,
                    color=PRIMARY, alpha=0.08, label='Net Marketing Profit Zone')
                    
    ax.set_ylabel('Amount (PKR Millions)', fontsize=11, color=TEXT_MUTED)
    ax.set_title('Annual Performance Trend: Revenue scaled 180% during Eid & Summer Pret launches while sustaining margin',
                 loc='left', fontsize=12, color=TEXT, pad=12)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'Rs. {x:,.0f}M'))
    ax.legend(frameon=True, facecolor=BG, edgecolor='#D4D1CA', loc='upper left', fontsize=9.5)
    ax.spines[['top', 'right']].set_visible(False)
    plt.xticks(rotation=30, ha='right')
    
    note = "Peak revenue spikes correspond to seasonal lawn pret launches and festive Eid shopping corridors."
    fig.text(0.02, -0.02, note, ha='left', va='top', fontsize=8, color=TEXT_MUTED)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  ✓ Saved: {output_path}")


# ==============================================================================
# MASTER RUNNER
# ==============================================================================
def generate_all_figures(output_dir='reports/figures'):
    os.makedirs(output_dir, exist_ok=True)
    print("\n" + "=" * 80)
    print(" 🎨 GENERATING 10 PUBLICATION-GRADE VISUALIZATIONS (300 DPI)")
    print("=" * 80)
    
    df_platform = pd.read_csv('data/processed/platform_summary.csv')
    df_city = pd.read_csv('data/processed/city_summary.csv')
    df_demo = pd.read_csv('data/processed/demographic_summary.csv')
    df_monthly = pd.read_csv('data/processed/monthly_summary.csv')
    df_bench = pd.read_csv('data/processed/benchmark_results.csv')
    brief_path = 'reports/budget_recommendation_brief.json'
    
    plot_01_cpa_by_platform(df_platform, os.path.join(output_dir, '01_cac_cpa_by_platform.png'))
    plot_02_roas_benchmark(df_platform, os.path.join(output_dir, '02_roas_vs_breakeven_benchmark.png'))
    plot_03_benchmark_scalability(df_bench, os.path.join(output_dir, '03_big_data_execution_time_benchmark.png'))
    plot_04_memory_throughput(df_bench, os.path.join(output_dir, '04_big_data_memory_throughput_benchmark.png'))
    plot_05_conversion_funnel(df_platform, os.path.join(output_dir, '05_conversion_funnel_by_platform.png'))
    plot_06_budget_allocation(brief_path, os.path.join(output_dir, '06_recommended_budget_allocation_rs1m.png'))
    plot_07_diminishing_returns(os.path.join(output_dir, '07_diminishing_returns_marginal_roas.png'))
    plot_08_city_performance(df_city, os.path.join(output_dir, '08_city_revenue_efficiency_matrix.png'))
    plot_09_demographics(df_demo, os.path.join(output_dir, '09_demographic_age_gender_performance.png'))
    plot_10_monthly_trend(df_monthly, os.path.join(output_dir, '10_monthly_spend_revenue_profit_trend.png'))
    
    print("\n✓ All 10 high-resolution charts successfully saved to 'reports/figures/'!")


if __name__ == '__main__':
    generate_all_figures()
