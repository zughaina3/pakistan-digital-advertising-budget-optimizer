"""
Pakistan Digital Advertising Budget Optimizer - Marketing Metrics Engine
========================================================================
Phase 2: Metric Engineering & Multidimensional Performance Analytics

Calculates:
  - CTR (Click-Through Rate, %)
  - CPC (Cost Per Click, Rs.)
  - CPA / CAC (Cost Per Acquisition, Rs.)
  - CVR (Conversion Rate, %)
  - ROAS (Return on Ad Spend, x)
  - CPM (Cost Per Mille, Rs.)
  - AOV (Average Order Value, Rs.)
  - Net Profit / Margin (Revenue - Spend, Rs.)
  
Across:
  - Platform
  - Campaign
  - City (Pakistan regional performance)
  - Demographic Cohorts (Age & Gender)
  - Device
  - Monthly time-series
"""

import os
import argparse
import pandas as pd
import numpy as np


def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute row-level and grouped marketing efficiency metrics."""
    data = df.copy()
    
    # Safe division helpers
    data['ctr'] = np.where(data['impressions'] > 0, (data['clicks'] / data['impressions']) * 100, 0.0).round(2)
    data['cpc'] = np.where(data['clicks'] > 0, data['spend'] / data['clicks'], 0.0).round(2)
    data['cpa'] = np.where(data['conversions'] > 0, data['spend'] / data['conversions'], np.nan).round(2)
    data['cvr'] = np.where(data['clicks'] > 0, (data['conversions'] / data['clicks']) * 100, 0.0).round(2)
    data['roas'] = np.where(data['spend'] > 0, data['revenue'] / data['spend'], 0.0).round(2)
    data['cpm'] = np.where(data['impressions'] > 0, (data['spend'] / data['impressions']) * 1000, 0.0).round(2)
    data['aov'] = np.where(data['conversions'] > 0, data['revenue'] / data['conversions'], 0.0).round(2)
    data['net_profit'] = (data['revenue'] - data['spend']).round(2)
    
    return data


def aggregate_by_dimension(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Aggregate campaign performance by any categorical dimension."""
    grouped = df.groupby(dimension).agg({
        'spend': 'sum',
        'revenue': 'sum',
        'impressions': 'sum',
        'clicks': 'sum',
        'conversions': 'sum'
    }).reset_index()
    
    grouped['ctr'] = ((grouped['clicks'] / grouped['impressions']) * 100).round(2)
    grouped['cpc'] = (grouped['spend'] / grouped['clicks']).round(2)
    grouped['cpa'] = (grouped['spend'] / grouped['conversions']).round(2)
    grouped['cvr'] = ((grouped['conversions'] / grouped['clicks']) * 100).round(2)
    grouped['roas'] = (grouped['revenue'] / grouped['spend']).round(2)
    grouped['cpm'] = ((grouped['spend'] / grouped['impressions']) * 1000).round(2)
    grouped['aov'] = (grouped['revenue'] / grouped['conversions']).round(2)
    grouped['net_profit'] = (grouped['revenue'] - grouped['spend']).round(2)
    
    # Portfolio share percentages
    total_spend = grouped['spend'].sum()
    total_rev = grouped['revenue'].sum()
    grouped['spend_share_pct'] = ((grouped['spend'] / total_spend) * 100).round(1)
    grouped['rev_share_pct'] = ((grouped['revenue'] / total_rev) * 100).round(1)
    
    return grouped


def run_metrics_pipeline(input_csv: str = 'data/raw/campaign_data_100k.csv', output_dir: str = 'data/processed'):
    """Execute complete metrics calculation and export structured analytics tables."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"Loading campaign dataset from {input_csv}...")
    df = pd.read_csv(input_csv)
    print(f"Loaded {len(df):,} records.")
    
    # Platform Summary
    platform_summary = aggregate_by_dimension(df, 'platform').sort_values('roas', ascending=False)
    platform_summary.to_csv(os.path.join(output_dir, 'platform_summary.csv'), index=False)
    
    # Campaign Summary
    campaign_summary = aggregate_by_dimension(df, 'campaign').sort_values('revenue', ascending=False)
    campaign_summary.to_csv(os.path.join(output_dir, 'campaign_summary.csv'), index=False)
    
    # City Summary
    city_summary = aggregate_by_dimension(df, 'city').sort_values('revenue', ascending=False)
    city_summary.to_csv(os.path.join(output_dir, 'city_summary.csv'), index=False)
    
    # Demographic Summary
    df['demographic'] = df['gender'] + ' | ' + df['age']
    demo_summary = aggregate_by_dimension(df, 'demographic').sort_values('roas', ascending=False)
    demo_summary.to_csv(os.path.join(output_dir, 'demographic_summary.csv'), index=False)
    
    # Device Summary
    device_summary = aggregate_by_dimension(df, 'device').sort_values('spend', ascending=False)
    device_summary.to_csv(os.path.join(output_dir, 'device_summary.csv'), index=False)
    
    # Monthly Trend
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
    monthly_summary = aggregate_by_dimension(df, 'month').sort_values('month')
    monthly_summary.to_csv(os.path.join(output_dir, 'monthly_summary.csv'), index=False)
    
    # Platform-Monthly Matrix
    p_month = df.groupby(['month', 'platform']).agg({
        'spend': 'sum', 'revenue': 'sum', 'conversions': 'sum', 'clicks': 'sum', 'impressions': 'sum'
    }).reset_index()
    p_month['roas'] = (p_month['revenue'] / p_month['spend']).round(2)
    p_month['cpa'] = (p_month['spend'] / p_month['conversions']).round(2)
    p_month.to_csv(os.path.join(output_dir, 'platform_monthly_matrix.csv'), index=False)
    
    # Master Metrics Summary
    platform_summary.to_csv(os.path.join(output_dir, 'campaign_metrics_summary.csv'), index=False)
    
    # Print Executive Summary Table
    print("\n" + "=" * 90)
    print(" 🇵🇰 PAKISTAN DIGITAL ADVERTISING PLATFORM EFFICIENCY BENCHMARK")
    print("=" * 90)
    print(f"{'Platform':<12} {'Spend (Rs.)':>14} {'Revenue (Rs.)':>16} {'ROAS':>7} {'CPA (Rs.)':>11} {'CPC (Rs.)':>11} {'CVR %':>7} {'CTR %':>7}")
    print("-" * 90)
    
    total_spend = platform_summary['spend'].sum()
    total_revenue = platform_summary['revenue'].sum()
    total_conversions = platform_summary['conversions'].sum()
    total_clicks = platform_summary['clicks'].sum()
    total_impressions = platform_summary['impressions'].sum()
    
    for _, row in platform_summary.iterrows():
        print(f"{row['platform']:<12} Rs. {row['spend']:>10,.0f} Rs. {row['revenue']:>12,.0f} "
              f"{row['roas']:>6.2f}x Rs. {row['cpa']:>7,.0f} Rs. {row['cpc']:>7.2f} "
              f"{row['cvr']:>6.2f}% {row['ctr']:>6.2f}%")
        
    print("-" * 90)
    blended_roas = total_revenue / total_spend
    blended_cpa = total_spend / total_conversions
    blended_cpc = total_spend / total_clicks
    blended_cvr = (total_conversions / total_clicks) * 100
    blended_ctr = (total_clicks / total_impressions) * 100
    
    print(f"{'BLENDED TOTAL':<12} Rs. {total_spend:>10,.0f} Rs. {total_revenue:>12,.0f} "
          f"{blended_roas:>6.2f}x Rs. {blended_cpa:>7,.0f} Rs. {blended_cpc:>7.2f} "
          f"{blended_cvr:>6.2f}% {blended_ctr:>6.2f}%")
    print("=" * 90)
    print(f"Summary datasets saved to '{output_dir}/'")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run marketing metrics computation engine.")
    parser.add_argument('--input', type=str, default='data/raw/campaign_data_100k.csv',
                        help="Input dataset path")
    args = parser.parse_args()
    run_metrics_pipeline(args.input)
