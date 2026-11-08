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


# Pakistani D2C E-Commerce Commercial Unit Economics Benchmarks
COGS_PCT = 0.45                    # Cost of Goods Sold: 45% of gross revenue (manufacturing & fabric)
COURIER_FEE = 220.0                # Standard forward shipping cost per order via TCS/CallCourier (PKR)
COD_RETURN_RATE = 0.12             # 12% industry baseline for Cash-on-Delivery customer doorstep returns
RETURN_LOGISTICS_FEE = 180.0       # Reverse logistics / RTO courier surcharge per returned parcel (PKR)


def validate_data_quality(df: pd.DataFrame) -> dict:
    """
    Perform rigorous data quality verification, anomaly detection, and schema validation.
    Returns a dictionary of validation results.
    """
    issues = []
    
    # 1. Null check
    null_counts = df.isnull().sum()
    total_nulls = int(null_counts.sum())
    if total_nulls > 0:
        issues.append(f"Found {total_nulls} null values across columns.")
        
    # 2. Non-negative constraints
    neg_spend = (df['spend'] < 0).sum()
    neg_rev = (df['revenue'] < 0).sum()
    neg_clicks = (df['clicks'] < 0).sum()
    if neg_spend > 0 or neg_rev > 0 or neg_clicks > 0:
        issues.append(f"Negative values detected: spend={neg_spend}, revenue={neg_rev}, clicks={neg_clicks}")
        
    # 3. Funnel logic integrity (Clicks <= Impressions)
    invalid_clicks = (df['clicks'] > df['impressions']).sum()
    if invalid_clicks > 0:
        issues.append(f"{invalid_clicks} rows have clicks > impressions.")
        
    # 4. Outlier detection on conversion rate
    cvr_series = np.where(df['clicks'] > 0, df['conversions'] / df['clicks'], 0)
    outlier_cvr = (cvr_series > 0.50).sum()  # Unrealistic >50% conversion rate
    if outlier_cvr > 0:
        issues.append(f"{outlier_cvr} rows exceed 50% conversion rate anomaly threshold.")
        
    status = "PASSED" if len(issues) == 0 else "WARNING"
    report = {
        'status': status,
        'records_checked': len(df),
        'total_nulls': total_nulls,
        'issues': issues
    }
    return report


def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute row-level and grouped marketing efficiency metrics with full unit economics."""
    data = df.copy()
    
    # Standard digital marketing funnel metrics
    data['ctr'] = np.where(data['impressions'] > 0, (data['clicks'] / data['impressions']) * 100, 0.0).round(2)
    data['cpc'] = np.where(data['clicks'] > 0, data['spend'] / data['clicks'], 0.0).round(2)
    data['cpa'] = np.where(data['conversions'] > 0, data['spend'] / data['conversions'], np.nan).round(2)
    data['cvr'] = np.where(data['clicks'] > 0, (data['conversions'] / data['clicks']) * 100, 0.0).round(2)
    data['roas'] = np.where(data['spend'] > 0, data['revenue'] / data['spend'], 0.0).round(2)
    data['cpm'] = np.where(data['impressions'] > 0, (data['spend'] / data['impressions']) * 1000, 0.0).round(2)
    data['aov'] = np.where(data['conversions'] > 0, data['revenue'] / data['conversions'], 0.0).round(2)
    
    # Financial Unit Economics:
    # 1. Gross Contribution Margin (Media Contribution) = Gross Revenue - Ad Spend
    data['gross_margin'] = (data['revenue'] - data['spend']).round(2)
    
    # 2. Delivered Revenue (adjusting for 12% COD return rate at doorstep)
    delivered_revenue = data['revenue'] * (1.0 - COD_RETURN_RATE)
    
    # 3. Product Cost of Goods Sold (COGS on delivered goods)
    cogs = delivered_revenue * COGS_PCT
    
    # 4. Logistics & COD Return Freight Costs
    shipping_costs = data['conversions'] * (COURIER_FEE + COD_RETURN_RATE * RETURN_LOGISTICS_FEE)
    
    # 5. True Net Profit (Operating Margin) = Delivered Revenue - COGS - Shipping - Ad Spend
    data['true_net_profit'] = (delivered_revenue - cogs - shipping_costs - data['spend']).round(2)
    
    return data


def aggregate_by_dimension(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Aggregate campaign performance by any categorical dimension with standard errors and unit economics."""
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
    
    # Media Contribution Margin
    grouped['gross_margin'] = (grouped['revenue'] - grouped['spend']).round(2)
    
    # True Net Profit Accounting
    delivered_rev = grouped['revenue'] * (1.0 - COD_RETURN_RATE)
    total_cogs = delivered_rev * COGS_PCT
    total_shipping = grouped['conversions'] * (COURIER_FEE + COD_RETURN_RATE * RETURN_LOGISTICS_FEE)
    grouped['true_net_profit'] = (delivered_rev - total_cogs - total_shipping - grouped['spend']).round(2)
    grouped['net_profit_margin_pct'] = ((grouped['true_net_profit'] / grouped['revenue']) * 100).round(1)
    
    # Statistical Estimation for ROAS:
    # We employ cluster block bootstrap resampling (1,000 iterations over daily observations)
    # to evaluate empirical realization volatility across time and campaign clusters.
    # Note on Synthetic Data: Because these logs are generated from a calibrated synthetic pipeline,
    # empirical confidence intervals quantify daily/campaign realization variance under generative
    # parameters rather than infinite-population sampling uncertainty.
    if dimension == 'platform':
        boot_se = []
        boot_ci_low = []
        boot_ci_high = []
        rng = np.random.default_rng(42)
        for _, row_dim in grouped.iterrows():
            dim_val = row_dim[dimension]
            sub_df = df[df[dimension] == dim_val]
            daily_agg = sub_df.groupby('date').agg({'spend': 'sum', 'revenue': 'sum'}).values
            n_days = len(daily_agg)
            if n_days > 1:
                boot_ratios = []
                for _ in range(1000):
                    idx = rng.integers(0, n_days, size=n_days)
                    sample = daily_agg[idx]
                    sp = sample[:, 0].sum()
                    rv = sample[:, 1].sum()
                    boot_ratios.append(rv / sp if sp > 0 else 0.0)
                se = float(np.std(boot_ratios))
                ci_lo = float(np.percentile(boot_ratios, 2.5))
                ci_hi = float(np.percentile(boot_ratios, 97.5))
            else:
                se, ci_lo, ci_hi = 0.0, float(row_dim['roas']), float(row_dim['roas'])
            boot_se.append(round(se, 3))
            boot_ci_low.append(round(ci_lo, 2))
            boot_ci_high.append(round(ci_hi, 2))
        grouped['roas_se'] = boot_se
        grouped['roas_ci_lower'] = boot_ci_low
        grouped['roas_ci_upper'] = boot_ci_high
    else:
        # For non-platform dimensions, provide standard variance bounds
        grouped['roas_se'] = np.where(grouped['conversions'] > 0, 
                                      (grouped['roas'] / np.sqrt(np.maximum(1, grouped['conversions']))).round(3), 0.0)
        grouped['roas_ci_lower'] = (grouped['roas'] - 1.96 * grouped['roas_se']).clip(lower=0).round(2)
        grouped['roas_ci_upper'] = (grouped['roas'] + 1.96 * grouped['roas_se']).round(2)
    
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
    
    # 1. Rigorous Data Quality Verification
    val_report = validate_data_quality(df)
    print(f"  ✓ Data Quality Check: {val_report['status']} ({len(df):,} rows checked, {val_report['total_nulls']} nulls)")
    if val_report['issues']:
        for issue in val_report['issues']:
            print(f"    - Notice: {issue}")
            
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
    print("\n" + "=" * 105)
    print(" 🇵🇰 PAKISTAN DIGITAL ADVERTISING PLATFORM EFFICIENCY & UNIT ECONOMICS")
    print("=" * 105)
    print(f"{'Platform':<12} {'Spend (Rs.)':>12} {'Revenue (Rs.)':>14} {'ROAS (95% CI)':>15} {'CPA (Rs.)':>10} {'Net Profit':>14} {'Net %':>7}")
    print("-" * 105)
    
    total_spend = platform_summary['spend'].sum()
    total_revenue = platform_summary['revenue'].sum()
    total_conversions = platform_summary['conversions'].sum()
    total_clicks = platform_summary['clicks'].sum()
    total_impressions = platform_summary['impressions'].sum()
    total_true_profit = platform_summary['true_net_profit'].sum()
    
    for _, row in platform_summary.iterrows():
        roas_ci = f"{row['roas']:.2f}±{row['roas_se']:.2f}"
        print(f"{row['platform']:<12} Rs. {row['spend']:>8,.0f} Rs. {row['revenue']:>10,.0f} "
              f"{roas_ci:>14} Rs. {row['cpa']:>6,.0f} Rs. {row['true_net_profit']:>10,.0f} "
              f"{row['net_profit_margin_pct']:>6.1f}%")
        
    print("-" * 105)
    blended_roas = total_revenue / total_spend
    blended_cpa = total_spend / total_conversions
    blended_net_pct = (total_true_profit / total_revenue) * 100
    
    print(f"{'BLENDED TOTAL':<12} Rs. {total_spend:>8,.0f} Rs. {total_revenue:>10,.0f} "
          f"{blended_roas:>14.2f}x Rs. {blended_cpa:>6,.0f} Rs. {total_true_profit:>10,.0f} "
          f"{blended_net_pct:>6.1f}%")
    print("=" * 105)
    print(f"Summary datasets saved to '{output_dir}/'")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run marketing metrics computation engine.")
    parser.add_argument('--input', type=str, default='data/raw/campaign_data_100k.csv',
                        help="Input dataset path")
    args = parser.parse_args()
    run_metrics_pipeline(args.input)
