import streamlit as st

def calculate_semi_monthly_tax(taxable_income):
    """Calculates withholding tax based on BIR Semi-Monthly Table (2023-2026)"""
    if taxable_income <= 10417.00:
        return 0.00
    elif taxable_income <= 16666.00:
        return (taxable_income - 10417.00) * 0.15
    elif taxable_income <= 33332.00:
        return 937.50 + (taxable_income - 16667.00) * 0.20
    elif taxable_income <= 83332.00:
        return 4270.70 + (taxable_income - 33333.00) * 0.25
    elif taxable_income <= 333332.00:
        return 16770.70 + (taxable_income - 83333.00) * 0.30
    else:
        return 91770.70 + (taxable_income - 333333.00) * 0.35

def calculate_salary(base_pay, de_minimis, bonuses, nd_days, odd_shift_days, ot_hours, regular_holiday_days, special_holiday_days):
    # Core Rates
    daily_rate = (base_pay * 12) / 261
    hourly_rate = daily_rate / 8
    
    # 1. Total Allowances & Premiums for the month
    nd_pay = nd_days * 8 * hourly_rate * 0.15
    odd_shift_pay = odd_shift_days * 150.00
    ot_pay = ot_hours * hourly_rate * 1.25
    regular_holiday_pay = regular_holiday_days * daily_rate * 1.00
    special_holiday_pay = special_holiday_days * daily_rate * 0.30
    total_holiday_pay = regular_holiday_pay + special_holiday_pay
    
    # Split earnings in half to represent equal semi-monthly cutoffs
    semi_base = base_pay / 2
    semi_nd = nd_pay / 2
    semi_odd = odd_shift_pay / 2
    semi_ot = ot_pay / 2
    semi_holiday = total_holiday_pay / 2
    semi_bonus = bonuses / 2
    semi_de_minimis = de_minimis / 2
    
    semi_gross_earnings = semi_base + semi_nd + semi_odd + semi_ot + semi_holiday + semi_bonus
    total_gross_taxable = semi_gross_earnings * 2
    
    # 2. Statutory Deductions (Deducted ONCE per month)
    # SSS Employee Share: Corrected to 4.5% of MSC (Max MSC is Php 35,000 for 2026)
    msc = min(base_pay, 35000.00)
    sss_contribution = msc * 0.045 
    philhealth = base_pay * 0.025  # Employee share is 2.5%
    pag_ibig = 200.00  # Statutory maximum cap
    total_gov_deductions = sss_contribution + philhealth + pag_ibig
    
    # 3. First Cutoff Computation (Includes all Gov Deductions)
    taxable_income_c1 = semi_gross_earnings - total_gov_deductions
    # Ensure taxable income doesn't fall below zero for tax calculation
    tax_c1 = calculate_semi_monthly_tax(max(taxable_income_c1, 0)) 
    net_c1 = semi_gross_earnings - total_gov_deductions - tax_c1 + semi_de_minimis
    
    # 4. Second Cutoff Computation (No Gov Deductions)
    taxable_income_c2 = semi_gross_earnings
    tax_c2 = calculate_semi_monthly_tax(max(taxable_income_c2, 0))
    net_c2 = semi_gross_earnings - tax_c2 + semi_de_minimis
    
    return {
        "semi_base": semi_base,
        "semi_extras": semi_nd + semi_odd + semi_ot + semi_holiday + semi_bonus,
        "semi_de_minimis": semi_de_minimis,
        "total_gross_taxable": total_gross_taxable,
        "sss": sss_contribution,
        "philhealth": philhealth,
        "pag_ibig": pag_ibig,
        "total_gov_deductions": total_gov_deductions,
        "taxable_income_c1": taxable_income_c1,
        "tax_c1": tax_c1,
        "net_c1": net_c1,
        "taxable_income_c2": taxable_income_c2,
        "tax_c2": tax_c2,
        "net_c2": net_c2,
        "total_net": net_c1 + net_c2
    }

# --- STREAMLIT UI LAYOUT ---

st.set_page_config(page_title="REPH Transparent Salary Calculator", layout="wide")

st.title("Semi-Monthly Salary Calculator")
st.markdown("Calculates dual-cutoff payouts incorporating all statutory deductions in the 1st Cutoff.")

# Input Columns
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Core & Allowances (Monthly Total)")
    base_pay = st.number_input("Monthly Base Pay (Php)", value=23000.00, step=500.00)
    de_minimis = st.number_input("De Minimis Benefit (Php)", value=1000.00, step=250.00)
    bonuses = st.number_input("Bonuses / Incentives (Php)", value=0.00, step=500.00)

with col2:
    st.subheader("Shift Adjustments (Monthly Total)")
    nd_days = st.number_input("Night Differential Days (9PM-6AM)", min_value=0, value=0, help="Assumes 8 hours of ND per shift.")
    odd_shift_days = st.number_input("Odd Shift Days (11PM-5AM)", min_value=0, value=0)
    ot_hours = st.number_input("Regular Overtime Hours", min_value=0.0, value=0.0, step=1.0)

with col3:
    st.subheader("Holiday Premiums (Monthly Total)")
    regular_holiday_days = st.number_input("Regular Holidays Worked (Days)", min_value=0, value=0, step=1)
    special_holiday_days = st.number_input("Special Non-Working Days Worked (Days)", min_value=0, value=0, step=1)

# Run Calculation
if st.button("Calculate Salary", type="primary"):
    d = calculate_salary(base_pay, de_minimis, bonuses, nd_days, odd_shift_days, ot_hours, regular_holiday_days, special_holiday_days)
    
    st.divider()
    
    # High-level Output
    st.subheader("Payout Summary")
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric("1st Cutoff Net Pay (w/ Gov Deductions)", f"Php {d['net_c1']:,.2f}")
    res_col2.metric("2nd Cutoff Net Pay", f"Php {d['net_c2']:,.2f}")
    res_col3.metric("Total Monthly Net Pay", f"Php {d['total_net']:,.2f}")
    
    # Transparent Breakdown
    st.markdown("### 🧮 Transparent Cutoff Breakdown")
    
    breakdown_col1, breakdown_col2 = st.columns(2)
    
    with breakdown_col1:
        st.markdown("#### 📅 1st Cutoff (15th)")
        st.write(f"Semi-Monthly Base Pay: `Php {d['semi_base']:,.2f}`")
        st.write(f"Allowances, OT, Holidays (Split): `+ Php {d['semi_extras']:,.2f}`")
        st.write(f"De Minimis Benefit (Split): `+ Php {d['semi_de_minimis']:,.2f}`")
        st.markdown("---")
        st.markdown("**Deductions:**")
        st.write(f"SSS Contribution: `- Php {d['sss']:,.2f}`")
        st.write(f"PhilHealth (2.5%): `- Php {d['philhealth']:,.2f}`")
        st.write(f"Pag-IBIG: `- Php {d['pag_ibig']:,.2f}`")
        st.write(f"Withholding Tax: `- Php {d['tax_c1']:,.2f}`")
        st.success(f"**Net Payout: Php {d['net_c1']:,.2f}**")
        
    with breakdown_col2:
        st.markdown("#### 📅 2nd Cutoff (30th)")
        st.write(f"Semi-Monthly Base Pay: `Php {d['semi_base']:,.2f}`")
        st.write(f"Allowances, OT, Holidays (Split): `+ Php {d['semi_extras']:,.2f}`")
        st.write(f"De Minimis Benefit (Split): `+ Php {d['semi_de_minimis']:,.2f}`")
        st.markdown("---")
        st.markdown("**Deductions:**")
        st.write(f"SSS Contribution: `- Php 0.00`")
        st.write(f"PhilHealth (2.5%): `- Php 0.00`")
        st.write(f"Pag-IBIG: `- Php 0.00`")
        st.write(f"Withholding Tax: `- Php {d['tax_c2']:,.2f}`")
        st.success(f"**Net Payout: Php {d['net_c2']:,.2f}**")
