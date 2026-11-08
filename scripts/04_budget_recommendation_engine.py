"""
Pakistan Digital Advertising Budget Optimizer - Marketing Budget Recommendation Engine
========================================================================================
Phase 2: Algorithmic Ad Budget Optimizer & Reallocation Engine

Solves Management's Core Strategic Question:
  "Where should we spend the next Rs. 1 Million (PKR 1,000,000)?"

Features:
  - Non-linear diminishing marginal returns modeling (Logarithmic saturation curve)
  - Mathematical optimization via scipy.optimize.minimize (SLSQP algorithm)
  - Equalizing marginal returns (dRev/dSpend = lambda) across channels under constraints
  - 3 Distinct Strategic Optimization Formulations:
      1. Balanced Strategic Growth (Recommended) - Constrained portfolio optimization
         with diversification floors (brand discovery & video recall) and exposure caps
      2. ROAS Maximizer - Pure yield maximization (max total revenue / ROAS)
      3. Volume / Scale Maximizer - Maximizes customer acquisition volume (conversions)
         subject to a commercial break-even ROAS floor (>= 2.80x)
  - Data-Driven Regional City Allocation derived from empirical city efficiency & volume
  - Commercial Unit Economics (Delivered revenue, COGS, shipping, true operating profit)
  - Machine-readable JSON output: reports/budget_recommendation_brief.json
"""

import os
import json
import argparse
import numpy as np
import pandas as pd
from scipy.optimize import minimize

PLATFORMS = ['Google', 'Instagram', 'Facebook', 'TikTok', 'YouTube']

# Commercial unit economics in Pakistan D2C retail
COGS_PCT = 0.45                    # Cost of Goods Sold: 45% of gross delivered sales
COURIER_FEE = 220.0                # Forward shipping cost per confirmed order (PKR)
COD_RETURN_RATE = 0.12             # 12% industry baseline for Cash-on-Delivery customer returns
RETURN_LOGISTICS_FEE = 180.0       # Reverse logistics / RTO courier charge per returned parcel (PKR)


def load_channel_benchmarks(data_path: str = 'data/raw/campaign_data_100k.csv') -> dict:
    """
    Calibrate empirical platform efficiency metrics and saturation constants directly from campaign logs.
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Campaign dataset not found at {data_path}. Run generator first.")
        
    df = pd.read_csv(data_path)
    platform_agg = df.groupby('platform').agg({
        'spend': 'sum',
        'revenue': 'sum',
        'clicks': 'sum',
        'impressions': 'sum',
        'conversions': 'sum'
    }).reset_index()
    
    benchmarks = {}
    for _, row in platform_agg.iterrows():
        p = row['platform']
        spend = row['spend']
        rev = row['revenue']
        clicks = row['clicks']
        imp = row['impressions']
        conv = row['conversions']
        
        hist_roas = rev / spend if spend > 0 else 1.0
        hist_cpa = spend / conv if conv > 0 else 500.0
        cpc = spend / clicks if clicks > 0 else 20.0
        ctr = clicks / imp if imp > 0 else 0.02
        cvr = conv / clicks if clicks > 0 else 0.03
        aov = rev / conv if conv > 0 else 2000.0
        
        # Econometric saturation asymptote: market carrying capacity for channel in PKR
        # Calibrated relative to channel historical revenue scale
        alpha = float(rev * 0.40)
        beta = float((hist_roas * 1.25) / alpha)
        
        benchmarks[p] = {
            'hist_roas': round(hist_roas, 2),
            'hist_cpa': round(hist_cpa, 2),
            'cpc': round(cpc, 2),
            'ctr': round(ctr, 4),
            'cvr': round(cvr, 4),
            'aov': round(aov, 2),
            'alpha': alpha,
            'beta': beta
        }
    return benchmarks


def predict_revenue(spend: float, p_cfg: dict) -> float:
    """Concave logarithmic saturation response curve: Revenue = alpha * ln(1 + beta * spend)."""
    if spend <= 0:
        return 0.0
    return float(p_cfg['alpha'] * np.log1p(p_cfg['beta'] * spend))


def predict_conversions(spend: float, p_cfg: dict) -> float:
    """Estimate conversions accounting for spend saturation on CPC and CVR."""
    if spend <= 0:
        return 0.0
    # Saturation factor: marginal cost increases with scale
    scale_factor = 1.0 + 0.12 * np.log1p(spend / 100000.0)
    effective_cpc = p_cfg['cpc'] * scale_factor
    effective_cvr = p_cfg['cvr'] / scale_factor
    clicks = spend / effective_cpc
    return float(clicks * effective_cvr)


def predict_channel_performance(platform: str, spend: float, p_cfg: dict) -> dict:
    """Predict performance metrics and commercial unit economics for a given platform and spend."""
    if spend <= 0:
        return {
            'platform': platform, 'spend': 0.0, 'allocation_pct': 0.0,
            'impressions': 0, 'clicks': 0, 'conversions': 0,
            'revenue': 0.0, 'roas': 0.0, 'cpa': 0.0, 
            'gross_margin': 0.0, 'true_net_profit': 0.0, 'marginal_roas': 0.0
        }
        
    revenue = predict_revenue(spend, p_cfg)
    conversions = max(1, int(round(predict_conversions(spend, p_cfg))))
    
    scale_factor = 1.0 + 0.12 * np.log1p(spend / 100000.0)
    effective_cpc = p_cfg['cpc'] * scale_factor
    clicks = max(conversions, int(round(spend / effective_cpc)))
    impressions = int(round(clicks / p_cfg['ctr'])) if p_cfg['ctr'] > 0 else 0
    
    cpa = round(spend / conversions, 2)
    roas = round(revenue / spend, 2)
    gross_margin = round(revenue - spend, 2)
    
    # Marginal ROAS: dRev/dSpend = alpha * beta / (1 + beta * spend)
    marginal_roas = round((p_cfg['alpha'] * p_cfg['beta']) / (1.0 + p_cfg['beta'] * spend), 3)
    
    # True Net Operating Profit after COGS, Courier shipping, and COD returns
    delivered_revenue = revenue * (1.0 - COD_RETURN_RATE)
    cogs = delivered_revenue * COGS_PCT
    shipping_costs = conversions * (COURIER_FEE + COD_RETURN_RATE * RETURN_LOGISTICS_FEE)
    true_net_profit = round(delivered_revenue - cogs - shipping_costs - spend, 2)
    
    return {
        'platform': platform,
        'spend': round(spend, 2),
        'impressions': impressions,
        'clicks': clicks,
        'conversions': conversions,
        'revenue': round(revenue, 2),
        'roas': roas,
        'cpa': cpa,
        'gross_margin': gross_margin,
        'true_net_profit': true_net_profit,
        'marginal_roas': marginal_roas
    }


def solve_optimization(total_budget: float, strategy: str, benchmarks: dict) -> dict:
    """
    Solve mathematical marketing budget optimization problem using scipy.optimize.minimize (SLSQP).
    """
    platforms = PLATFORMS
    num_p = len(platforms)
    
    # Initial guess: equal split
    x0 = np.array([total_budget / num_p] * num_p)
    
    # Budget conservation constraint: sum(x) == total_budget
    budget_constraint = {'type': 'eq', 'fun': lambda x: np.sum(x) - total_budget}
    constraints = [budget_constraint]
    
    if strategy == 'roas_max':
        # Strategy 1: ROAS Maximizer (Pure Yield)
        # Maximize total gross revenue: min -sum(R_i(x_i))
        bounds = [(0.02 * total_budget, 0.60 * total_budget) for _ in platforms]
        
        def objective(x):
            return -sum(predict_revenue(x[i], benchmarks[platforms[i]]) for i in range(num_p))
            
    elif strategy == 'balanced':
        # Strategy 2: Balanced Strategic Growth (Recommended)
        # Maximize revenue subject to strategic portfolio diversification constraints:
        # Ensures top-of-funnel customer discovery is fed while preventing single-channel saturation.
        bounds = [
            (0.15 * total_budget, 0.40 * total_budget),  # Google (high intent search core)
            (0.15 * total_budget, 0.35 * total_budget),  # Instagram (visual pret & accessories)
            (0.10 * total_budget, 0.25 * total_budget),  # Facebook (retargeting & family demographics)
            (0.08 * total_budget, 0.20 * total_budget),  # TikTok (youth top-of-funnel discovery)
            (0.04 * total_budget, 0.15 * total_budget),  # YouTube (unboxing recall & social proof)
        ]
        
        def objective(x):
            return -sum(predict_revenue(x[i], benchmarks[platforms[i]]) for i in range(num_p))
            
    elif strategy == 'scale_max':
        # Strategy 3: Volume / Conversion Maximizer
        # Maximize total order volume: min -sum(C_i(x_i))
        # Subject to sustaining minimum commercial break-even ROAS (>= 2.80x)
        bounds = [
            (0.10 * total_budget, 0.45 * total_budget),  # Google
            (0.15 * total_budget, 0.45 * total_budget),  # Instagram
            (0.08 * total_budget, 0.30 * total_budget),  # Facebook
            (0.10 * total_budget, 0.30 * total_budget),  # TikTok
            (0.02 * total_budget, 0.15 * total_budget),  # YouTube
        ]
        
        def roas_floor_constraint(x):
            tot_rev = sum(predict_revenue(x[i], benchmarks[platforms[i]]) for i in range(num_p))
            return (tot_rev / total_budget) - 2.80
            
        constraints.append({'type': 'ineq', 'fun': roas_floor_constraint})
        
        def objective(x):
            return -sum(predict_conversions(x[i], benchmarks[platforms[i]]) for i in range(num_p))
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
        
    # Execute SLSQP mathematical optimization
    opt_res = minimize(
        fun=objective,
        x0=x0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'ftol': 1e-9, 'maxiter': 500}
    )
    
    if not opt_res.success:
        print(f"Warning: Optimizer did not fully converge for {strategy}: {opt_res.message}")
        
    optimal_spends = opt_res.x
    
    # Harvest channel results
    channel_results = []
    tot_spend = 0.0
    tot_rev = 0.0
    tot_conv = 0
    tot_clicks = 0
    tot_imp = 0
    tot_gross_margin = 0.0
    tot_true_profit = 0.0
    
    for i, p in enumerate(platforms):
        p_spend = optimal_spends[i]
        res = predict_channel_performance(p, p_spend, benchmarks[p])
        res['allocation_pct'] = round((p_spend / total_budget) * 100, 1)
        channel_results.append(res)
        
        tot_spend += res['spend']
        tot_rev += res['revenue']
        tot_conv += res['conversions']
        tot_clicks += res['clicks']
        tot_imp += res['impressions']
        tot_gross_margin += res['gross_margin']
        tot_true_profit += res['true_net_profit']
        
    blended_roas = round(tot_rev / tot_spend, 2)
    blended_cpa = round(tot_spend / tot_conv, 2)
    
    return {
        'strategy': strategy,
        'optimizer_status': {
            'success': bool(opt_res.success),
            'message': str(opt_res.message),
            'iterations': int(opt_res.nit),
            'algorithm': 'SLSQP (Sequential Least Squares Programming)'
        },
        'total_budget': round(tot_spend, 2),
        'total_revenue': round(tot_rev, 2),
        'blended_roas': blended_roas,
        'blended_cpa': blended_cpa,
        'total_conversions': tot_conv,
        'total_clicks': tot_clicks,
        'total_impressions': tot_imp,
        'gross_margin': round(tot_gross_margin, 2),
        'true_net_profit': round(tot_true_profit, 2),
        'net_profit_margin_pct': round((tot_true_profit / tot_rev) * 100, 1),
        'channels': channel_results
    }


def compute_data_driven_city_allocation(total_budget: float = 1000000.0, data_path: str = 'data/raw/campaign_data_100k.csv') -> pd.DataFrame:
    """
    Derive regional Pakistani city budget allocation directly from empirical city efficiency & volume.
    Combines city order volume share and city ROAS performance score.
    """
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        city_agg = df.groupby('city').agg({
            'spend': 'sum',
            'revenue': 'sum',
            'conversions': 'sum'
        }).reset_index()
        city_agg['roas'] = city_agg['revenue'] / city_agg['spend']
        city_agg['cpa'] = city_agg['spend'] / city_agg['conversions']
        
        tot_orders = city_agg['conversions'].sum()
        city_agg['order_share'] = city_agg['conversions'] / tot_orders
        blended_roas = city_agg['revenue'].sum() / city_agg['spend'].sum()
        city_agg['roas_index'] = city_agg['roas'] / blended_roas
        
        # Empirical Composite Score: Order Share * ROAS Index
        city_agg['composite_score'] = city_agg['order_share'] * city_agg['roas_index']
        total_score = city_agg['composite_score'].sum()
        city_agg['recommended_share'] = city_agg['composite_score'] / total_score
        city_agg = city_agg.sort_values('recommended_share', ascending=False).reset_index(drop=True)
    else:
        # Fallback calibrated weights
        city_agg = pd.DataFrame([
            {'city': 'Karachi', 'recommended_share': 0.35, 'roas': 4.45, 'cpa': 480.0},
            {'city': 'Lahore', 'recommended_share': 0.28, 'roas': 4.38, 'cpa': 495.0},
            {'city': 'Islamabad', 'recommended_share': 0.15, 'roas': 4.52, 'cpa': 510.0},
            {'city': 'Rawalpindi', 'recommended_share': 0.07, 'roas': 4.20, 'cpa': 530.0},
            {'city': 'Faisalabad', 'recommended_share': 0.05, 'roas': 3.90, 'cpa': 560.0},
            {'city': 'Multan', 'recommended_share': 0.04, 'roas': 3.80, 'cpa': 580.0},
            {'city': 'Peshawar', 'recommended_share': 0.03, 'roas': 3.50, 'cpa': 620.0},
            {'city': 'Sialkot', 'recommended_share': 0.02, 'roas': 3.40, 'cpa': 640.0},
            {'city': 'Gujranwala', 'recommended_share': 0.01, 'roas': 3.30, 'cpa': 650.0},
            {'city': 'Quetta', 'recommended_share': 0.01, 'roas': 3.10, 'cpa': 690.0},
        ])
        
    city_rationales = {
        'Karachi': 'Mega-city e-commerce hub, highest COD parcel volume & customer density',
        'Lahore': 'Fashion and lawn pret capital, highest visual lifestyle demand',
        'Islamabad': 'Highest per-capita purchasing power and premium festive collection AOV',
        'Rawalpindi': 'High density twin-city order volume with fast courier transit times',
        'Faisalabad': 'Textile and industrial hub, value-conscious volume buyers',
        'Multan': 'South Punjab regional hub with rising mobile COD adoption',
        'Peshawar': 'Selective demand for festive and unstitched formal wear',
        'Sialkot': 'High export-economy purchasing power with low doorstep rejection',
        'Gujranwala': 'Tier-2 commercial center, responsive to clearance sales',
        'Quetta': 'Emerging regional market with higher delivery lead-times'
    }
    
    rows = []
    for _, r in city_agg.iterrows():
        city_name = r['city']
        share = float(r['recommended_share'])
        city_spend = round(total_budget * share, 2)
        rows.append({
            'city_region': city_name,
            'budget_rs': city_spend,
            'allocation_pct': round(share * 100, 1),
            'empirical_roas': round(float(r['roas']), 2),
            'strategic_rationale': city_rationales.get(city_name, 'Regional digital market')
        })
    return pd.DataFrame(rows)


def run_recommendation_engine(total_budget: float = 1000000.0, data_path: str = 'data/raw/campaign_data_100k.csv', output_dir: str = 'reports'):
    """Generate recommendations, save outputs, and print executive brief."""
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # 1. Calibrate empirical channel parameters from historical data
    print("Calibrating empirical channel saturation parameters from dataset...")
    benchmarks = load_channel_benchmarks(data_path)
    
    # 2. Execute mathematical optimization for 3 strategies using SLSQP
    print("Solving mathematical optimization via scipy.optimize.minimize (SLSQP)...")
    strat_balanced = solve_optimization(total_budget, 'balanced', benchmarks)
    strat_roas = solve_optimization(total_budget, 'roas_max', benchmarks)
    strat_scale = solve_optimization(total_budget, 'scale_max', benchmarks)
    
    # 3. Data-driven Regional City Allocation
    city_df = compute_data_driven_city_allocation(total_budget, data_path)
    city_df.to_csv('data/processed/budget_city_allocation.csv', index=False)
    
    # Format allocation splits for display
    def format_split(strat_dict):
        return ", ".join([f"{ch['platform']} {ch['allocation_pct']:.0f}%" for ch in strat_dict['channels']])
        
    # 4. Compile Strategy Comparison DataFrame
    strategies_summary = [
        {
            'Strategy': 'Balanced Growth (Recommended)',
            'Spend (Rs.)': strat_balanced['total_budget'],
            'Revenue (Rs.)': strat_balanced['total_revenue'],
            'Blended ROAS': f"{strat_balanced['blended_roas']}x",
            'Blended CPA (Rs.)': strat_balanced['blended_cpa'],
            'Conversions': strat_balanced['total_conversions'],
            'Media Margin (Rs.)': strat_balanced['gross_margin'],
            'True Operating Profit (Rs.)': strat_balanced['true_net_profit'],
            'Net Margin %': f"{strat_balanced['net_profit_margin_pct']}%",
            'Allocation Split': format_split(strat_balanced),
            'Optimization Status': f"{strat_balanced['optimizer_status']['algorithm']} ({strat_balanced['optimizer_status']['iterations']} iters)"
        },
        {
            'Strategy': 'ROAS Maximizer',
            'Spend (Rs.)': strat_roas['total_budget'],
            'Revenue (Rs.)': strat_roas['total_revenue'],
            'Blended ROAS': f"{strat_roas['blended_roas']}x",
            'Blended CPA (Rs.)': strat_roas['blended_cpa'],
            'Conversions': strat_roas['total_conversions'],
            'Media Margin (Rs.)': strat_roas['gross_margin'],
            'True Operating Profit (Rs.)': strat_roas['true_net_profit'],
            'Net Margin %': f"{strat_roas['net_profit_margin_pct']}%",
            'Allocation Split': format_split(strat_roas),
            'Optimization Status': f"{strat_roas['optimizer_status']['algorithm']} ({strat_roas['optimizer_status']['iterations']} iters)"
        },
        {
            'Strategy': 'Aggressive Scale',
            'Spend (Rs.)': strat_scale['total_budget'],
            'Revenue (Rs.)': strat_scale['total_revenue'],
            'Blended ROAS': f"{strat_scale['blended_roas']}x",
            'Blended CPA (Rs.)': strat_scale['blended_cpa'],
            'Conversions': strat_scale['total_conversions'],
            'Media Margin (Rs.)': strat_scale['gross_margin'],
            'True Operating Profit (Rs.)': strat_scale['true_net_profit'],
            'Net Margin %': f"{strat_scale['net_profit_margin_pct']}%",
            'Allocation Split': format_split(strat_scale),
            'Optimization Status': f"{strat_scale['optimizer_status']['algorithm']} ({strat_scale['optimizer_status']['iterations']} iters)"
        }
    ]
    strat_df = pd.DataFrame(strategies_summary)
    strat_df.to_csv('data/processed/budget_recommendation_strategies.csv', index=False)
    
    # Export channel breakdown of Recommended Allocation
    rec_channels_df = pd.DataFrame(strat_balanced['channels'])
    rec_channels_df.to_csv('data/processed/budget_recommendations.csv', index=False)
    
    # 5. Save Machine-Readable JSON Brief
    brief_data = {
        'metadata': {
            'project': 'Pakistan Digital Advertising Budget Optimizer (Phase 2)',
            'question': 'Where should we spend the next Rs. 1 Million?',
            'total_budget_pkr': total_budget,
            'currency': 'PKR',
            'optimizer_engine': 'scipy.optimize.minimize (SLSQP)',
            'unit_economics_assumptions': {
                'cogs_pct': COGS_PCT,
                'courier_fee_pkr': COURIER_FEE,
                'cod_return_rate': COD_RETURN_RATE,
                'return_logistics_pkr': RETURN_LOGISTICS_FEE
            }
        },
        'recommended_allocation': strat_balanced,
        'alternative_scenarios': {
            'roas_maximizer': strat_roas,
            'aggressive_scale': strat_scale
        },
        'city_targeting_breakdown': city_df.to_dict(orient='records'),
        'executive_action_plan': [
            f"Allocate Rs. {strat_balanced['channels'][0]['spend']:,.0f} ({strat_balanced['channels'][0]['allocation_pct']}%) to Google Ads targeting high-intent search terms.",
            f"Allocate Rs. {strat_balanced['channels'][1]['spend']:,.0f} ({strat_balanced['channels'][1]['allocation_pct']}%) to Instagram Ads for visual lifestyle & pret collections.",
            f"Allocate Rs. {strat_balanced['channels'][2]['spend']:,.0f} ({strat_balanced['channels'][2]['allocation_pct']}%) to Facebook Ads focusing on family buyers and abandoned cart recovery.",
            f"Allocate Rs. {strat_balanced['channels'][3]['spend']:,.0f} ({strat_balanced['channels'][3]['allocation_pct']}%) to TikTok Ads for low-CPC top-of-funnel Gen Z discovery.",
            f"Allocate Rs. {strat_balanced['channels'][4]['spend']:,.0f} ({strat_balanced['channels'][4]['allocation_pct']}%) to YouTube Ads for brand video recall and creator partnerships.",
            f"Concentrate top geographic spend in Karachi (Rs. {city_df.iloc[0]['budget_rs']:,.0f}) and Lahore (Rs. {city_df.iloc[1]['budget_rs']:,.0f}) to optimize delivery times and minimize COD return rates."
        ]
    }
    
    json_path = os.path.join(output_dir, 'budget_recommendation_brief.json')
    with open(json_path, 'w') as f:
        json.dump(brief_data, f, indent=2)
        
    # 6. Print Executive Brief
    print("\n" + "=" * 105)
    print(" 🎯 MATHEMATICALLY OPTIMIZED BUDGET RECOMMENDATION: ALLOCATION OF RS. 1 MILLION")
    print("=" * 105)
    print(f"Optimizer Engine: {strat_balanced['optimizer_status']['algorithm']} (Converged: {strat_balanced['optimizer_status']['success']})")
    print("-" * 105)
    print(f"{'Platform':<12} {'Share %':>8} {'Spend (Rs.)':>12} {'Expected Rev':>14} {'ROAS':>7} {'Marg. ROAS':>11} {'CPA (Rs.)':>10} {'Orders':>8}")
    print("-" * 105)
    
    for ch in strat_balanced['channels']:
        print(f"{ch['platform']:<12} {ch['allocation_pct']:>7.1f}% Rs. {ch['spend']:>8,.0f} "
              f"Rs. {ch['revenue']:>10,.0f} {ch['roas']:>6.2f}x {ch['marginal_roas']:>10.3f} Rs. {ch['cpa']:>7,.0f} {ch['conversions']:>8,}")
              
    print("-" * 105)
    print(f"{'TOTAL / BLENDED':<12} {'100.0%':>8} Rs. {strat_balanced['total_budget']:>8,.0f} "
          f"Rs. {strat_balanced['total_revenue']:>10,.0f} {strat_balanced['blended_roas']:>6.2f}x "
          f"{'—':>11} Rs. {strat_balanced['blended_cpa']:>7,.0f} {strat_balanced['total_conversions']:>8,}")
    print(f"Gross Media Contribution Margin (Rev - Spend): Rs. {strat_balanced['gross_margin']:,.0f}")
    print(f"True Operating Net Profit (After COGS 45% & COD Logistics): Rs. {strat_balanced['true_net_profit']:,.0f} ({strat_balanced['net_profit_margin_pct']:.1f}% Net Margin)")
    print("=" * 105)
    print(f"Machine-readable recommendation brief saved to '{json_path}'")
    print(f"Strategy comparison saved to 'data/processed/budget_recommendation_strategies.csv'")
    return strat_balanced


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Marketing Budget Recommendation Engine.")
    parser.add_argument('--budget', type=float, default=1000000.0,
                        help="Total marketing budget to allocate in PKR (default: 1,000,000)")
    parser.add_argument('--input', type=str, default='data/raw/campaign_data_100k.csv',
                        help="Path to campaign dataset for calibration")
    args = parser.parse_args()
    run_recommendation_engine(args.budget, data_path=args.input)
