"""
PNG Compliance Hub 2026 — Core Tax Engine
=========================================
TaxCalculator class implementing 2026 IRC legal specifications for:
  - SWT (Salary & Wages Tax) — Resident progressive brackets
  - GST (Goods & Services Tax) — 10% with Input Tax Credits
  - SBT (Small Business Tax) — Turnover-based

All monetary values are in Papua New Guinea Kina (PGK).
"""

from decimal import Decimal, ROUND_HALF_UP


class TaxCalculator:
    """
    Central 2026 IRC Tax Calculator for PNG MSMEs.
    All amounts in PGK (Papua New Guinea Kina).
    """

    # ── 2026 SWT Resident Progressive Brackets ──────────────────────────────
    # Format: (upper_limit_inclusive, marginal_rate)
    # None in upper_limit = no ceiling (top bracket)
    SWT_RESIDENT_BRACKETS = [
        (Decimal('20000'),  Decimal('0.22')),
        (Decimal('33000'),  Decimal('0.30')),
        (Decimal('70000'),  Decimal('0.35')),
        (Decimal('250000'), Decimal('0.40')),
        (None,              Decimal('0.42')),
    ]

    GST_RATE = Decimal('0.10')          # 10% standard rate

    SBT_THRESHOLD      = Decimal('250000')  # Max turnover to qualify for SBT
    SBT_FLAT_THRESHOLD = Decimal('50000')   # Below this → flat fee
    SBT_FLAT_FEE       = Decimal('400')     # K400 annual flat fee
    SBT_RATE           = Decimal('0.02')    # 2% for K50k–K250k band

    # ── SWT Calculation ──────────────────────────────────────────────────────

    @classmethod
    def calculate_swt(cls, annual_salary: Decimal, is_resident: bool = True) -> dict:
        """
        Calculate Salary & Wages Tax using 2026 progressive brackets.

        Args:
            annual_salary: Gross annual salary in PGK.
            is_resident:   True for resident, False for non-resident (flat 22%).

        Returns:
            dict with annual_tax, monthly_tax, effective_rate, breakdown.
        """
        annual_salary = Decimal(str(annual_salary))

        if not is_resident:
            # Non-residents: flat 22% on entire income, no threshold
            annual_tax = (annual_salary * Decimal('0.22')).quantize(Decimal('0.01'), ROUND_HALF_UP)
            return {
                'annual_tax': annual_tax,
                'monthly_tax': (annual_tax / 12).quantize(Decimal('0.01'), ROUND_HALF_UP),
                'fortnightly_tax': (annual_tax / 26).quantize(Decimal('0.01'), ROUND_HALF_UP),
                'effective_rate': Decimal('22.00'),
                'breakdown': [{'bracket': 'All income', 'rate': '22%', 'tax': annual_tax}],
                'is_resident': False,
            }

        # Resident: progressive brackets
        total_tax = Decimal('0')
        breakdown = []
        previous_limit = Decimal('0')
        remaining = annual_salary

        for upper_limit, rate in cls.SWT_RESIDENT_BRACKETS:
            if remaining <= 0:
                break

            if upper_limit is None:
                # Top bracket — no ceiling
                taxable_in_band = remaining
            else:
                band_width = upper_limit - previous_limit
                taxable_in_band = min(remaining, band_width)

            tax_in_band = (taxable_in_band * rate).quantize(Decimal('0.01'), ROUND_HALF_UP)
            total_tax += tax_in_band

            if taxable_in_band > 0:
                breakdown.append({
                    'bracket': f'K{previous_limit:,.0f} – K{upper_limit:,.0f}' if upper_limit else f'K{previous_limit:,.0f}+',
                    'taxable_amount': taxable_in_band,
                    'rate': f'{rate * 100:.0f}%',
                    'tax': tax_in_band,
                })

            remaining -= taxable_in_band
            if upper_limit:
                previous_limit = upper_limit

        effective_rate = (
            (total_tax / annual_salary * 100).quantize(Decimal('0.01'), ROUND_HALF_UP)
            if annual_salary > 0 else Decimal('0')
        )

        return {
            'annual_tax': total_tax,
            'monthly_tax': (total_tax / 12).quantize(Decimal('0.01'), ROUND_HALF_UP),
            'fortnightly_tax': (total_tax / 26).quantize(Decimal('0.01'), ROUND_HALF_UP),
            'net_annual': annual_salary - total_tax,
            'net_monthly': ((annual_salary - total_tax) / 12).quantize(Decimal('0.01'), ROUND_HALF_UP),
            'effective_rate': effective_rate,
            'breakdown': breakdown,
            'is_resident': True,
        }

    # ── GST Calculation ──────────────────────────────────────────────────────

    @classmethod
    def calculate_gst(cls, sales_amount: Decimal, purchases_amount: Decimal = Decimal('0')) -> dict:
        """
        Calculate GST with Input Tax Credit (ITC) mechanism.

        Args:
            sales_amount:     Total sales (GST-exclusive or inclusive handled by caller).
            purchases_amount: Total GST-taxable purchases (for ITC claim).

        Returns:
            dict with output_gst, input_gst, net_gst, gst_refund_due.
        """
        sales_amount     = Decimal(str(sales_amount))
        purchases_amount = Decimal(str(purchases_amount))

        output_gst = (sales_amount * cls.GST_RATE).quantize(Decimal('0.01'), ROUND_HALF_UP)
        input_gst  = (purchases_amount * cls.GST_RATE).quantize(Decimal('0.01'), ROUND_HALF_UP)
        net_gst    = output_gst - input_gst
        refund_due = net_gst < 0

        return {
            'sales_amount':     sales_amount,
            'purchases_amount': purchases_amount,
            'output_gst':       output_gst,
            'input_gst':        input_gst,
            'net_gst':          abs(net_gst),
            'gst_payable':      net_gst if net_gst > 0 else Decimal('0'),
            'gst_refund_due':   abs(net_gst) if refund_due else Decimal('0'),
            'refund_due':       refund_due,
            'rate_pct':         '10%',
        }

    # ── SBT Calculation ──────────────────────────────────────────────────────

    @classmethod
    def calculate_sbt(cls, annual_turnover: Decimal) -> dict:
        """
        Calculate Small Business Tax for eligible businesses (turnover < K250,000).

        Args:
            annual_turnover: Annual gross turnover in PGK.

        Returns:
            dict with sbt_liability, sbt_type, is_eligible.
        """
        annual_turnover = Decimal(str(annual_turnover))

        if annual_turnover >= cls.SBT_THRESHOLD:
            return {
                'is_eligible': False,
                'annual_turnover': annual_turnover,
                'sbt_liability': Decimal('0'),
                'sbt_type': 'Not eligible — standard GST/Income Tax applies',
                'note': 'Turnover exceeds K250,000. Business must register for GST and pay income tax.',
            }

        if annual_turnover < cls.SBT_FLAT_THRESHOLD:
            return {
                'is_eligible': True,
                'annual_turnover': annual_turnover,
                'sbt_liability': cls.SBT_FLAT_FEE,
                'sbt_type': 'Flat Fee',
                'rate_display': f'K{cls.SBT_FLAT_FEE} annual flat fee',
                'note': 'Turnover below K50,000. K400 flat annual SBT applies.',
            }

        # K50k – K250k: 2% of turnover
        liability = (annual_turnover * cls.SBT_RATE).quantize(Decimal('0.01'), ROUND_HALF_UP)
        return {
            'is_eligible': True,
            'annual_turnover': annual_turnover,
            'sbt_liability': liability,
            'sbt_type': 'Percentage of Turnover',
            'rate_display': '2% of annual turnover',
            'note': 'Turnover between K50,000 and K250,000. SBT = 2% of gross turnover.',
        }

    # ── Summary ──────────────────────────────────────────────────────────────

    @classmethod
    def full_compliance_summary(
        cls,
        annual_turnover: Decimal,
        annual_sales: Decimal,
        annual_purchases: Decimal,
        payroll_entries: list | None = None,
    ) -> dict:
        """
        Generate a complete compliance summary for a business.

        Args:
            annual_turnover:   Total business turnover.
            annual_sales:      GST-taxable sales.
            annual_purchases:  GST-taxable purchases.
            payroll_entries:   List of dicts: [{'name': str, 'salary': Decimal, 'is_resident': bool}]

        Returns:
            Combined compliance summary dict.
        """
        gst = cls.calculate_gst(annual_sales, annual_purchases)
        sbt = cls.calculate_sbt(annual_turnover)

        swt_summary = []
        total_swt = Decimal('0')
        if payroll_entries:
            for emp in payroll_entries:
                result = cls.calculate_swt(emp['salary'], emp.get('is_resident', True))
                swt_summary.append({
                    'employee': emp.get('name', 'Unknown'),
                    **result,
                })
                total_swt += result['annual_tax']

        return {
            'gst': gst,
            'sbt': sbt,
            'swt': {
                'employees': swt_summary,
                'total_annual_swt': total_swt,
                'total_monthly_swt': (total_swt / 12).quantize(Decimal('0.01'), ROUND_HALF_UP),
            },
            'total_tax_liability': gst['gst_payable'] + sbt['sbt_liability'] + total_swt,
        }
