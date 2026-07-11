import streamlit as st

def calculate_salary(base_pay, de_minimis, bonuses, nd_days, odd_shift_days, ot_hours, regular_holiday_days, special_holiday_days):
    # Core Rates
    daily_rate = (base_pay * 12) / 261
    hourly_rate = daily_rate / 8
    
    # 1. Allowances & Premiums
    # A 9PM-6AM shift contains exactly 8 hours of ND (10PM to 6AM window)
    nd_pay = nd_days * 8 * hourly_rate * 0.15
    odd_shift_pay = odd_shift_days * 150.00
    
    # Overtime Pay (Regular OT at 125%)
    ot_pay = ot_hours * hourly_rate * 1.25
    
    # Holiday Premium Calculations (Statutory)
    regular_holiday_pay = regular_holiday_days * daily_rate * 1.00  # Extra 100% on top of base
    special_holiday_pay = special_holiday_days * daily_rate * 0.30  # Extra 30% on top of base
    total_holiday_pay = regular_holiday_pay + special_holiday_pay
        
    # 2. Gross Taxable Income Calculation
    gross_taxable = base_pay + nd_pay + odd_shift_pay + ot_pay + total_holiday_pay + bonuses
    
    # 3. Statutory Deductions
    # SSS: 5% of Monthly Salary Credit (Max MSC is Php 35,000 for 2026)
    msc = min(base_pay, 35000.00)
    sss_contribution = msc * 0.05
    philhealth = base_pay * 0.025  # Employee share is 2.5%
    pag_ibig = 200.00  # Statutory maximum cap
    
    total_contributions = sss_contribution + philhealth + pag_ibig
    
    # 4. Tax Computation (TRAIN Law for 2023-2026)
    taxable_income = gross_taxable - total_contributions
    tax = 0.00
    if taxable_income > 20833.33:
        tax = (taxable_income - 20833.33) * 0.15
        
    # 5. Final Net Pay
    # De Minimis is added AFTER tax because it is a non-taxable benefit
    net_monthly = gross_taxable - total_contributions - tax + de_minimis
    semi_monthly = net_monthly / 2
    
    return {
        "base_pay": base_pay,
        "nd_pay": nd_pay,
        "odd_shift_pay": odd_shift_pay,
        "ot_pay": ot_pay,
        "regular_holiday_pay": regular_holiday_pay,
        "special_holiday_pay": special_holiday_pay,
        "total_holiday_pay": total_holiday_pay,
        "bonuses": bonuses,
        "de_minimis": de_minimis,
        "gross_taxable": gross_taxable,
        "sss": sss_contribution,
        "philhealth": philhealth,
        "pag_ibig": pag_ibig,
        "total_contributions": total_contributions,
        "taxable_income": taxable_income,
        "tax": tax,
        "net_monthly": net_monthly,
        "semi_monthly": semi_monthly
    }

# --- STREAMLIT UI LAYOUT ---

st.set_page_config(page_title="REPH Transparent Salary Calculator", layout="wide")

st.title("Monthly Salary Calculator")
st.markdown("Based on REPH Total Rewards & Statutory Rates")

# Input Columns
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Core & Allowances")
    base_pay = st.number_input("Monthly Base Pay (Php)", value=23000.00, step=500.00)
    de_minimis = st.number_input("De Minimis Benefit (Php)", value=1000.00, step=250.00)
    bonuses = st.number_input("Bonuses / Incentives (Php)", value=0.00, step=500.00)

with col2:
    st.subheader("Shift Adjustments")
    nd_days = st.number_input("Night Differential Days (9PM-6AM)", min_value=0, value=0, help="Assumes 8 hours of ND per shift.")
    odd_shift_days = st.number_input("Odd Shift Days (11PM-5AM)", min_value=0, value=0)
    ot_hours = st.number_input("Regular Overtime Hours", min_value=0.0, value=0.0, step=1.0)

with col3:
    st.subheader("Holiday Premiums")
    regular_holiday_days = st.number_input("Regular Holidays Worked (Days)", min_value=0, value=0, step=1)
    special_holiday_days = st.number_input("Special Non-Working Days Worked (Days)", min_value=0, value=0, step=1)

# Run Calculation
if st.button("Calculate Salary", type="primary"):
    d = calculate_salary(base_pay, de_minimis, bonuses, nd_days, odd_shift_days, ot_hours, regular_holiday_days, special_holiday_days)
    
    st.divider()
    
    # High-level Output
    st.subheader("Payout Summary")
    res_col1, res_col2 = st.columns(2)
    res_col1.metric("Final Net Pay (Monthly)", f"Php {d['net_monthly']:,.2f}")
    res_col2.metric("Semi-Monthly Payout", f"Php {d['semi_monthly']:,.2f}")
    
    # Transparent Breakdown
    st.markdown("### 🧮 Transparent Computation Breakdown")
    
    breakdown_col1, breakdown_col2, breakdown_col3 = st.columns(3)
    
    with breakdown_col1:
        st.markdown("**1. Earnings & Premiums**")
        st.write(f"Base Pay: `Php {d['base_pay']:,.2f}`")
        st.write(f"Night Diff ({nd_days} days): `+ Php {d['nd_pay']:,.2f}`")
        st.write(f"Odd Shift ({odd_shift_days} days): `+ Php {d['odd_shift_pay']:,.2f}`")
        st.write(f"Overtime ({ot_hours} hrs): `+ Php {d['ot_pay']:,.2f}`")
        st.write(f"Regular Holiday Pay ({regular_holiday_days} days): `+ Php {d['regular_holiday_pay']:,.2f}`")
        st.write(f"Special Holiday Pay ({special_holiday_days} days): `+ Php {d['special_holiday_pay']:,.2f}`")
        st.write(f"Bonuses/Incentives: `+ Php {d['bonuses']:,.2f}`")
        st.info(f"**Gross Taxable = Php {d['gross_taxable']:,.2f}**")
        
    with breakdown_col2:
        st.markdown("**2. Deductions (Gov & Tax)**")
        st.write(f"SSS Contribution: `- Php {d['sss']:,.2f}`")
        st.write(f"PhilHealth (2.5%): `- Php {d['philhealth']:,.2f}`")
        st.write(f"Pag-IBIG (Max Cap): `- Php {d['pag_ibig']:,.2f}`")
        st.write(f"Withholding Tax: `- Php {d['tax']:,.2f}`")
        st.error(f"**Total Deductions = Php {(d['total_contributions'] + d['tax']):,.2f}**")

    with breakdown_col3:
        st.markdown("**3. Final Computation**")
        st.write(f"Gross Taxable: `Php {d['gross_taxable']:,.2f}`")
        st.write(f"Less Deductions: `- Php {(d['total_contributions'] + d['tax']):,.2f}`")
        st.write(f"Add De Minimis: `+ Php {d['de_minimis']:,.2f}`")
        st.success(f"**Net Monthly = Php {d['net_monthly']:,.2f}**")