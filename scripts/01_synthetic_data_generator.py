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
import gc
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


def generate_batch(num_records: int, start_date: str = '2025-06-01', days: int = 365, seed: int = None) -> pd.DataFrame:
    """
    Generate a realistic batch of marketing campaign logs with non-linear diminishing returns,
    demographic interactions, and realistic variance.
    """
    if seed is not None:
        np.random.seed(seed)
        
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
    # Range: Rs. 800 to Rs. 28,000 per daily ad campaign placement
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
        p_campaigns = campaigns[mask]
        p_cities = cities[mask]
        p_ages = ages[mask]
        p_genders = genders[mask]
        p_devices = devices[mask]
        
        # ----------------------------------------------------------------------
        # 1. Non-Linear Ad Saturation & Diminishing Marginal Returns
        # As daily spend in an ad placement increases, auction competition rises
        # (marginal CPC increases) and audience ad fatigue sets in (marginal CVR falls).
        # ----------------------------------------------------------------------
        spend_ratio = p_spends / 4000.0
        cpc_saturation_factor = 1.0 + 0.15 * np.log1p(spend_ratio)
        cvr_saturation_factor = 1.0 / (1.0 + 0.12 * np.log1p(spend_ratio))
        
        # Base CPC with auction noise
        effective_cpc = cfg['cpc'] * cpc_saturation_factor * np.random.uniform(0.90, 1.10, size=n)
        p_clicks = np.maximum(1, (p_spends / effective_cpc).astype(int))
        
        # Impressions = Clicks / CTR (with CTR variation)
        ctr_variations = cfg['ctr'] * np.random.uniform(0.88, 1.12, size=n)
        p_impressions = np.maximum(p_clicks, (p_clicks / ctr_variations).astype(int))
        
        # ----------------------------------------------------------------------
        # 2. Demographic x Platform Interactions
        # ----------------------------------------------------------------------
        demog_cvr_mult = np.ones(n, dtype=float)
        demog_aov_mult = np.ones(n, dtype=float)
        
        # Gender interaction
        if platform in ['Instagram', 'Facebook']:
            # Women drive fashion/pret conversions
            demog_cvr_mult = np.where(p_genders == 'Female', demog_cvr_mult * 1.25, demog_cvr_mult * 0.85)
        elif platform == 'Google':
            # Men have higher AOV on search (buying higher-ticket gifts, tech accessories)
            demog_aov_mult = np.where(p_genders == 'Male', demog_aov_mult * 1.15, demog_aov_mult * 1.0)
            
        # Age group interaction
        if platform in ['TikTok', 'Instagram']:
            # Gen Z (18-24) converts heavily on tote bags / student apparel, but lower AOV
            is_genz = (p_ages == '18-24')
            demog_cvr_mult = np.where(is_genz, demog_cvr_mult * 1.28, demog_cvr_mult)
            demog_aov_mult = np.where(is_genz, demog_aov_mult * 0.82, demog_aov_mult)
        elif platform in ['Facebook', 'Google']:
            # Older buyers (35-54) have higher disposable income for luxury / unstitched pret
            is_mature = np.isin(p_ages, ['35-44', '45-54'])
            demog_cvr_mult = np.where(is_mature, demog_cvr_mult * 1.12, demog_cvr_mult)
            demog_aov_mult = np.where(is_mature, demog_aov_mult * 1.25, demog_aov_mult)
            
        # Device interaction (Desktop users have higher purchasing intent and larger carts)
        demog_cvr_mult = np.where(p_devices == 'Desktop', demog_cvr_mult * 1.10, demog_cvr_mult)
        demog_aov_mult = np.where(p_devices == 'Desktop', demog_aov_mult * 1.18, demog_aov_mult)
        
        # ----------------------------------------------------------------------
        # 3. Campaign x Platform Interactions
        # ----------------------------------------------------------------------
        camp_cvr_mult = np.ones(n, dtype=float)
        camp_aov_mult = np.ones(n, dtype=float)
        
        # Retargeting has high intent across all channels
        camp_cvr_mult = np.where(p_campaigns == 'Retargeting_Abandoned_Cart', camp_cvr_mult * 1.75, camp_cvr_mult)
        # Festive Eid collection commands premium pricing
        camp_aov_mult = np.where(p_campaigns == 'Eid_Festive_Collection', camp_aov_mult * 1.35, camp_aov_mult)
        # Tote bags have high student volume, lower AOV
        camp_cvr_mult = np.where(p_campaigns == 'ToteBag_Uni_Special', camp_cvr_mult * 1.20, camp_cvr_mult)
        camp_aov_mult = np.where(p_campaigns == 'ToteBag_Uni_Special', camp_aov_mult * 0.72, camp_aov_mult)
        # Clearance flash sale: high conversions, discounted price
        camp_cvr_mult = np.where(p_campaigns == 'Flash_Clearance_Sale', camp_cvr_mult * 1.35, camp_cvr_mult)
        camp_aov_mult = np.where(p_campaigns == 'Flash_Clearance_Sale', camp_aov_mult * 0.75, camp_aov_mult)

        # ----------------------------------------------------------------------
        # 4. Geographic Purchasing Power & Logistics Friction
        # ----------------------------------------------------------------------
        city_cvr_mult = np.ones(n, dtype=float)
        city_aov_mult = np.ones(n, dtype=float)
        
        # Tier 1 hubs: Karachi, Lahore (high volume, smooth logistics)
        city_cvr_mult = np.where(np.isin(p_cities, ['Karachi', 'Lahore']), 1.08, city_cvr_mult)
        city_aov_mult = np.where(np.isin(p_cities, ['Karachi', 'Lahore']), 1.05, city_aov_mult)
        # Islamabad / Rawalpindi (highest per-capita purchasing power)
        city_aov_mult = np.where(np.isin(p_cities, ['Islamabad', 'Rawalpindi']), 1.18, city_aov_mult)
        city_cvr_mult = np.where(np.isin(p_cities, ['Islamabad', 'Rawalpindi']), 1.05, city_cvr_mult)
        # Tier 2/3 remote cities: higher delivery bounce & conservative checkout
        city_cvr_mult = np.where(np.isin(p_cities, ['Peshawar', 'Quetta', 'Gujranwala']), 0.88, city_cvr_mult)
        city_aov_mult = np.where(np.isin(p_cities, ['Peshawar', 'Quetta', 'Gujranwala']), 0.92, city_aov_mult)

        # ----------------------------------------------------------------------
        # 5. Conversion Generation via Poisson Process
        # Prevents integer truncation bias (which previously made high-spend rows have higher ROAS)
        # ----------------------------------------------------------------------
        cvr_combined = (cfg['cvr'] * cvr_saturation_factor * demog_cvr_mult * camp_cvr_mult * city_cvr_mult)
        cvr_combined = np.clip(cvr_combined * np.random.uniform(0.85, 1.15, size=n), 0.002, 0.25)
        
        expected_conversions = p_clicks * cvr_combined
        p_conversions = np.random.poisson(lam=expected_conversions)
        
        # ----------------------------------------------------------------------
        # 6. Revenue Calculation
        # ----------------------------------------------------------------------
        aov_combined = (cfg['aov'] * demog_aov_mult * camp_aov_mult * city_aov_mult)
        aov_combined = aov_combined * np.random.uniform(0.88, 1.12, size=n)
        
        p_revenues = np.where(
            p_conversions > 0,
            (p_conversions * aov_combined).round(2),
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


def generate_streaming_chunks(total_records: int, chunk_size: int = 1000000, start_seed: int = 100):
    """Generator yielding distinct chunks of records without exhausting RAM."""
    remaining = total_records
    chunk_idx = 0
    while remaining > 0:
        current_chunk_size = min(remaining, chunk_size)
        seed = start_seed + chunk_idx
        chunk_df = generate_batch(current_chunk_size, seed=seed)
        yield chunk_df
        remaining -= current_chunk_size
        chunk_idx += 1
        del chunk_df
        gc.collect()


def generate_10m_dataset(output_path: str = 'data/raw/campaign_data_10m.csv') -> str:
    """Generate Tier 10M (10,000,000 records) to CSV via streaming chunks."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"Generating Tier 10M (10,000,000 records) to {output_path}...")
    first = True
    for chunk in generate_streaming_chunks(10000000, chunk_size=1000000):
        chunk.to_csv(output_path, mode='w' if first else 'a', header=first, index=False)
        first = False
        print("  ✓ Appended 1,000,000 records to disk...")
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"✓ Saved 10M records to {output_path} ({size_mb:.2f} MB)")
    return output_path


def generate_all_datasets(output_dir: str = 'data/raw', include_10m: bool = False):
    """Generate datasets for 10K, 100K, and 1M records (and optionally 10M)."""
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
        df = generate_batch(count, seed=42)
        df.to_csv(filepath, index=False)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"  ✓ Saved to {filepath} ({size_mb:.2f} MB)")
        generated_files[label] = filepath
        
    if include_10m:
        filepath_10m = os.path.join(output_dir, 'campaign_data_10m.csv')
        generate_10m_dataset(filepath_10m)
        generated_files['10m'] = filepath_10m
    
    print("\nDataset generation complete!")
    return generated_files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate synthetic big data for Pakistan Ad Budget Optimizer.")
    parser.add_argument('--tier', type=str, choices=['10k', '100k', '1m', '10m', 'all'], default='all',
                        help="Select tier to generate (10k, 100k, 1m, 10m, or all)")
    args = parser.parse_args()
    
    if args.tier == 'all':
        generate_all_datasets()
    elif args.tier == '10m':
        generate_10m_dataset()
    else:
        counts = {'10k': 10000, '100k': 100000, '1m': 1000000}
        os.makedirs('data/raw', exist_ok=True)
        target = f'data/raw/campaign_data_{args.tier}.csv'
        print(f"Generating {args.tier.upper()} ({counts[args.tier]:,} records)...")
        df = generate_batch(counts[args.tier], seed=42)
        df.to_csv(target, index=False)
        print(f"Saved to {target}")


