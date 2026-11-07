"""
Pakistan Digital Advertising Budget Optimizer - Synthetic Big Data Generator
============================================================================
Phase 2: Digital Marketing Intelligence & Ad Budget Optimization
Generates realistic multi-tier digital advertising campaign datasets for Pakistani
D2C e-commerce brands (apparel, pret, tote bags, accessories) across:
  - Facebook, Instagram, Google, TikTok, YouTube
  - Major Pakistani cities: Karachi, Lahore, Islamabad, Rawalpindi, Faisalabad, etc.
  - Realistic currency: Pakistani Rupee (PKR / Rs.)
  - Tiers: 10,000 | 100,000 | 1,000,000 | 10,000,000 (streaming generator)
"""

import os
import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set deterministic seed for reproducibility
np.random.seed(42)

PLATFORMS = ['Google', 'Instagram', 'Facebook', 'TikTok', 'YouTube']

CAMPAIGNS = [
    'Lawn_Summer_Pret_2026',
    'ToteBag_Uni_Special',
    'Eid_Festive_Collection',
    'Retargeting_Abandoned_Cart',
    'Flash_Clearance_Sale'
]

CITIES = [
    'Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 
    'Faisalabad', 'Multan', 'Peshawar', 'Sialkot', 'Gujranwala', 'Quetta'
]
# City population & economic weights in Pakistan e-commerce
CITY_WEIGHTS = [0.35, 0.28, 0.14, 0.07, 0.05, 0.04, 0.03, 0.02, 0.01, 0.01]

AGE_GROUPS = ['18-24', '25-34', '35-44', '45-54']
AGE_WEIGHTS = [0.35, 0.40, 0.18, 0.07]

GENDERS = ['Female', 'Male', 'Unisex']
GENDER_WEIGHTS = [0.65, 0.25, 0.10]  # Female-skewed for pret & fashion

DEVICES = ['Mobile', 'Desktop', 'Tablet']
DEVICE_WEIGHTS = [0.88, 0.10, 0.02]  # Heavy mobile e-commerce usage in Pakistan

# Calibrated unit economic baselines in PKR (Rs.)
# Paid marketing funnel: Spend -> Clicks (via CPC) -> Impressions (via CTR) -> Conversions (via CVR) -> Revenue (via AOV)
PLATFORM_PROFILES = {
    'Google': {
        'cpc': 28.50,       # High intent search & shopping keywords
        'ctr': 0.034,       # Solid search click-through rate
        'cvr': 0.046,       # High intent to buy stitched pret & accessories
        'aov': 2600.0,      # High basket value
        'spend_weight': 0.32
    },
    'Instagram': {
        'cpc': 18.20,       # Visual feeds, reels, and stories
        'ctr': 0.026,       # Strong lifestyle engagement
        'cvr': 0.038,       # High impulse purchases (tote bags & lawn)
        'aov': 1850.0,      # Moderate-to-high basket value
        'spend_weight': 0.28
    },
    'Facebook': {
        'cpc': 22.00,       # Mature demographic feed placements
        'ctr': 0.018,       # Moderate CTR
        'cvr': 0.029,       # Moderate conversion rate
        'aov': 2100.0,      # Family & unstitched fabrics
        'spend_weight': 0.20
    },
    'TikTok': {
        'cpc': 8.50,        # Cheap short-form video clicks
        'ctr': 0.022,       # High video curiosity taps
        'cvr': 0.016,       # Lower conversion intent among young users
        'aov': 1150.0,      # Entry-level accessories & tote bags
        'spend_weight': 0.12
    },
    'YouTube': {
        'cpc': 32.00,       # Video ads & bumper placements
        'ctr': 0.011,       # Lower click-through on video
        'cvr': 0.021,       # Brand awareness / top-of-funnel
        'aov': 2800.0,      # Brand unboxing viewers
        'spend_weight': 0.08
    }
}


def generate_batch(num_records: int, start_date: str = '2025-06-01', days: int = 365) -> pd.DataFrame:
    """Generate a realistic batch of marketing campaign logs."""
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    date_offsets = np.random.randint(0, days, size=num_records)
    dates = [start_dt + timedelta(days=int(d)) for d in date_offsets]
    
    # Assign platforms according to real-world Pakistani brand media budget split
    platform_probs = [PLATFORM_PROFILES[p]['spend_weight'] for p in PLATFORMS]
    platforms = np.random.choice(PLATFORMS, size=num_records, p=platform_probs)
    
    campaigns = np.random.choice(CAMPAIGNS, size=num_records, p=[0.30, 0.25, 0.20, 0.15, 0.10])
    cities = np.random.choice(CITIES, size=num_records, p=CITY_WEIGHTS)
    ages = np.random.choice(AGE_GROUPS, size=num_records, p=AGE_WEIGHTS)
    genders = np.random.choice(GENDERS, size=num_records, p=GENDER_WEIGHTS)
    devices = np.random.choice(DEVICES, size=num_records, p=DEVICE_WEIGHTS)
    
    # Daily budget spends per ad set (in PKR)
    # Range: Rs. 1,000 to Rs. 25,000 per daily ad campaign placement
    base_spends = np.random.exponential(scale=3500, size=num_records) + 800
    spends = np.clip(base_spends, 800, 30000).round(2)
    
    impressions = np.zeros(num_records, dtype=int)
    clicks = np.zeros(num_records, dtype=int)
    conversions = np.zeros(num_records, dtype=int)
    revenues = np.zeros(num_records, dtype=float)
    
    for platform in PLATFORMS:
        mask = (platforms == platform)
        n = np.sum(mask)
        if n == 0:
            continue
        
        cfg = PLATFORM_PROFILES[platform]
        p_spends = spends[mask]
        
        # 1. Clicks = Spend / CPC
        cpc_variations = cfg['cpc'] * np.random.uniform(0.88, 1.12, size=n)
        p_clicks = np.maximum(1, (p_spends / cpc_variations).astype(int))
        
        # 2. Impressions = Clicks / CTR
        ctr_variations = cfg['ctr'] * np.random.uniform(0.85, 1.15, size=n)
        p_impressions = np.maximum(p_clicks, (p_clicks / ctr_variations).astype(int))
        
        # 3. Conversions = Clicks * CVR
        cvr_variations = cfg['cvr'] * np.random.uniform(0.80, 1.20, size=n)
        
        # Campaign modifier: Retargeting has 1.6x higher CVR; Clearance has 1.3x higher CVR
        camp_slice = campaigns[mask]
        camp_mult = np.where(camp_slice == 'Retargeting_Abandoned_Cart', 1.60, 
                    np.where(camp_slice == 'Flash_Clearance_Sale', 1.30, 1.0))
        
        p_conversions = np.maximum(0, (p_clicks * cvr_variations * camp_mult).astype(int))
        
        # 4. Revenue = Conversions * AOV
        aov_variations = cfg['aov'] * np.random.uniform(0.85, 1.15, size=n)
        
        # City modifier: Karachi and Islamabad have slightly higher purchasing power (+8%)
        city_slice = cities[mask]
        city_mult = np.where(np.isin(city_slice, ['Karachi', 'Islamabad', 'Lahore']), 1.08, 0.94)
        
        p_revenues = np.where(
            p_conversions > 0,
            (p_conversions * aov_variations * city_mult).round(2),
            0.0
        )
        
        impressions[mask] = p_impressions
        clicks[mask] = p_clicks
        conversions[mask] = p_conversions
        revenues[mask] = p_revenues
    
    df = pd.DataFrame({
        'date': [d.strftime('%Y-%m-%d') for d in dates],
        'campaign': campaigns,
        'platform': platforms,
        'impressions': impressions,
        'clicks': clicks,
        'spend': spends,
        'conversions': conversions,
        'revenue': revenues,
        'age': ages,
        'gender': genders,
        'city': cities,
        'device': devices
    })
    
    # Sort chronologically
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return df


def generate_all_datasets(output_dir: str = 'data/raw'):
    """Generate datasets for 10K, 100K, and 1M records."""
    os.makedirs(output_dir, exist_ok=True)
    
    tiers = {
        '10k': 10000,
        '100k': 100000,
        '1m': 1000000
    }
    
    generated_files = {}
    for label, count in tiers.items():
        filepath = os.path.join(output_dir, f'campaign_data_{label}.csv')
        print(f"Generating Tier {label.upper()} ({count:,} records)...")
        df = generate_batch(count)
        df.to_csv(filepath, index=False)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"  ✓ Saved to {filepath} ({size_mb:.2f} MB)")
        generated_files[label] = filepath
    
    print("\nDataset generation complete!")
    return generated_files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate synthetic big data for Pakistan Ad Budget Optimizer.")
    parser.add_argument('--tier', type=str, choices=['10k', '100k', '1m', 'all'], default='all',
                        help="Select tier to generate (10k, 100k, 1m, or all)")
    args = parser.parse_args()
    
    if args.tier == 'all':
        generate_all_datasets()
    else:
        counts = {'10k': 10000, '100k': 100000, '1m': 1000000}
        os.makedirs('data/raw', exist_ok=True)
        target = f'data/raw/campaign_data_{args.tier}.csv'
        print(f"Generating {args.tier.upper()} ({counts[args.tier]:,} records)...")
        df = generate_batch(counts[args.tier])
        df.to_csv(target, index=False)
        print(f"Saved to {target}")
