#!/usr/bin/env python3
"""
Real Estate Valuation Formulas
Based on: The Appraisal of Real Estate, 15th Edition (Appraisal Institute)

This module implements industry-standard valuation formulas for:
- Direct Capitalization
- Yield Capitalization (DCF)
- Gross Rent Multiplier (GRM)
- Net Operating Income (NOI)
- Present Value calculations

Reference: Pages 437-490 of the textbook
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class PropertyFinancials:
    """Financial data for a property."""
    gross_potential_income: float  # Total rent if 100% occupied
    vacancy_rate: float            # e.g., 0.05 for 5%
    operating_expenses: float      # Annual operating costs
    purchase_price: float          # Property value/price
    
    @property
    def effective_gross_income(self) -> float:
        """EGI = Potential Income - Vacancy Loss"""
        return self.gross_potential_income * (1 - self.vacancy_rate)
    
    @property
    def net_operating_income(self) -> float:
        """NOI = Effective Gross Income - Operating Expenses"""
        return self.effective_gross_income - self.operating_expenses


# =============================================================================
# DIRECT CAPITALIZATION (Chapter 24)
# =============================================================================

def capitalization_rate(noi: float, value: float) -> float:
    """
    Calculate the capitalization rate (cap rate).
    
    Formula: R = NOI / V
    
    Args:
        noi: Net Operating Income (annual)
        value: Property value or sale price
    
    Returns:
        Capitalization rate as decimal (e.g., 0.065 for 6.5%)
    
    Reference: Page 446 - "The overall capitalization rate is the ratio of 
               net operating income to value."
    """
    if value <= 0:
        return 0
    return noi / value


def value_from_cap_rate(noi: float, cap_rate: float) -> float:
    """
    Calculate property value using direct capitalization.
    
    Formula: V = NOI / R
    
    Args:
        noi: Net Operating Income (annual)
        cap_rate: Capitalization rate as decimal
    
    Returns:
        Property value
    
    Reference: Page 445 - "In direct capitalization, the value is derived
               by dividing the single year's income by an appropriate rate."
    """
    if cap_rate <= 0:
        return 0
    return noi / cap_rate


def noi_from_value(value: float, cap_rate: float) -> float:
    """
    Calculate NOI from value and cap rate.
    
    Formula: NOI = V × R
    """
    return value * cap_rate


# =============================================================================
# GROSS RENT MULTIPLIER (Chapter 24)
# =============================================================================

def gross_rent_multiplier(sale_price: float, gross_annual_rent: float) -> float:
    """
    Calculate Gross Rent Multiplier (GRM).
    
    Formula: GRM = Sale Price / Gross Annual Rent
    
    Args:
        sale_price: Property sale price
        gross_annual_rent: Annual rental income
    
    Returns:
        Gross Rent Multiplier
    
    Reference: Page 486 - "The ratio of the sale price of a property to its
               anticipated next year's income... is the gross income multiplier."
    """
    if gross_annual_rent <= 0:
        return 0
    return sale_price / gross_annual_rent


def value_from_grm(gross_annual_rent: float, grm: float) -> float:
    """
    Calculate property value using GRM.
    
    Formula: V = Gross Annual Rent × GRM
    """
    return gross_annual_rent * grm


def monthly_grm(sale_price: float, monthly_rent: float) -> float:
    """
    Calculate Monthly Gross Rent Multiplier.
    
    Common in residential markets.
    """
    if monthly_rent <= 0:
        return 0
    return sale_price / monthly_rent


# =============================================================================
# YIELD CAPITALIZATION / DCF (Chapter 25)
# =============================================================================

def present_value(future_value: float, rate: float, periods: int) -> float:
    """
    Calculate present value of a future payment.
    
    Formula: PV = FV / (1 + i)^n
    
    Args:
        future_value: Future payment amount
        rate: Discount rate per period (as decimal)
        periods: Number of periods
    
    Returns:
        Present value
    
    Reference: Page 489 - "The standard formula for discounting future value 
               to present value is: PV = FV / (1 + i)^n"
    """
    if rate <= -1 or periods < 0:
        return 0
    return future_value / ((1 + rate) ** periods)


def discounted_cash_flow(
    cash_flows: List[float],
    discount_rate: float,
    reversion: Optional[float] = None
) -> float:
    """
    Discounted Cash Flow (DCF) Analysis.
    
    Formula: PV = Σ(CF_n / (1 + Y)^n) + Reversion / (1 + Y)^n
    
    Args:
        cash_flows: List of periodic cash flows (typically annual)
        discount_rate: Yield rate (property yield rate Y_o)
        reversion: End-of-period sale value (optional)
    
    Returns:
        Present value of all cash flows
    
    Reference: Page 490 - "In DCF analysis, the yield formula is expressed as:
               PV = CF1/(1+Y) + CF2/(1+Y)^2 + ... + CFn/(1+Y)^n"
    """
    total_pv = 0
    
    # Discount each cash flow
    for n, cf in enumerate(cash_flows, start=1):
        total_pv += present_value(cf, discount_rate, n)
    
    # Add discounted reversion if provided
    if reversion is not None and len(cash_flows) > 0:
        total_pv += present_value(reversion, discount_rate, len(cash_flows))
    
    return total_pv


def net_present_value(
    initial_investment: float,
    cash_flows: List[float],
    discount_rate: float,
    reversion: Optional[float] = None
) -> float:
    """
    Calculate Net Present Value (NPV).
    
    Formula: NPV = DCF - Initial Investment
    """
    pv = discounted_cash_flow(cash_flows, discount_rate, reversion)
    return pv - initial_investment


def yield_rental(
    monthly_rent: float,
    purchase_price: float,
    annual_expenses_ratio: float = 0.30
) -> float:
    """
    Calculate rental yield (simplified).
    
    Formula: Yield = (Annual Rent - Expenses) / Purchase Price
    
    Args:
        monthly_rent: Monthly rental income
        purchase_price: Property purchase price
        annual_expenses_ratio: Operating expenses as ratio of rent (default 30%)
    
    Returns:
        Rental yield as percentage (e.g., 5.5 for 5.5%)
    """
    if purchase_price <= 0:
        return 0
    
    annual_rent = monthly_rent * 12
    net_income = annual_rent * (1 - annual_expenses_ratio)
    return (net_income / purchase_price) * 100


# =============================================================================
# INVESTMENT SCORING (Integration with scoring engine)
# =============================================================================

def calculate_investment_score(
    monthly_rent: float,
    purchase_price: float,
    market_cap_rate: float = 0.05,
    growth_forecast_5yr: float = 15.0,
    vacancy_rate: float = 0.05
) -> Dict[str, float]:
    """
    Calculate comprehensive investment score for a property.
    
    Uses multiple valuation methods from the textbook to derive a 0-100 score.
    
    Args:
        monthly_rent: Monthly rental income
        purchase_price: Property value
        market_cap_rate: Market capitalization rate (default 5%)
        growth_forecast_5yr: 5-year price growth forecast (%)
        vacancy_rate: Vacancy rate (default 5%)
    
    Returns:
        Dictionary with all calculated metrics and final score
    """
    annual_rent = monthly_rent * 12
    
    # 1. Gross Rent Multiplier
    grm = gross_rent_multiplier(purchase_price, annual_rent)
    grm_score = max(0, min(100, (25 - grm) * 5))  # Lower GRM = better (15-25 range)
    
    # 2. Rental Yield
    rental_yield_pct = yield_rental(monthly_rent, purchase_price)
    yield_score = min(100, rental_yield_pct * 15)  # 6.5% yield = 97.5 score
    
    # 3. Cap Rate Implied Value vs Actual
    estimated_noi = annual_rent * (1 - vacancy_rate) * 0.70  # 30% expense ratio
    implied_value = value_from_cap_rate(estimated_noi, market_cap_rate)
    value_ratio = implied_value / purchase_price if purchase_price > 0 else 1
    value_score = min(100, value_ratio * 50)  # 2x undervalued = 100
    
    # 4. Growth Potential
    growth_score = min(100, growth_forecast_5yr * 3)  # 33% growth = 100
    
    # 5. 5-Year DCF Analysis
    projected_noi = [estimated_noi * (1.02 ** n) for n in range(5)]  # 2% NOI growth
    reversion = purchase_price * (1 + growth_forecast_5yr / 100)
    dcf_value = discounted_cash_flow(projected_noi, 0.08, reversion)
    dcf_ratio = dcf_value / purchase_price if purchase_price > 0 else 1
    dcf_score = min(100, (dcf_ratio - 0.8) * 250)  # Score based on value ratio
    
    # Weighted composite score
    composite_score = (
        grm_score * 0.15 +
        yield_score * 0.30 +
        value_score * 0.20 +
        growth_score * 0.15 +
        dcf_score * 0.20
    )
    
    return {
        "gross_rent_multiplier": round(grm, 2),
        "rental_yield_pct": round(rental_yield_pct, 2),
        "implied_value": round(implied_value),
        "dcf_value_5yr": round(dcf_value),
        "value_ratio": round(value_ratio, 2),
        "grm_score": round(grm_score),
        "yield_score": round(yield_score),
        "value_score": round(value_score),
        "growth_score": round(growth_score),
        "dcf_score": round(dcf_score),
        "investment_score": round(composite_score)
    }


def calculate_investment_difficulty(
    monthly_rent: float,
    purchase_price: float,
    safety_score: float = 50,
    yield_estimate: float = 5.0,
    growth_forecast_5yr: float = 15.0,
    vacancy_rate: float = 0.05,
    area_name: str = ""
) -> Dict:
    """
    Calculate the Investment Difficulty Rating for a property.
    
    Based on The Appraisal of Real Estate, 15th Edition concepts:
    - Market risk (volatility, liquidity)
    - Operational complexity (management intensity)
    - Financial risk (leverage, cash flow stability)
    - Location risk (crime, economic factors)
    
    Returns:
        Dictionary with difficulty level (1-5 stars), factors, and description
    """
    difficulty_factors = []
    difficulty_score = 0  # 0-100, higher = more difficult
    
    # 1. ENTRY BARRIER (High price = harder to enter)
    if purchase_price > 500000:
        difficulty_score += 20
        difficulty_factors.append("High entry capital required (£500k+)")
    elif purchase_price > 350000:
        difficulty_score += 10
        difficulty_factors.append("Moderate capital barrier (£350k+)")
    else:
        difficulty_factors.append("Lower entry capital (sub-£350k)")
    
    # 2. YIELD-TO-PRICE RATIO (Low yield = harder to profit)
    yield_pct = yield_rental(monthly_rent, purchase_price)
    if yield_pct < 4:
        difficulty_score += 25
        difficulty_factors.append(f"Challenging yield ({yield_pct:.1f}% < 4% threshold)")
    elif yield_pct < 5:
        difficulty_score += 15
        difficulty_factors.append(f"Below-market yield ({yield_pct:.1f}%)")
    else:
        difficulty_factors.append(f"Strong yield ({yield_pct:.1f}%)")
    
    # 3. SAFETY/LOCATION RISK
    if safety_score < 45:
        difficulty_score += 20
        difficulty_factors.append("Higher location risk (safety concerns)")
    elif safety_score < 60:
        difficulty_score += 10
        difficulty_factors.append("Moderate location profile")
    else:
        difficulty_factors.append("Low location risk (safe area)")
    
    # 4. GROWTH UNCERTAINTY
    if growth_forecast_5yr > 25:
        difficulty_score += 15  # High growth = high volatility
        difficulty_factors.append("High volatility market (>25% projected growth)")
    elif growth_forecast_5yr < 10:
        difficulty_score += 10
        difficulty_factors.append("Slow growth area (<10% forecast)")
    else:
        difficulty_factors.append("Stable growth trajectory")
    
    # 5. VACANCY RISK
    if vacancy_rate > 0.08:
        difficulty_score += 15
        difficulty_factors.append("Higher vacancy risk (>8%)")
    elif vacancy_rate > 0.05:
        difficulty_score += 5
        difficulty_factors.append("Standard vacancy profile")
    else:
        difficulty_factors.append("Low vacancy risk (<5%)")
    
    # Convert score to star rating (1-5)
    if difficulty_score >= 70:
        stars = 5
        level = "Expert"
        description = "Complex investment requiring deep market knowledge and significant capital reserves"
    elif difficulty_score >= 55:
        stars = 4
        level = "Advanced"
        description = "Challenging investment with multiple risk factors to manage"
    elif difficulty_score >= 40:
        stars = 3
        level = "Intermediate"
        description = "Moderate complexity suitable for experienced investors"
    elif difficulty_score >= 25:
        stars = 2
        level = "Beginner-Friendly"
        description = "Manageable investment with favorable fundamentals"
    else:
        stars = 1
        level = "Entry-Level"
        description = "Low-complexity investment ideal for first-time investors"
    
    return {
        "difficulty_stars": stars,
        "difficulty_level": level,
        "difficulty_score": difficulty_score,
        "difficulty_description": description,
        "difficulty_factors": difficulty_factors[:3],  # Top 3 factors
        "area_name": area_name
    }


# =============================================================================
# TEST / DEMO
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Real Estate Valuation Formulas - Test")
    print("Based on: The Appraisal of Real Estate, 15th Edition")
    print("=" * 80)
    print()
    
    # Test property: E6 East Ham
    monthly_rent = 1750
    purchase_price = 390000
    
    print(f"Test Property: East Ham (E6)")
    print(f"  Monthly Rent: £{monthly_rent:,}")
    print(f"  Purchase Price: £{purchase_price:,}")
    print()
    
    results = calculate_investment_score(
        monthly_rent=monthly_rent,
        purchase_price=purchase_price,
        growth_forecast_5yr=22.0
    )
    
    print("Valuation Metrics:")
    print(f"  Gross Rent Multiplier: {results['gross_rent_multiplier']}")
    print(f"  Rental Yield: {results['rental_yield_pct']}%")
    print(f"  Implied Value (5% cap): £{results['implied_value']:,}")
    print(f"  5-Year DCF Value: £{results['dcf_value_5yr']:,}")
    print(f"  Value Ratio: {results['value_ratio']}")
    print()
    
    print("Component Scores (0-100):")
    print(f"  GRM Score: {results['grm_score']}")
    print(f"  Yield Score: {results['yield_score']}")
    print(f"  Value Score: {results['value_score']}")
    print(f"  Growth Score: {results['growth_score']}")
    print(f"  DCF Score: {results['dcf_score']}")
    print()
    
    print(f"INVESTMENT SCORE: {results['investment_score']}/100")
    print("=" * 80)
