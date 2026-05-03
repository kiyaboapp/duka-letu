# Kiyabo Duka — Accounting & Financial Reports Reference
## Upendo Stationery | Dar es Salaam, Tanzania | Currency: TZS
### Prepared by: Accountant / Financial Controller
### Version: 1.0 — May 2026

---

> **Purpose of this document:** A professional accountant's complete guide to every financial report this business can and should produce — what each report is, why it exists, what period it covers, who reads it, and what decisions it drives. Reports are grouped by time horizon: intraday → daily → weekly → monthly → quarterly → annual. Each report section includes its formal accounting definition, its structure, and its practical use for Upendo Stationery.

---

## SECTION A — INTRADAY REPORTS (During the trading day)

---

### A1. Live Sales Ticker / Point-of-Sale Summary

**What it is:** A running real-time accumulation of all transactions processed since the shop opened that day. Not a formal accounting statement — it is an operational control tool.

**Period:** From opening time to the moment of printing/viewing.

**Why it exists:** The shop manager and cashier need to see at a glance how much cash and M-Pesa has been collected so far, how many items have moved, and whether anything unusual has happened (large return, unexpected credit sale) before the day is closed.

**Structure:**

```
LIVE SALES SUMMARY — Upendo Stationery
As at: [TIME] on [DATE]
─────────────────────────────────────────
Transaction Type          Count      TZS
─────────────────────────────────────────
Direct Cash Sales            14    87,400
M-Pesa Sales                  6    31,200
Credit Sales (Debtors)        2    18,000
Return Inwards                1   (4,500)
─────────────────────────────────────────
GROSS SALES TO DATE                132,100
Less: Returns                       (4,500)
NET SALES TO DATE                  127,600
─────────────────────────────────────────
Cash in Till (expected)             87,400
M-Pesa Received                     31,200
TOTAL CASH ACCOUNTED FOR           118,600
─────────────────────────────────────────
```

**Who reads it:** Cashier (for reconciliation), Shop Manager (for oversight).

**Accounting basis:** Cash and accrual. Credit sales are shown even though cash has not been received, because they reduce stock.

---

### A2. Intraday Stock Alert Report

**What it is:** A list of product specs that have fallen below their reorder level during the current trading day.

**Period:** Live — recalculated after each sale transaction.

**Why it exists:** A stationery shop loses sales rapidly when popular items run out. This report flags items before they reach zero, giving the owner time to reorder from suppliers within the same day.

**Structure:**

```
STOCK ALERT — Upendo Stationery
Generated: [TIME] on [DATE]
──────────────────────────────────────────────────────────
Product                  Spec      Current Qty   Reorder Qty   Status
──────────────────────────────────────────────────────────
Notebook Hardcover       A4             3             10        ⚠ LOW
Ballpoint Pen Blue       Box/12         0              5        ✘ OUT
Stapler Standard         —              2              4        ⚠ LOW
──────────────────────────────────────────────────────────
Items at zero stock: 1    Items below reorder level: 3
──────────────────────────────────────────────────────────
```

**Who reads it:** Shop Owner, Purchasing Officer.

**Accounting basis:** Inventory control. The figures derive from the running stock formula:
`Current Stock = Purchases + Return Inwards − Direct Sales − Credit Sales − Return Outwards − Office Use − Drawings`

---

## SECTION B — DAILY REPORTS (End of each trading day)

---

### B1. Daily Cash Reconciliation Report

**What it is:** A formal reconciliation between the cash that *should* be in the till (per the system) and the cash that *physically is* in the till (per counting). This is the most important daily control document in any retail business.

**Period:** Single trading day (midnight to midnight, or opening to closing).

**Why it exists:** Protects against theft, cashier error, and unrecorded transactions. Every cent of discrepancy must be explained before the day is closed in the books. Auditors rely on these records to assess internal control quality.

**Structure:**

```
DAILY CASH RECONCILIATION
Upendo Stationery — [DATE]
Prepared by: [Cashier Name]   Verified by: [Manager Name]
══════════════════════════════════════════════════════════

SYSTEM CASH POSITION
Opening Float                                    50,000
Add: Cash Sales                                 87,400
Add: Debt Repayments received (cash)            15,000
Less: Cash Expenses paid from till             (12,000)
Less: Drawings taken                                  0
──────────────────────────────────────────────────────
EXPECTED CASH IN TILL                          140,400

PHYSICAL CASH COUNT
1,000/= × 42 notes                              42,000
500/= × 61 notes                                30,500
200/= × 84 coins                                16,800
100/= × 51 coins                                 5,100
Other coins                                      2,000
──────────────────────────────────────────────────────
PHYSICAL CASH COUNTED                           96,400
M-Pesa Balance (float is separate)              44,000
TOTAL ACCOUNTED FOR                            140,400

VARIANCE                                              0
──────────────────────────────────────────────────────
Status: ✓ RECONCILED
══════════════════════════════════════════════════════════
Notes: [Any explanation of variance if present]
```

**Who reads it:** Shop Owner (daily), External Auditor (on audit).

**Accounting basis:** Double-entry check. Cash account Dr must equal sum of all cash receipts minus all cash payments for the day.

---

### B2. Daily Sales Report (Daily Revenue Summary)

**What it is:** A summary of all revenue-generating activity for one calendar day, broken down by transaction type and by payment method.

**Period:** One trading day.

**Why it exists:** Tells the owner exactly how much the business earned, how much is owed (credit), and what sold most — all in one page. Used for day-to-day performance monitoring and for posting to the monthly ledger.

**Structure:**

```
DAILY SALES REPORT
Upendo Stationery — [DATE]
══════════════════════════════════════════════════════════

BY TRANSACTION TYPE
Direct Sales (Cash)                             87,400
Direct Sales (M-Pesa)                           31,200
Credit Sales (on account)                       18,000
──────────────────────────────────────────────────────
GROSS SALES                                    136,600
Less: Return Inwards                            (4,500)
──────────────────────────────────────────────────────
NET SALES                                      132,100

BY PRODUCT CATEGORY
Notebooks & Pads                                44,200
Pens & Pencils                                  28,600
Office Supplies                                 21,800
Paper & Printing                                37,500
──────────────────────────────────────────────────────
TOTAL                                          132,100

TOP 5 ITEMS BY REVENUE TODAY
1. Notebook Hardcover A4      38 units    25,080
2. Ballpoint Pen Blue Box      9 units    18,000
3. A4 Copy Paper Ream          5 units    17,500
4. File Folder Plastic        22 units    11,000
5. Staples Box                14 units     7,000

CREDIT SALES DETAIL
Debtor Name           Amount Due    Due Date    Reference
Amina Rashidi          12,000       15/06/26    DT-2026-0041
Juma Mwangi             6,000       20/06/26    DT-2026-0042
──────────────────────────────────────────────────────
Total New Credit Today  18,000
══════════════════════════════════════════════════════════
```

**Who reads it:** Owner, Accountant, Sales Manager.

**Accounting basis:** Accrual basis. Revenue is recognised at point of sale regardless of payment timing.

---

### B3. Daily Stock Movement Report

**What it is:** A record of every change in inventory that occurred during the day — inflows, outflows, and the cause of each movement.

**Period:** One trading day.

**Why it exists:** Provides the audit trail for inventory. Without this, it is impossible to explain why a product's stock changed by a certain amount. Required for year-end stocktake reconciliation and for identifying shrinkage.

**Structure:**

```
DAILY STOCK MOVEMENT REPORT
Upendo Stationery — [DATE]
══════════════════════════════════════════════════════════

Product: Notebook Hardcover A4
──────────────────────────────────────────────────────
Opening Balance             120 units
Add: Purchases                 0 units
Add: Return Inwards            2 units   (Ref: RI-2026-0018)
Less: Direct Sales           (38 units)
Less: Credit Sales            (0 units)
Less: Return Outwards          (0 units)
Less: Office Use               (1 unit)
Less: Drawings                 (0 units)
──────────────────────────────────────────────────────
CLOSING BALANCE              83 units
Weighted Avg Cost: 660/=    Stock Value: TZS 54,780
══════════════════════════════════════════════════════════

[Repeated for each product that moved today]

DAILY SUMMARY ACROSS ALL PRODUCTS
Total Opening Stock Value        3,026,350
Total Purchases (cost)                   0
Total COGS (weighted avg)           14,950
Total Closing Stock Value        3,011,400

Integrity Check: 3,026,350 + 0 = 14,950 + 3,011,400 ✓
══════════════════════════════════════════════════════════
```

**Who reads it:** Accountant, Stock Controller, External Auditor.

**Accounting basis:** Weighted Average Cost method (GAAP compliant). Inventory is a Balance Sheet asset; every outflow is either COGS (Income Statement) or an Owner's Equity reduction (Drawings).

---

### B4. Daily Expense Voucher Summary

**What it is:** A list of every expense paid during the day, with authorisation references. Not a full ledger — it is the daily posting summary before entries are made.

**Period:** One trading day.

**Why it exists:** Creates an authorised, dated record of cash out. Every expense must be approved before payment; this report shows what was approved and paid. Without it, expense claims cannot be verified.

**Structure:**

```
DAILY EXPENSE VOUCHER SUMMARY
Upendo Stationery — [DATE]
══════════════════════════════════════════════════════════

Voucher No.   Expense Type      Item Description        Amount
EV-2026-091   Usafi (Cleaning)  Daily shop cleaning      5,000
EV-2026-092   Matengenezo       Shelving repair          7,000
──────────────────────────────────────────────────────
TOTAL EXPENSES PAID TODAY                               12,000

Approved by: [Owner Signature]    Posted by: [Accountant]
══════════════════════════════════════════════════════════
```

**Who reads it:** Owner, Accountant.

---

## SECTION C — WEEKLY REPORTS

---

### C1. Weekly Sales Performance Report

**What it is:** A comparative summary of sales across the seven days of the week, with a week-over-week comparison.

**Period:** Monday to Sunday (or Saturday, depending on trading days).

**Why it exists:** Single-day data is noisy — a slow Tuesday is meaningless in isolation. Weekly data reveals genuine performance trends: which days are strongest, whether the week improved or declined versus last week, and whether targets are being met.

**Structure:**

```
WEEKLY SALES PERFORMANCE REPORT
Upendo Stationery
Week: [DD/MM/YYYY] to [DD/MM/YYYY]
══════════════════════════════════════════════════════════

         Net Sales    COGS      Gross Profit   GP Margin
Mon        98,200    61,400       36,800         37.5%
Tue        87,400    54,000       33,400         38.2%
Wed       112,300    71,000       41,300         36.8%
Thu        95,600    59,800       35,800         37.4%
Fri       143,200    89,500       53,700         37.5%
Sat       167,900   104,400       63,500         37.8%
Sun        32,000    19,800       12,200         38.1%
──────────────────────────────────────────────────────
WEEK TOT   736,600   460,000      276,700         37.6%
PREV WEEK  698,200   436,000      262,200         37.6%
VARIANCE   +38,400   +24,000      +14,500        +0.0pp

Credit Sales This Week:                         54,000
Cash Collections from Debtors:                  31,200
Net Receivables Movement:                      +22,800
══════════════════════════════════════════════════════════
```

**Who reads it:** Owner (for business pulse), Accountant (for ledger review).

---

### C2. Weekly Debtor Aging — Short Form

**What it is:** A list of all outstanding credit balances owed to the shop, grouped by how long they have been outstanding.

**Period:** Point-in-time snapshot at end of week.

**Why it exists:** Credit extended to customers is an asset (Accounts Receivable). As time passes, the probability of collection drops. This report flags debts that are ageing badly so the owner can follow up before they become uncollectible. It is also needed to assess whether a provision for bad debts is required.

**Structure:**

```
WEEKLY DEBTOR AGING REPORT
Upendo Stationery — As at [DATE]
══════════════════════════════════════════════════════════

Debtor            Total Owed    Current    1–30d    31–60d    61–90d    90d+
                                (0–0d)
Amina Rashidi       45,000      12,000    18,000    15,000         0       0
Juma Mwangi         28,500           0     6,000    22,500         0       0
Hassan Omari        62,000           0         0    14,000    48,000       0
Fatuma Kilio        19,000           0         0         0         0  19,000
──────────────────────────────────────────────────────────────────────────
TOTALS             154,500      12,000    24,000    51,500    48,000  19,000
% of total            100%        7.8%     15.5%     33.3%     31.1%   12.3%

Bad Debt Provision (10% of 90d+):                              1,900
══════════════════════════════════════════════════════════════════════════
Action Required:
  - Fatuma Kilio: 90+ days — ESCALATE to owner for personal contact
  - Hassan Omari: 61–90 days — Send formal written demand
══════════════════════════════════════════════════════════════════════════
```

**Who reads it:** Owner, Accountant. The 90d+ column is reviewed before extending any new credit to a debtor.

---

### C3. Weekly Purchase & Supplier Summary

**What it is:** A summary of all goods purchased from suppliers during the week, by supplier and by product category.

**Period:** One week (Monday to Sunday).

**Why it exists:** Purchasing decisions affect cash flow, stock levels, and COGS simultaneously. This report tells the owner whether purchasing matched sales velocity, whether carriage costs are proportional, and whether any supplier has become unusually dominant in the supply mix.

**Structure:**

```
WEEKLY PURCHASE SUMMARY
Upendo Stationery
Week: [DD/MM/YYYY] to [DD/MM/YYYY]
══════════════════════════════════════════════════════════

Supplier              Invoice Ref    Category       Qty    Unit Cost    Total Cost
Dar Stationery Ltd    INV-1042       Notebooks      200       660        132,000
Kariakoo Office       INV-0891       Pens           500        80         40,000
Dar Stationery Ltd    INV-1043       Paper           50     3,500        175,000
──────────────────────────────────────────────────────────────────────────
TOTAL PURCHASES                                                          347,000
Less: Return Outwards                                                    (18,000)
Add: Carriage Inwards                                                     12,000
──────────────────────────────────────────────────────────────────────────
NET COST OF PURCHASES                                                    341,000

Opening Stock Value (Mon)                                              2,980,400
Add: Net Purchases                                                       341,000
Cost of Goods Available for Sale                                       3,321,400
══════════════════════════════════════════════════════════════════════════
```

---

## SECTION D — MONTHLY REPORTS (Core Management Accounts)

---

### D1. Monthly Income Statement (Profit & Loss Account)

**What it is:** The most important financial statement for any business. It shows all revenue earned and all costs incurred during a month, arriving at the net profit or loss. This is the standard P&L — the core management report every business runs monthly.

**Period:** One calendar month (1st to last day).

**Why it exists:** Tells the owner whether the business is profitable. Banks, investors, and tax authorities all require this. Internally, it is the primary measure of commercial performance. Without a monthly P&L, the owner is flying blind.

**Structure:**

```
INCOME STATEMENT
Upendo Stationery (Kiyabo Duka)
For the Month Ended: [31 MONTH YYYY]
Prepared by: [Accountant Name], [Date]
══════════════════════════════════════════════════════════

                                          TZS            TZS
REVENUE
  Direct Sales (Cash + M-Pesa)                     3,840,200
  Credit Sales                                       642,000
  Less: Return Inwards                               (87,400)
                                              ──────────────
  NET SALES                                        4,394,800

COST OF GOODS SOLD
  Opening Stock (1st of month)             3,026,350
  Add: Purchases                           1,240,000
  Add: Carriage Inwards                       48,000
  Less: Return Outwards                      (62,000)
                                          ──────────────
  Net Purchases                            1,226,000
  Cost of Goods Available for Sale (COGAS) 4,252,350
  Less: Closing Stock (last day of month) (3,018,200)
                                              ──────────────
  COST OF GOODS SOLD (COGS)                        1,234,150

                                              ──────────────
GROSS PROFIT                                       3,160,650
Gross Profit Margin                                    71.9%

OPERATING EXPENSES
  Kodi (Rent)                                        480,000
  Mshahara (Salaries)                                600,000
  Umeme (Electricity)                                 87,000
  Maji (Water)                                        12,000
  Matangazo (Advertising)                             45,000
  Matengenezo (Maintenance)                           38,000
  Usafi (Cleaning)                                    62,000
  Office Use / Sundries                               14,800
  Interest on Liabilities                             22,000
                                              ──────────────
  TOTAL OPERATING EXPENSES                         1,360,800

                                              ══════════════
NET PROFIT BEFORE TAX                              1,799,850
Estimated Tax Provision (30%)                       (539,955)
                                              ══════════════
NET PROFIT AFTER TAX                               1,259,895
                                              ══════════════

Accounting Integrity Check:
Opening Stock (3,026,350) + Net Purchases (1,226,000)
= COGS (1,234,150) + Closing Stock (3,018,200)
= 4,252,350  ✓
══════════════════════════════════════════════════════════
```

**Who reads it:** Owner (strategic), Accountant (preparation), Bank (loan reviews), Tanzania Revenue Authority (tax filing).

**Accounting basis:** Accrual basis. Weighted Average Cost for inventory.

---

### D2. Monthly Balance Sheet (Statement of Financial Position)

**What it is:** A snapshot of everything the business owns (assets), everything it owes (liabilities), and the owner's net stake (equity) — at a single point in time: the last day of the month.

**Period:** Point in time — last day of the month.

**Why it exists:** The P&L shows flow (what happened this month). The Balance Sheet shows stock (what the business is worth right now). Together they tell the complete financial story. Lenders require it to assess creditworthiness. Owners need it to understand the true value of their business.

**Structure:**

```
BALANCE SHEET (STATEMENT OF FINANCIAL POSITION)
Upendo Stationery (Kiyabo Duka)
As at: [31 MONTH YYYY]
Prepared by: [Accountant Name], [Date]
══════════════════════════════════════════════════════════

NON-CURRENT ASSETS                             TZS            TZS
  Fixtures & Fittings (at cost)            450,000
  Less: Accumulated Depreciation           (90,000)
  Net Book Value — Fixtures                               360,000

  Shop Equipment (at cost)                 180,000
  Less: Accumulated Depreciation           (36,000)
  Net Book Value — Equipment                              144,000
                                                     ──────────────
TOTAL NON-CURRENT ASSETS                               504,000

CURRENT ASSETS
  Inventory (Closing Stock — weighted avg cost)       3,018,200
  Accounts Receivable (Debtors)           154,500
  Less: Provision for Bad Debts            (7,725)
  Net Receivables                                       146,775
  Cash and Cash Equivalents                             218,400
  M-Pesa Balance                                         87,200
                                                     ──────────────
TOTAL CURRENT ASSETS                                 3,470,575

                                                     ══════════════
TOTAL ASSETS                                         3,974,575
                                                     ══════════════

NON-CURRENT LIABILITIES
  Bank Loan — Principal Outstanding                     500,000
  Long-term Trade Payable                               120,000
                                                     ──────────────
TOTAL NON-CURRENT LIABILITIES                          620,000

CURRENT LIABILITIES
  Accounts Payable (Creditors)                          187,000
  Expense Obligations Due Within 30 Days                 94,000
  Accrued Interest Payable                               22,000
                                                     ──────────────
TOTAL CURRENT LIABILITIES                              303,000

TOTAL LIABILITIES                                      923,000

                                                     ══════════════
NET ASSETS                                           3,051,575
                                                     ══════════════

OWNER'S EQUITY
  Opening Capital (1st of month)                     2,791,680
  Add: Net Profit for Month                          1,259,895
  Less: Drawings (month)                              (480,000)
  Less: Tax Provision                                 (519,000)
                                                     ──────────────
CLOSING EQUITY                                       3,051,575

Accounting Equation Check:
Total Assets (3,974,575) = Total Liabilities (923,000) + Equity (3,051,575) ✓
══════════════════════════════════════════════════════════
```

---

### D3. Monthly Cash Flow Statement

**What it is:** A reconciliation of cash inflows and cash outflows during the month, split into three activities: Operating (day-to-day trading), Investing (buying/selling assets), and Financing (loans, drawings).

**Period:** One calendar month.

**Why it exists:** A business can show a profit on the P&L yet still run out of cash — for example, if sales are on credit and debtors do not pay. The Cash Flow Statement shows the *actual cash reality* behind the accounting numbers. Banks and investors consider this more reliable than profit figures.

**Structure:**

```
CASH FLOW STATEMENT
Upendo Stationery (Kiyabo Duka)
For the Month Ended: [31 MONTH YYYY]
══════════════════════════════════════════════════════════

OPERATING ACTIVITIES                           TZS
  Net Profit Before Tax                      1,799,850
  Adjustments:
    Add: Depreciation                           15,000
    Less: Increase in Inventory              (240,000)   [stock went up]
    Less: Increase in Receivables             (62,000)   [more credit given]
    Add: Increase in Payables                  42,000    [owe more to suppliers]
  ──────────────────────────────────────────────────────
  Cash Generated from Operations             1,554,850
  Less: Tax Paid                              (519,000)
  ──────────────────────────────────────────────────────
  NET CASH FROM OPERATING ACTIVITIES         1,035,850

INVESTING ACTIVITIES
  Purchase of Equipment                        (0)
  Proceeds from Asset Disposal                 (0)
  ──────────────────────────────────────────────────────
  NET CASH FROM INVESTING ACTIVITIES                  0

FINANCING ACTIVITIES
  Drawings by Owner                          (480,000)
  Loan Repayment — Principal                  (50,000)
  Loan Repayment — Interest                   (22,000)
  ──────────────────────────────────────────────────────
  NET CASH FROM FINANCING ACTIVITIES         (552,000)

  ══════════════════════════════════════════════════════
  NET INCREASE IN CASH                        483,850
  Opening Cash Balance (1st of month)         (177,650)
  ══════════════════════════════════════════════════════
  CLOSING CASH BALANCE                        305,600   ✓ [matches B/S cash + M-Pesa]
══════════════════════════════════════════════════════════
```

---

### D4. Monthly Expense Analysis Report

**What it is:** A detailed breakdown of all operating expenses by type and item, compared against budget (if set) and the prior month.

**Period:** One calendar month.

**Why it exists:** The P&L shows total expenses in one line. This report shows the detail behind that line — which expense type is growing, which supplier is charging more, and whether the expense pattern is seasonal or structural.

**Structure:**

```
MONTHLY EXPENSE ANALYSIS
Upendo Stationery — [MONTH YYYY]
══════════════════════════════════════════════════════════

Expense Type          Item Description      Budget    Actual    Variance
─────────────────────────────────────────────────────────────────────────
Rent (Kodi)           Shop Rent Kariakoo   480,000   480,000        0
Salaries (Mshahara)   Cashier × 1          300,000   300,000        0
                      Cleaner × 1          180,000   180,000        0  [auto-generated obligation]
Electricity (Umeme)   TANESCO Bill          90,000    87,000     +3,000
Water (Maji)          DAWASCO              12,000    12,000        0
Advertising           Social Media Posts    50,000    45,000     +5,000
Maintenance           Shelf Repair          20,000    38,000    (18,000) ⚠
Cleaning              Daily Service         60,000    62,000     (2,000)
Office Use            Items consumed —      15,000    14,800       +200
─────────────────────────────────────────────────────────────────────────
TOTAL OPERATING EXP                      1,207,000 1,218,800    (11,800)

⚠ Maintenance exceeded budget by TZS 18,000. Reason: Unplanned shelf repair.
  Prepayment applied: TZS 12,000 from prepayment batch PP-2026-004.
══════════════════════════════════════════════════════════════════════════
```

---

### D5. Monthly Debtor Aging Report (Full)

**What it is:** The comprehensive monthly version of the weekly aging report. Includes debtor contact details, original invoice dates, payment history, and collection notes.

**Period:** As at last day of month.

**Why it exists:** Month-end is when the formal accounts receivable balance is struck for the Balance Sheet. The aging analysis determines what provision for bad debts to create. Auditors require this as evidence for the receivables balance.

**Structure:**

```
DEBTOR AGING REPORT — FULL
Upendo Stationery — As at [31 MONTH YYYY]
══════════════════════════════════════════════════════════

Ref        Debtor         NIDA Ref    Invoice Date  Due Date    Original    Paid     Balance    Age
DT-2026-018 Amina Rashidi  T-0098-A   12/04/2026    12/05/2026   45,000    12,000    33,000    50d
DT-2026-024 Juma Mwangi    T-1124-B   20/04/2026    20/05/2026   28,500     6,000    22,500    41d
DT-2026-031 Hassan Omari   T-8834-C   01/03/2026    01/04/2026   62,000         0    62,000    91d ⚠
DT-2026-007 Fatuma Kilio   T-3341-D   15/01/2026    15/02/2026   19,000         0    19,000   136d ✘
─────────────────────────────────────────────────────────────────────────────────────────────────────
TOTALS                                               154,500    18,000   136,500

Aging Buckets:
  Current (0–30 days):     TZS  12,000   (8.8%)
  1–60 days:               TZS  55,500   (40.7%)
  61–90 days:              TZS  50,000   (36.6%)
  Over 90 days:            TZS  19,000   (13.9%)

Bad Debt Provision:
  10% × TZS 19,000 (90d+)  =  TZS  1,900
  5% × TZS 50,000 (61–90d) =  TZS  2,500
  Total Provision Required    =  TZS  4,400
══════════════════════════════════════════════════════════════════════════
```

---

### D6. Monthly Liability (Loan) Schedule

**What it is:** A detailed statement of all external borrowings — the opening balance, interest accrued, payments made (split into principal and interest), and the closing balance for the month.

**Period:** One calendar month.

**Why it exists:** The owner must know exactly how much is owed on each loan at any point. The split between principal and interest matters because only principal reduces the liability balance on the Balance Sheet, while interest is an expense on the P&L.

**Structure:**

```
MONTHLY LIABILITY SCHEDULE
Upendo Stationery — [MONTH YYYY]
══════════════════════════════════════════════════════════

Liability: CRDB Bank Business Loan
Category: Bank Loan  |  Type: Term Loan  |  Rate: 18% p.a.

Opening Balance (1st):                         550,000
Add: Interest Accrued (18% ÷ 12):               8,250
Less: Payment Made on [DATE]:                  (58,250)
  — Principal Component:                        50,000
  — Interest Component:                          8,250
Closing Balance (last day):                    500,000

Maturity Date: 31/12/2027
Remaining Term: 20 months
Monthly Instalment: TZS 58,250 (fixed)
══════════════════════════════════════════════════════════

[Repeated per liability item]

TOTAL LIABILITIES SUMMARY
Opening Total Liabilities:    670,000
Closing Total Liabilities:    620,000
Principal Repaid This Month:   50,000
Interest Expensed This Month:   8,250
══════════════════════════════════════════════════════════
```

---

### D7. Monthly Drawings Summary

**What it is:** A record of all goods or cash taken from the business by the owner for personal use during the month.

**Period:** One calendar month.

**Why it exists:** Drawings are not a business expense — they are a reduction of owner's equity. They must be tracked separately from expenses to prevent the P&L from being distorted. This report also helps the owner understand how much they are withdrawing relative to the profit generated.

**Structure:**

```
MONTHLY DRAWINGS SUMMARY
Upendo Stationery — [MONTH YYYY]
══════════════════════════════════════════════════════════

Date       Type         Description                  Qty    Value (TZS)
05/05/26   Cash         Personal withdrawal            —      200,000
12/05/26   Goods        Notebooks A5 for children      5        3,300
18/05/26   Cash         Personal withdrawal            —      150,000
24/05/26   Goods        Pens for home                 12          960
28/05/26   Cash         Personal withdrawal            —      125,740
──────────────────────────────────────────────────────────────────────
TOTAL CASH DRAWINGS                                          475,740
TOTAL GOODS DRAWINGS (at weighted avg cost)                    4,260
TOTAL DRAWINGS THIS MONTH                                    480,000

Net Profit for Month:       1,799,850
Total Drawings:              (480,000)
Drawings as % of Profit:        26.7%
══════════════════════════════════════════════════════════════════════
```

---

## SECTION E — QUARTERLY REPORTS

---

### E1. Quarterly Management Accounts Pack

**What it is:** A consolidated three-month summary combining the P&L, Balance Sheet, Cash Flow, and key ratio analysis into one management pack. Produced for the owner's strategic decision-making and for any bank or lender who asks for a business performance update.

**Period:** January–March, April–June, July–September, October–December.

**Why it exists:** Monthly data is detailed but granular. Quarterly data smooths out one-off events (a particularly good Friday, a supplier delay that shifted one week) and shows the genuine trajectory of the business over a meaningful trading period.

**Key contents:**
1. Comparative P&L — three months side by side with trend arrows
2. Quarter-end Balance Sheet
3. Cash Flow for the quarter
4. Key Performance Ratios (see below)
5. Stock Turn Analysis
6. Debtor Collection Period
7. Commentary from the Accountant

**Key Ratios Included:**

```
QUARTERLY KPI DASHBOARD
Upendo Stationery — Q2 [YYYY] (April–June)
══════════════════════════════════════════════════════════

PROFITABILITY
  Gross Profit Margin          =  Gross Profit / Net Sales       72.1%
  Net Profit Margin            =  Net Profit / Net Sales         40.8%
  Return on Capital Employed   =  EBIT / Total Assets            55.3%

LIQUIDITY
  Current Ratio                =  Current Assets / Current Liab   11.4×
  Quick Ratio (excl. stock)    =  (Cash + Receivables) / C.Liab    1.4×
  Cash Coverage Days           =  Cash / Daily Expenses            6.8d

EFFICIENCY
  Inventory Turnover           =  COGS / Avg Inventory             1.6×
  Days Inventory Outstanding   =  365 / Inventory Turnover       228.1d
  Debtor Collection Period     =  Avg Receivables / (Sales/365)   11.3d

LEVERAGE
  Debt-to-Equity Ratio         =  Total Liabilities / Equity      0.30×
  Interest Coverage Ratio      =  EBIT / Interest Expense         82.0×
══════════════════════════════════════════════════════════════════════
```

---

### E2. Quarterly Stock Valuation Report

**What it is:** A full product-by-product listing of all inventory on hand at the end of the quarter, valued at weighted average cost, with a reconciliation to the ledger balance.

**Period:** As at last day of quarter.

**Why it exists:** Inventory is typically the largest asset on the Balance Sheet for a retail business. Quarterly valuation confirms that the system stock matches physical reality. Significant variances require investigation — they indicate either system error, shrinkage (theft), or spoilage.

**Structure:**

```
STOCK VALUATION REPORT
Upendo Stationery — As at [31 MONTH YYYY] (Quarter End)
══════════════════════════════════════════════════════════

Product              Spec     Qty on Hand   Wtd Avg Cost   Stock Value
Notebook Hardcover   A4               83          660.00       54,780
Notebook Hardcover   A5              112          440.00       49,280
Ballpoint Pen Blue   Box/12          230           80.00       18,400
A4 Copy Paper        Ream            142        3,500.00      497,000
[... continued for all 123+ products ...]
──────────────────────────────────────────────────────────────────────
TOTAL INVENTORY AT WEIGHTED AVG COST (SYSTEM)           3,018,200
PHYSICAL STOCKTAKE VALUE (if done this quarter)         3,018,200
VARIANCE                                                        0  ✓

Costing Method: Weighted Average (WAC)
Basis: All purchase history used — WAC reflects the true blended cost of every unit.
══════════════════════════════════════════════════════════════════════
```

---

## SECTION F — ANNUAL REPORTS (Statutory & Tax)

---

### F1. Annual Income Statement (Audited Profit & Loss)

**What it is:** The full-year P&L covering all 12 months of the financial year. The definitive summary of how the business performed across the entire year.

**Period:** Full financial year (e.g., 1 January to 31 December).

**Why it exists:** A full year of trading needs a single, clean summary. Used by banks for annual loan reviews and forms the foundation for the following year's budget. Also the document to reach for if the business ever needs to present its performance to a bank or partner.

**Structure:** Identical to the monthly P&L but covering 12 months. Includes comparative columns for the prior financial year. Signed by the accountant with their professional registration number.

**Unique to Annual Version:**
- Prior year comparative column (so you can see growth at a glance)
- Owner's sign-off confirming the figures are accurate
- Accountant's preparation note

---

### F2. Annual Balance Sheet (Audited)

**What it is:** The year-end Statement of Financial Position. A snapshot of everything the business owns, owes, and the owner's net stake — as at the last day of the financial year.

**Period:** As at the last day of the financial year.

**Unique to Annual Version:**
- Full depreciation schedule for all fixed assets
- Comparative prior year column
- Notes to the financial statements (accounting policies, inventory valuation method, related party transactions — e.g., drawings)
- Auditor's or accountant's report

---

### F3. Annual Owners' Review Pack

**What it is:** A summary pack the owner keeps for their own records at year-end — combining the key annual figures, drawings review, and notes on any significant events during the year. This is an internal document, not a submission.

**Period:** Full financial year.

**Contents:**

```
SECTION 1 — Year in Review (narrative summary)
  Sales growth vs prior year
  Gross margin movement and explanation
  Top 5 products by revenue and by profit contribution
  Key expenses that changed materially and why

SECTION 2 — Drawings Summary (annual)
  Total cash drawings for the year
  Total goods drawings (at weighted avg cost)
  Drawings as % of net profit
  Month-by-month drawings trend

SECTION 3 — Debtors Review
  Year-end outstanding balances
  Amounts written off as uncollectible
  Collection rate (% of credit sales ultimately collected)

SECTION 4 — Asset & Equipment Review
  Assets purchased during the year
  Assets disposed of or retired
  Net Book Value movement year-on-year

SECTION 5 — Liabilities Position
  Opening vs closing loan balances
  Total interest paid during the year
  Remaining repayment schedule
```

---

### F4. Annual Fixed Asset Register

**What it is:** A complete schedule of every piece of property, plant, and equipment owned by the business — from purchase date through accumulated depreciation to net book value.

**Period:** As at year-end.

**Why it exists:** The business owns real assets — shelves, equipment, computers, cameras. Without a register that tracks each one from purchase through depreciation to disposal, the Balance Sheet asset figure is just a guess. This register is what the owner looks at when deciding whether to replace or repair something.

**Structure:**

```
ANNUAL FIXED ASSET REGISTER
Upendo Stationery — As at [31 DECEMBER YYYY]
══════════════════════════════════════════════════════════

Asset Ref  Description          Category  Date Acqd  Cost     Acc Dep    NBV
FA-001     Shelving Unit Main   Fixtures  01/03/22  120,000   48,000   72,000
FA-002     Display Counter      Fixtures  01/03/22  180,000   72,000  108,000
FA-003     Cash Register        Equipment 15/06/23   85,000   17,000   68,000
FA-004     Computer + Printer   Equipment 01/01/24   95,000   19,000   76,000
FA-005     Security Camera ×2   Equipment 20/09/24   45,000    4,500   40,500
──────────────────────────────────────────────────────────────────────────────
TOTAL                                               525,000  160,500  364,500

Depreciation Method: Straight-line
Rates: Fixtures 20% p.a. | Equipment 20% p.a.
Assets checked/verified by owner: [Signature & Date]
══════════════════════════════════════════════════════════════════════════════
```

---

### F5. Annual Budget vs. Actual Report

**What it is:** A comparison of every income and expense line in the annual budget against what actually happened — with variance analysis explaining material differences.

**Period:** Full financial year.

**Why it exists:** The budget is the plan. The actual is reality. The gap between them (variance) is where management attention and learning lives. This report is used to set the *next* year's budget more accurately and to hold the business accountable to its own targets.

**Structure:**

```
ANNUAL BUDGET vs. ACTUAL
Upendo Stationery — Year Ended [31 DECEMBER YYYY]
══════════════════════════════════════════════════════════

                        Budget      Actual      Variance    Var %
NET SALES           52,000,000  51,840,000     (160,000)   (0.3%)
COGS                14,560,000  14,515,200      (44,800)   (0.3%)
GROSS PROFIT        37,440,000  37,324,800     (115,200)   (0.3%)
GP MARGIN                72.0%       72.0%           —

EXPENSES
  Rent               5,760,000   5,760,000            0     0.0%
  Salaries           8,400,000   8,400,000            0     0.0%
  Electricity        1,080,000   1,044,000       36,000     3.3%
  Maintenance          240,000     412,000     (172,000)  (71.7%) ⚠
  Other              1,800,000   1,786,000       14,000     0.8%
──────────────────────────────────────────────────────────────────
TOTAL EXPENSES      17,280,000  17,402,000     (122,000)   (0.7%)
NET PROFIT          20,160,000  19,922,800     (237,200)   (1.2%)

⚠ Maintenance variance (TZS 172,000 over budget) due to unexpected HVAC
  and shelving repairs in Q2 and Q4. Recommend TZS 450,000 budget for next year.
══════════════════════════════════════════════════════════════════════════════
```

---

## SECTION G — SPECIAL-PURPOSE REPORTS (On Demand)

---

### G1. Product Profitability Report

**What it is:** A ranking of all products by their individual gross profit contribution, using weighted average cost to determine COGS per unit.

**Period:** Any period (daily, monthly, annual — as required).

**Why it exists:** Not all products earn the same margin. A product generating high revenue may contribute little profit if its COGS is high. This report shows which products the business *should* prioritise and which it should potentially discontinue.

---

### G2. Supplier Price Movement Report

**What it is:** A trend analysis of how purchase costs per unit have changed over time for each product, by supplier.

**Period:** Rolling 12 months.

**Why it exists:** Cost inflation from suppliers directly erodes gross margin if selling prices are not adjusted accordingly. This report tells the accountant and owner whether the weighted average cost is rising and whether price increases to customers are warranted.

---

### G3. Break-Even Analysis Report

**What it is:** A calculation of the minimum sales revenue the business must achieve each month to cover all fixed costs — the point at which profit equals zero.

**Period:** Based on current cost structure (produced when cost base changes significantly).

**Formula:**
```
Break-Even Revenue = Fixed Costs / Gross Profit Margin %

Example:
Fixed Costs = TZS 1,360,800 (monthly)
GP Margin  = 71.9%
Break-Even = 1,360,800 / 0.719 = TZS 1,892,629 per month

Safety Margin = Net Sales − Break-Even = 4,394,800 − 1,892,629 = TZS 2,502,171
Safety Margin % = 2,502,171 / 4,394,800 = 57.0%
```

**Why it exists:** Tells the owner exactly how much sales can fall before the business starts losing money. Essential for risk assessment and for pricing decisions.

---

### G4. Cash Flow Forecast (13-Week Rolling)

**What it is:** A forward-looking projection of weekly cash inflows and outflows for the next 13 weeks, based on known obligations (rent due dates, loan repayment schedules, expense recurrence patterns) and estimated sales.

**Period:** Forward-looking — 13 weeks from current date.

**Why it exists:** Reactive accounting is not enough. The business must anticipate cash shortfalls *before* they occur. This is the most practically useful report for day-to-day business survival. A business with a healthy P&L can still fail if it runs out of cash to pay rent or suppliers.

---

## APPENDIX — Report Production Schedule

```
REPORT PRODUCTION CALENDAR — Upendo Stationery
══════════════════════════════════════════════════════════

Frequency     Report                               Produced By     Deadline
─────────────────────────────────────────────────────────────────────────────
Intraday      Live Sales Ticker (A1)               System          Continuous
Intraday      Stock Alert (A2)                     System          After each sale
Daily         Cash Reconciliation (B1)             Cashier         Day close
Daily         Daily Sales Report (B2)              Cashier/Acct    Day close
Daily         Daily Stock Movement (B3)            System/Acct     Day close
Daily         Expense Voucher Summary (B4)         Accountant      Day close
Weekly        Sales Performance (C1)               Accountant      Every Monday
Weekly        Debtor Aging Short (C2)              Accountant      Every Monday
Weekly        Purchase Summary (C3)                Accountant      Every Monday
Monthly       Income Statement (D1)                Accountant      5th of next month
Monthly       Balance Sheet (D2)                   Accountant      5th of next month
Monthly       Cash Flow Statement (D3)             Accountant      5th of next month
Monthly       Expense Analysis (D4)                Accountant      5th of next month
Monthly       Debtor Aging Full (D5)               Accountant      5th of next month
Monthly       Liability Schedule (D6)              Accountant      5th of next month
Monthly       Drawings Summary (D7)                Accountant      5th of next month
Quarterly     Management Accounts Pack (E1)        Accountant      15th after quarter
Quarterly     Stock Valuation (E2)                 Accountant/Owner 15th after quarter
Annual        Audited P&L (F1)                     Accountant      31 March (90d after YE)
Annual        Audited Balance Sheet (F2)           Accountant      31 March
Annual        Owners' Review Pack (F3)              Owner/Accountant 31 January
Annual        Fixed Asset Register (F4)            Accountant      31 March
Annual        Budget vs. Actual (F5)               Accountant      31 January
Ad hoc        Product Profitability (G1)           Accountant      On request
Ad hoc        Break-Even Analysis (G3)             Accountant      On request
Rolling       Cash Flow Forecast (G4)              Accountant      Every Friday
══════════════════════════════════════════════════════════════════════════════
```

---

## SECTION H — MODEL CHANGES, MODIFICATIONS & NEW MODELS FOR REPORT CAPABILITY

> **Purpose of this section:** Every report described in Sections A–G requires specific data to exist in the database in a specific shape. This section is the bridge between the accounting requirement and the Django implementation. It lists, for every gap between the current model set and what the reports demand: (1) which existing model needs a field or method added, (2) which entirely new model must be created, and (3) which service method produces the data. This is the authoritative engineering reference for the `reports` app.

---

### H0. Guiding Principles

Before touching any model, follow these rules:

**Rule 1 — Never store what can be derived.** If a value is always `a + b − c`, store `a`, `b`, `c` and compute the result in a `@property` or an ORM annotation. The original VBA code stored `month_id`, `month_name`, `amount`, and `current_balance` as columns — all of these are derivable and must not be repeated in Django.

**Rule 2 — Monetary fields are always `DecimalField(max_digits=15, decimal_places=2)`.** Never `FloatField`. Floats accumulate rounding error in financial calculations, which breaks the accounting equation over time.

**Rule 3 — Every model that participates in a report period must have a single canonical date field used for filtering.** Sale → `sale_date`. Purchase → `purchase_date`. Payment → `payment_date`. Never filter on two date fields for the same model.

**Rule 4 — Every new model needs `created_at` and `updated_at` timestamps.** These are essential for tracing when data was entered or changed — invaluable when investigating discrepancies, understanding the sequence of events, or reviewing any period's activity. Add them via an abstract base class.

**Rule 5 — The accounting integrity equation must be enforced as a nightly management command**, not only as a property. Silent drift breaks Balance Sheets across periods.

---

### H1. New Abstract Base Model — `TimestampedModel`

**Gap:** No existing model in the system records when a record was created or last modified. Every financial record should carry a timestamp so the owner and accountant can trace the sequence of entries and investigate any discrepancy.

**Action:** Create one abstract base model and inherit it in every app.

```python
# apps/core/models.py  (new file — create this app)

from django.db import models


class TimestampedModel(models.Model):
    """
    Abstract base for every model in the system.
    Provides created_at and updated_at automatically.
    These are read-only in the admin — never edited by users.
    Helps trace exactly when any record was created or last modified.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

**Apply to:** Every model in every app. Migration: add `created_at` and `updated_at` to all existing tables via `python manage.py makemigrations`.

**Reports unlocked:** All reports with "Prepared by / Date" footers. Every report can show when it was generated and by whom.

---

### H2. Modifications to `apps/catalog/models.py`

#### H2.1 — `ProductSpec` — Add `selling_price` and deprecation-proof WAC field

**Gap:** `ProductSpec` has `default_cost_price` and `default_selling_price` but no authoritative `current_weighted_average_cost`. The WAC is computed live by `AccountingService` — correct, but slow for the Stock Valuation Report (E2) over 123+ products.

**Action:** Add a cached WAC field that is updated after every purchase batch is saved.

```python
# Modification to existing ProductSpec in apps/catalog/models.py

class ProductSpec(TimestampedModel):   # ← inherit TimestampedModel
    # ... existing fields unchanged ...

    # NEW FIELDS
    cached_wac = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name='Cached Weighted Avg Cost',
        help_text='Refreshed after every PurchaseDetail save. '
                  'Used for fast stock valuation. '
                  'Source of truth is AccountingService.weighted_average_cost().'
    )
    cached_stock_value = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name='Cached Stock Value (TZS)',
        help_text='= current_stock × cached_wac. Refreshed on every transaction.'
    )

    # NEW METHOD
    def refresh_wac(self):
        """
        Recalculate and persist the weighted average cost.
        Call after every PurchaseDetail save/delete.
        Formula: total_purchase_cost_all_time / total_purchased_qty_all_time
        WAC is cumulative — it uses ALL purchase history, not just the current period,
        so the cost per unit reflects the true blended cost across all batches ever bought.
        """
        from django.db.models import Sum
        from django.db.models.functions import Coalesce
        from decimal import Decimal

        agg = self.purchase_details.aggregate(
            total_cost=Coalesce(
                Sum(models.ExpressionWrapper(
                    models.F('quantity') * models.F('unit_cost'),
                    output_field=models.DecimalField()
                )), Decimal('0')
            ),
            total_qty=Coalesce(Sum('quantity'), 0)
        )
        if agg['total_qty'] > 0:
            self.cached_wac = agg['total_cost'] / agg['total_qty']
        else:
            self.cached_wac = Decimal('0')
        self.cached_stock_value = self.current_stock * self.cached_wac
        self.save(update_fields=['cached_wac', 'cached_stock_value'])

    def update_stock(self):
        # ... existing code unchanged ...
        self.save(update_fields=['current_stock'])
        self.refresh_wac()   # ← ADD THIS LINE at the end
```

**Reports unlocked:** E2 (Stock Valuation), D2 (Balance Sheet inventory line), quarterly and annual stock figures.

---

#### H2.2 — `ProductSpec` — Add `budget_monthly_sales` for Budget vs. Actual

**Gap:** Report F5 (Budget vs. Actual) requires a budgeted figure to compare against. Currently no budget data exists anywhere in the system.

**Action:** Add a simple budget field at the product level.

```python
    # NEW FIELD on ProductSpec
    budget_monthly_sales_qty = models.PositiveIntegerField(
        default=0,
        help_text='Expected units to sell per month — used for Budget vs Actual report (F5).'
    )
```

**Reports unlocked:** F5 (Annual Budget vs. Actual), E1 (Quarterly KPI dashboard).

---

### H3. Modifications to `apps/inventory/models.py`

#### H3.1 — `Purchase` — Add `carriage_inwards` field

**Gap:** The live P&L from the VBA system shows `Add: Carriage Inwards` as a separate line in COGS. The current `Purchase` model has no field for this. `AccountingService.to_income_statement()` already returns `'carriage_inwards': Decimal('0')` with a comment "not tracked yet" — this must now be tracked.

**Action:** Add to `Purchase` model.

```python
# Modification to existing Purchase in apps/inventory/models.py

class Purchase(TimestampedModel):   # ← inherit TimestampedModel
    supplier = models.ForeignKey(...)
    purchase_date = models.DateTimeField(...)
    invoice_number = models.CharField(...)

    # NEW FIELD
    carriage_inwards = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        help_text='Transport/freight cost to bring goods to shop. '
                  'Added to COGS — it is a real cost of acquiring stock. Allocated across all items in this purchase.'
    )
    notes = models.TextField(blank=True)   # NEW — for audit trail
```

**Update `AccountingService.carriage_inwards()` method:**

```python
# apps/reports/services/accounting.py — modify existing method

def carriage_inwards(self) -> Decimal:
    """Previously returned Decimal('0'). Now reads from Purchase.carriage_inwards."""
    from apps.inventory.models import Purchase
    qs = Purchase.objects.filter(
        purchase_date__date__range=(self.start, self.end)
    )
    return qs.aggregate(
        total=Coalesce(Sum('carriage_inwards'), Decimal('0'))
    )['total']

def net_purchases(self) -> Decimal:
    """Updated to include carriage inwards — freight is part of the real cost of stock."""
    return self.purchases() + self.carriage_inwards() - self.return_outwards()
```

**Reports unlocked:** D1 (Monthly Income Statement COGS section), E1 (Quarterly management pack — COGS accuracy), and any annual summary.

---

#### H3.2 — `PurchaseDetail` — Call `refresh_wac()` on save and delete

**Gap:** `PurchaseDetail.save()` currently calls `product_spec.update_stock()` but not `refresh_wac()`. After H2.1 changes, `update_stock()` already calls `refresh_wac()` — but `PurchaseDetail.delete()` does not trigger either. Add signal or override `delete()`.

```python
# Modification to PurchaseDetail in apps/inventory/models.py

    def delete(self, *args, **kwargs):
        spec = self.product_spec   # capture before deletion
        super().delete(*args, **kwargs)
        spec.update_stock()        # recalculate stock and WAC after deletion
```

---

### H4. Modifications to `apps/sales/models.py`

#### H4.1 — `Sale` — Add `reference_number` for Cash Reconciliation

**Gap:** Report B1 (Daily Cash Reconciliation) requires a traceable reference for every cash transaction. Currently `Sale` has no reference number — the only identifier is the auto-incremented PK.

```python
# Modification to Sale model

class Sale(TimestampedModel):
    # ... existing fields ...
    reference_number = models.CharField(
        max_length=50, blank=True, unique=True,
        help_text='Auto-generated sale reference e.g. SL-2026-004020. '
                  'Printed on receipts and used in cash reconciliation.'
    )

    def save(self, *args, **kwargs):
        if not self.reference_number:
            # Generate on first save after pk is assigned
            super().save(*args, **kwargs)
            self.reference_number = f"SL-{self.sale_date.year}-{self.pk:06d}"
            self.save(update_fields=['reference_number'])
        else:
            super().save(*args, **kwargs)
        self.product_spec.update_stock()
```

**Reports unlocked:** B1 (Cash Reconciliation — voucher trail), B2 (Daily Sales Report — reference column).

---

#### H4.2 — `Drawing` — Add `drawing_type` to distinguish cash vs. goods

**Gap:** Report D7 (Monthly Drawings Summary) separates cash drawings from goods drawings. The current `Drawing` model cannot distinguish between the two — it only has `product_spec`, implying goods only.

```python
# Modification to Drawing model in apps/sales/models.py

class Drawing(TimestampedModel):
    DRAWING_TYPES = [
        ('GOODS', 'Goods (inventory items)'),
        ('CASH', 'Cash withdrawal'),
    ]
    drawing_type = models.CharField(         # NEW FIELD
        max_length=10,
        choices=DRAWING_TYPES,
        default='GOODS',
    )
    cash_amount = models.DecimalField(       # NEW FIELD
        max_digits=15, decimal_places=2,
        default=0,
        help_text='Amount in TZS if drawing_type is CASH. '
                  'Zero for goods drawings — goods value is qty × wac.'
    )
    # product_spec becomes nullable — cash drawings have no product
    product_spec = models.ForeignKey(
        ProductSpec, on_delete=models.PROTECT,
        related_name='drawings',
        null=True, blank=True    # ← CHANGE: was not nullable
    )

    @property
    def amount(self):
        if self.drawing_type == 'CASH':
            return self.cash_amount
        if self.product_spec:
            return self.quantity * self.product_spec.cached_wac
        return Decimal('0')
```

**Reports unlocked:** D7 (Drawings Summary — full breakdown by cash vs. goods), D2 (Balance Sheet equity section — accurate owner equity deduction).

---

### H5. Modifications to `apps/credit/models.py`

#### H5.1 — `Debt` — Add `reference_number` and `payment_method`

**Gap:** Report D5 (Monthly Debtor Aging) and B2 (Daily Sales) show a `Ref` column for each credit sale. `Debt` has no reference. Additionally, credit sales can be partially cash + partially on account in some retail scenarios; the payment method on the debt indicates the agreed repayment channel.

```python
# Modifications to Debt model

class Debt(TimestampedModel):
    # ... existing fields ...
    reference_number = models.CharField(
        max_length=50, blank=True, unique=True,
        help_text='Auto-generated e.g. DT-2026-0041. Used in aging reports.'
    )
    payment_method = models.ForeignKey(    # NEW — agreed repayment method
        'finance.PaymentMethod',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Expected repayment channel (M-Pesa, Cash, Bank).'
    )

    def save(self, *args, **kwargs):
        if not self.reference_number:
            super().save(*args, **kwargs)
            self.reference_number = f"DT-{self.sale_date.year}-{self.pk:04d}"
            self.save(update_fields=['reference_number'])
        else:
            super().save(*args, **kwargs)
        self.product_spec.update_stock()
```

**Reports unlocked:** D5 (Full Debtor Aging — Ref column), C2 (Weekly Aging — Ref column), B2 (Daily Sales — Credit Sales Detail).

---

#### H5.2 — `Debtor` — Add `credit_limit` and `is_blocked`

**Gap:** The business currently has no mechanism to prevent further credit to a debtor who has 90d+ overdue balances. Report D5 flags this manually. The model should enforce it.

```python
# New fields on Debtor model

class Debtor(TimestampedModel):
    # ... existing fields ...
    credit_limit = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        help_text='Maximum outstanding balance allowed. 0 = no limit set.'
    )
    is_blocked = models.BooleanField(
        default=False,
        help_text='If True, no new credit sales can be created for this debtor. '
                  'Set manually or by the nightly aging check command.'
    )

    @property
    def is_over_limit(self) -> bool:
        if self.credit_limit == 0:
            return False
        return self.outstanding_balance > self.credit_limit
```

**New validation in `DebtForm.clean()`:**

```python
def clean(self):
    cleaned = super().clean()
    debtor = cleaned.get('debtor')
    if debtor and debtor.is_blocked:
        raise ValidationError(
            f"{debtor.name} is blocked for credit. "
            "Outstanding balance must be cleared before new credit is extended."
        )
    return cleaned
```

**Reports unlocked:** D5 (Aging — blocked flag column), C2 (Weekly aging — credit limit utilisation).

---

### H6. Modifications to `apps/finance/models.py`

#### H6.1 — `ExpenseType` — Add `is_cogs` flag

**Gap:** Report D1 (Income Statement) separates COGS from Operating Expenses. Currently all expenses flow into "Operating Expenses." However, Carriage Inwards is a COGS expense, not an operating expense. Future expense types like spoilage or damage could also be COGS. The system needs to know which expense types belong above the gross profit line.

```python
# Modification to ExpenseType

class ExpenseType(TimestampedModel):
    name = models.CharField(max_length=255, unique=True)
    is_cogs = models.BooleanField(       # NEW FIELD
        default=False,
        help_text='If True, this expense appears in COGS on the Income Statement above the Gross Profit line, '
                  'not in Operating Expenses below it. Example: Carriage Inwards, Stock Spoilage.'
    )
    display_order = models.PositiveSmallIntegerField(  # NEW FIELD
        default=0,
        help_text='Controls order of appearance on Income Statement. '
                  'Lower numbers appear first.'
    )

    class Meta:
        ordering = ['display_order', 'name']
```

**Reports unlocked:** D1 (Monthly Income Statement — correct COGS vs. Operating split), E1 (Quarterly — same), and any annual summary.

---

#### H6.2 — `Payment` — Add `payment_reference` and `approved_by`

**Gap:** Report B4 (Daily Expense Summary) needs a traceable reference per payment so the owner can quickly locate what was paid and who authorised it. The current `reference_number` is optional free-text — it needs to be auto-generated and consistent.

```python
# Modification to Payment model

class Payment(TimestampedModel):
    # ... existing fields ...
    payment_reference = models.CharField(  # NEW FIELD — replaces free-text reference_number
        max_length=50, blank=True, unique=True,
        help_text='Auto-generated: EXP-YYYY-NNN for expenses, LN-YYYY-NNN for liability payments. '
                  'Printed on payment records and used in expense summaries.'
    )
    approved_by = models.CharField(        # NEW FIELD
        max_length=255, blank=True,
        help_text='Name of owner or manager who authorised this payment. '
                  'Keeps the owner in control of every cash outflow.'
    )

    def save(self, *args, **kwargs):
        if not self.payment_reference:
            super().save(*args, **kwargs)
            prefix = 'EXP' if self.payment_type == 'EXPENSE' else 'LN'
            self.payment_reference = f"{prefix}-{self.payment_date.year}-{self.pk:04d}"
            self.save(update_fields=['payment_reference'])
        else:
            super().save(*args, **kwargs)
```

**Reports unlocked:** B4 (Daily Expense Summary — payment reference column), D4 (Monthly Expense Analysis — traceable reference per line).

---

#### H6.3 — `LiabilityItem` — Add `interest_type` and monthly accrual method

**Gap:** Report D6 (Monthly Liability Schedule) requires splitting each payment into principal and interest components AND showing monthly interest accrual (even if not yet paid). The current model stores `rate` but has no method to compute the monthly interest charge.

```python
# Modification to LiabilityItem

class LiabilityItem(TimestampedModel):
    INTEREST_TYPES = [
        ('FLAT', 'Flat Rate (on original amount)'),
        ('REDUCING', 'Reducing Balance (on outstanding principal)'),
        ('NONE', 'No Interest'),
    ]
    # ... existing fields ...
    interest_type = models.CharField(     # NEW FIELD
        max_length=20,
        choices=INTEREST_TYPES,
        default='REDUCING',
    )

    def monthly_interest_charge(self, as_of_date=None) -> Decimal:
        """
        Compute the interest accruing for the month containing as_of_date.
        Used in Report D6 (Liability Schedule) and D1 (Interest expense on P&L).
        """
        from decimal import Decimal
        if not self.rate or self.interest_type == 'NONE':
            return Decimal('0')

        monthly_rate = self.rate / Decimal('12')

        if self.interest_type == 'FLAT':
            return self.original_amount * monthly_rate
        elif self.interest_type == 'REDUCING':
            return self.current_balance * monthly_rate
        return Decimal('0')

    def amortisation_schedule(self, months: int = 12) -> list:
        """
        Produce a list of {month, opening_balance, interest, principal, closing_balance}
        dicts for Report D6 (Liability Schedule — forward payment planning).
        """
        from datetime import date
        import calendar
        schedule = []
        balance = self.current_balance
        monthly_payment = self.amount_per_return or Decimal('0')
        today = date.today()

        for i in range(months):
            month = (today.month + i - 1) % 12 + 1
            year = today.year + (today.month + i - 1) // 12
            monthly_rate = (self.rate or Decimal('0')) / Decimal('12')

            if self.interest_type == 'REDUCING':
                interest = balance * monthly_rate
            elif self.interest_type == 'FLAT':
                interest = self.original_amount * monthly_rate
            else:
                interest = Decimal('0')

            principal = max(monthly_payment - interest, Decimal('0'))
            closing = max(balance - principal, Decimal('0'))

            schedule.append({
                'month': f"{calendar.month_abbr[month]} {year}",
                'opening_balance': balance,
                'interest': interest,
                'principal': principal,
                'payment': monthly_payment,
                'closing_balance': closing,
            })
            balance = closing
            if balance <= 0:
                break

        return schedule
```

**Reports unlocked:** D6 (Monthly Liability Schedule — full amortisation detail with interest/principal split), D1 (Interest expense line in Operating Expenses — accurate P&L).

---

### H7. Modifications to `apps/assets/models.py`

#### H7.1 — `Asset` — Full depreciation tracking: cost, NBV, disposal

**Gap:** The current `Asset` model stores only `worth` and `date_checked`. It cannot produce Report F4 (Fixed Asset Register) or the depreciation charge needed for D1 (P&L) and D3 (Cash Flow Statement — add-back depreciation). Proper asset tracking requires: original cost, accumulated depreciation, net book value, depreciation method, and a record when an asset is sold or scrapped.

```python
# Major modification to Asset model in apps/assets/models.py

class Asset(TimestampedModel):
    DEPRECIATION_METHODS = [
        ('SL', 'Straight-Line'),
        ('DB', 'Declining Balance'),
        ('NONE', 'No Depreciation (Land/Art)'),
    ]

    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT, related_name='assets')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # ASSET TRACKING FIELDS — all new
    asset_reference = models.CharField(
        max_length=50, blank=True, unique=True,
        help_text='Auto-generated: FA-001, FA-002 etc.'
    )
    cost_price = models.DecimalField(          # replaces 'worth'
        max_digits=15, decimal_places=2,
        help_text='Original purchase price (TZS). Never changes after acquisition.'
    )
    acquisition_date = models.DateField(
        help_text='Date the asset was purchased/put into service.'
    )
    depreciation_method = models.CharField(
        max_length=10, choices=DEPRECIATION_METHODS, default='SL'
    )
    depreciation_rate = models.DecimalField(
        max_digits=5, decimal_places=4,
        default=Decimal('0.20'),
        help_text='Annual depreciation rate (e.g. 0.20 = 20% p.a.). '
                  'Typical rates: furniture/fixtures 20%, equipment 20%, computers 33%.'
    )
    residual_value = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        help_text='Estimated scrap value at end of useful life.'
    )
    disposal_date = models.DateField(
        null=True, blank=True,
        help_text='Date asset was sold, scrapped, or written off.'
    )
    disposal_proceeds = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0
    )
    notes = models.TextField(blank=True)

    # Legacy field kept for migration compatibility, computed going forward
    # worth = models.DecimalField(...)  ← DEPRECATE, replace with net_book_value property

    class Meta:
        ordering = ['asset_type__name', 'name']

    def __str__(self):
        return f"{self.asset_reference} — {self.name}"

    @property
    def accumulated_depreciation(self) -> Decimal:
        """
        Straight-line: (cost − residual) × rate × years_in_service.
        Capped at (cost − residual).
        """
        from datetime import date
        import math
        if self.depreciation_method == 'NONE':
            return Decimal('0')

        end_date = self.disposal_date or date.today()
        years = (end_date - self.acquisition_date).days / Decimal('365.25')

        depreciable = self.cost_price - self.residual_value
        if self.depreciation_method == 'SL':
            acc_dep = depreciable * self.depreciation_rate * years
        elif self.depreciation_method == 'DB':
            # Declining balance: cost × (1 − rate)^years
            acc_dep = self.cost_price * (1 - (1 - self.depreciation_rate) ** years)
        else:
            return Decimal('0')

        return min(acc_dep, depreciable).quantize(Decimal('0.01'))

    @property
    def net_book_value(self) -> Decimal:
        """NBV = Cost − Accumulated Depreciation."""
        return self.cost_price - self.accumulated_depreciation

    @property
    def annual_depreciation_charge(self) -> Decimal:
        """Monthly and annual depreciation charge for P&L and Cash Flow."""
        if self.depreciation_method == 'NONE':
            return Decimal('0')
        return ((self.cost_price - self.residual_value) * self.depreciation_rate).quantize(Decimal('0.01'))

    @property
    def monthly_depreciation_charge(self) -> Decimal:
        return (self.annual_depreciation_charge / 12).quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        if not self.asset_reference:
            super().save(*args, **kwargs)
            self.asset_reference = f"FA-{self.pk:03d}"
            self.save(update_fields=['asset_reference'])
        else:
            super().save(*args, **kwargs)
```

**Reports unlocked:** F4 (Fixed Asset Register — cost, accumulated depreciation, NBV per asset), D1 (Depreciation charge in Operating Expenses), D3 (Cash Flow Statement — add-back depreciation), D2 (Balance Sheet — accurate NBV of non-current assets).

---

### H8. New Model — `apps/finance/models.py` — `BudgetLine`

**Gap:** Report F5 (Budget vs. Actual) and E1 (Quarterly KPI) require budgeted figures. Currently no budget model exists at all. Budget must be set at the level of expense type and revenue per month.

```python
# NEW MODEL — add to apps/finance/models.py

class BudgetLine(TimestampedModel):
    """
    Monthly budget target for a revenue or expense category.
    One row per (financial_year, month, budget_type, category).
    Used exclusively for Budget vs. Actual reporting (F5, E1).
    """
    BUDGET_TYPES = [
        ('REVENUE', 'Net Sales Revenue'),
        ('COGS', 'Cost of Goods Sold'),
        ('EXPENSE', 'Operating Expense'),
        ('CAPEX', 'Capital Expenditure'),
    ]

    financial_year = models.PositiveSmallIntegerField(
        help_text='e.g. 2026'
    )
    month = models.PositiveSmallIntegerField(
        help_text='1 = January … 12 = December'
    )
    budget_type = models.CharField(max_length=20, choices=BUDGET_TYPES)
    expense_type = models.ForeignKey(
        ExpenseType, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Populated when budget_type = EXPENSE. Null for REVENUE/COGS.'
    )
    description = models.CharField(
        max_length=255, blank=True,
        help_text='e.g. "Rent", "Salaries", "Target Net Sales"'
    )
    budgeted_amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_by = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = [['financial_year', 'month', 'budget_type', 'expense_type']]
        ordering = ['financial_year', 'month', 'budget_type']
        verbose_name = 'Budget Line'

    def __str__(self):
        return (
            f"{self.financial_year}/{self.month:02d} — "
            f"{self.get_budget_type_display()} — "
            f"TZS {self.budgeted_amount:,.0f}"
        )

    @classmethod
    def annual_total(cls, year: int, budget_type: str, expense_type=None) -> Decimal:
        """Sum all 12 months for one category in a given year."""
        from django.db.models import Sum
        from django.db.models.functions import Coalesce
        qs = cls.objects.filter(financial_year=year, budget_type=budget_type)
        if expense_type:
            qs = qs.filter(expense_type=expense_type)
        return qs.aggregate(t=Coalesce(Sum('budgeted_amount'), Decimal('0')))['t']
```

**Reports unlocked:** F5 (Annual Budget vs. Actual — all rows), E1 (Quarterly KPI — budget vs. actual comparison), D4 (Monthly Expense Analysis — budget column).

---

### H9. New Model — `apps/finance/models.py` — `CashRegisterSession`

**Gap:** Report B1 (Daily Cash Reconciliation) requires an opening float, a physical count, and a closing balance — none of which are currently stored. Without this model, the reconciliation is manual and unauditable.

```python
# NEW MODEL — add to apps/finance/models.py

class CashRegisterSession(TimestampedModel):
    """
    Represents one trading day's cash register session.
    Opened at start of day (with opening float), closed at end of day
    (with physical count). The system cash position is computed from
    all transactions in Sale, DebtReturn, and Payment for that date.
    Used exclusively for Report B1 (Daily Cash Reconciliation).
    """
    STATUS_CHOICES = [
        ('OPEN', 'Open — day in progress'),
        ('CLOSED', 'Closed — reconciled'),
        ('VARIANCE', 'Closed — variance noted'),
    ]

    session_date = models.DateField(unique=True)
    opened_by = models.CharField(max_length=255)
    closed_by = models.CharField(max_length=255, blank=True)
    opening_float = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text='Cash physically placed in till at start of day (TZS).'
    )
    physical_count_cash = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        help_text='Actual cash counted at day close.'
    )
    physical_count_mpesa = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        help_text='M-Pesa wallet balance at day close.'
    )
    variance_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        help_text='Expected − Physical. Positive = overage, Negative = shortage.'
    )
    variance_explanation = models.TextField(
        blank=True,
        help_text='Required if |variance| > TZS 1,000.'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='OPEN'
    )

    class Meta:
        ordering = ['-session_date']
        verbose_name = 'Cash Register Session'

    def __str__(self):
        return f"Session {self.session_date} [{self.status}]"

    def compute_expected_cash(self) -> Decimal:
        """
        System cash = opening_float + cash_sales + debt_repayments_cash
                     − cash_expenses_paid − cash_drawings.
        This is the 'expected' figure that the physical count should match.
        """
        from django.db.models import Sum, Q
        from django.db.models.functions import Coalesce
        from apps.sales.models import Sale, Drawing
        from apps.credit.models import DebtReturn
        from apps.finance.models import Payment

        d = self.session_date

        cash_sales = Sale.objects.filter(
            sale_date__date=d,
            payment_method__name__in=['Cash', 'cash']
        ).aggregate(t=Coalesce(Sum('amount'), Decimal('0')))

        # DebtReturn cash only
        debt_cash = DebtReturn.objects.filter(
            return_date__date=d,
            payment_method__name__in=['Cash', 'cash']
        ).aggregate(t=Coalesce(Sum('amount'), Decimal('0')))

        # Cash expenses paid from till
        cash_expenses = Payment.objects.filter(
            payment_date__date=d,
            payment_method__name__in=['Cash', 'cash'],
            payment_type='EXPENSE'
        ).aggregate(t=Coalesce(Sum('amount_paid'), Decimal('0')))

        # Cash drawings
        cash_drawings = Drawing.objects.filter(
            sale_date__date=d,
            drawing_type='CASH'
        ).aggregate(t=Coalesce(Sum('cash_amount'), Decimal('0')))

        return (
            self.opening_float
            + cash_sales['t']
            + debt_cash['t']
            - cash_expenses['t']
            - cash_drawings['t']
        )

    def close_session(self, physical_cash: Decimal, physical_mpesa: Decimal,
                      closed_by: str, explanation: str = '') -> None:
        """Called when cashier closes the day."""
        expected = self.compute_expected_cash()
        self.physical_count_cash = physical_cash
        self.physical_count_mpesa = physical_mpesa
        self.closed_by = closed_by
        self.variance_amount = expected - physical_cash
        self.variance_explanation = explanation
        self.status = 'VARIANCE' if abs(self.variance_amount) > Decimal('1000') else 'CLOSED'
        self.save()
```

**Reports unlocked:** B1 (Daily Cash Reconciliation — complete with opening float, physical count, variance, and explanation).

---

### H10. New Model — `apps/reports/models.py` — `ReportSnapshot`

**Gap:** All current reports are computed live on every request. For the monthly, quarterly, and annual reports (D1–D7, E1–E2, F1–F5), this is expensive and creates inconsistency — the P&L for May 2026 viewed in July 2026 should show exactly the same figures as when it was first produced on 5 June 2026. A snapshot model locks in the computed values.

```python
# NEW MODEL — create apps/reports/models.py (currently no models in reports app)

from django.db import models
from apps.core.models import TimestampedModel


class ReportSnapshot(TimestampedModel):
    """
    Stores a serialised (JSON) copy of a computed report for a specific period.
    Once a period is locked (e.g., the month is closed), this snapshot becomes
    the reference version. Ensures the May P&L viewed in August looks identical
    to how it looked on 5 June — data entered later for a different period
    cannot silently change a past report.

    Reports that should be snapshotted: D1, D2, D3, D4, D5, D6, E1, E2.
    """
    REPORT_CODES = [
        ('D1', 'Monthly Income Statement'),
        ('D2', 'Monthly Balance Sheet'),
        ('D3', 'Monthly Cash Flow Statement'),
        ('D4', 'Monthly Expense Analysis'),
        ('D5', 'Monthly Debtor Aging'),
        ('D6', 'Monthly Liability Schedule'),
        ('D7', 'Monthly Drawings Summary'),
        ('E1', 'Quarterly Management Accounts'),
        ('E2', 'Quarterly Stock Valuation'),
        ('F1', 'Annual Income Statement'),
        ('F2', 'Annual Balance Sheet'),
        ('F3', 'Annual Owners Review Pack'),
        ('F4', 'Annual Fixed Asset Register'),
        ('F5', 'Annual Budget vs. Actual'),
    ]

    report_code = models.CharField(max_length=10, choices=REPORT_CODES)
    period_start = models.DateField()
    period_end = models.DateField()
    generated_by = models.CharField(
        max_length=255,
        help_text='Name of accountant who ran/locked this report.'
    )
    is_locked = models.BooleanField(
        default=False,
        help_text='If True, this period is closed and signed off by the owner. '
                  'No further changes to the underlying data will alter this report. '
                  'Gives confidence that historical reports are stable.'
    )
    data = models.JSONField(
        help_text='Full serialised output of the report service for this period. '
                  'Stored as JSON. Rendered by the report template on demand.'
    )
    pdf_path = models.CharField(
        max_length=500, blank=True,
        help_text='Path to generated PDF file (WeasyPrint output) if produced.'
    )
    checksum = models.CharField(
        max_length=64, blank=True,
        help_text='SHA-256 of data field. Used to detect tampering.'
    )

    class Meta:
        unique_together = [['report_code', 'period_start', 'period_end']]
        ordering = ['-period_end', 'report_code']
        verbose_name = 'Report Snapshot'

    def __str__(self):
        return f"{self.report_code} | {self.period_start} → {self.period_end}"

    def compute_checksum(self) -> str:
        import hashlib, json
        return hashlib.sha256(
            json.dumps(self.data, sort_keys=True, default=str).encode()
        ).hexdigest()

    def lock(self, locked_by: str) -> None:
        """Freeze this period's report. Called by owner or accountant after reviewing and signing off."""
        self.is_locked = True
        self.generated_by = locked_by
        self.checksum = self.compute_checksum()
        self.save(update_fields=['is_locked', 'generated_by', 'checksum', 'updated_at'])
```

**Reports unlocked:** All monthly and quarterly reports — ensures that a period's numbers are frozen once reviewed and signed off by the owner, preventing silent retroactive drift.

---

### H11. New Management Command — `verify_accounting_integrity`

**Gap:** The accounting equation `Opening Stock + Net Purchases = COGS + Closing Stock` is currently only a comment in the master plan. It must run automatically and alert the owner/accountant if it breaks.

```python
# NEW FILE: apps/reports/management/commands/verify_accounting_integrity.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = (
        'Verify accounting integrity equations for all product specs. '
        'Run nightly via cron or Celery beat. '
        'Alerts if: Opening + NetPurchases ≠ COGS + Closing.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--date', type=str, default=None,
            help='Check as of YYYY-MM-DD (default: yesterday)'
        )
        parser.add_argument(
            '--tolerance', type=float, default=1.0,
            help='Acceptable rounding tolerance in TZS (default: 1.00)'
        )

    def handle(self, *args, **options):
        from apps.catalog.models import ProductSpec
        from apps.reports.services.accounting import AccountingService

        check_date = date.today() - timedelta(days=1)
        if options['date']:
            check_date = date.fromisoformat(options['date'])

        tolerance = Decimal(str(options['tolerance']))
        errors = []
        warnings = []

        specs = ProductSpec.objects.all()
        self.stdout.write(f"Checking {specs.count()} product specs as of {check_date}...")

        for spec in specs:
            svc = AccountingService(date(2000, 1, 1), check_date, spec.pk)
            opening = svc.opening_stock_value()
            net_purch = svc.net_purchases() + svc.carriage_inwards()
            cogs = svc.cogs()
            closing = svc.closing_stock_value()

            lhs = opening + net_purch
            rhs = cogs + closing
            diff = abs(lhs - rhs)

            if diff > tolerance:
                errors.append(
                    f"  ✘ {spec} | LHS={lhs:,.2f} RHS={rhs:,.2f} DIFF={diff:,.2f}"
                )

            # Also check that cached_stock_value matches computed closing
            cached_diff = abs(spec.cached_stock_value - closing)
            if cached_diff > tolerance:
                warnings.append(
                    f"  ⚠ {spec} | cached_stock_value={spec.cached_stock_value:,.2f} "
                    f"computed_closing={closing:,.2f}"
                )

        if errors:
            self.stderr.write(self.style.ERROR(
                f"\n{len(errors)} INTEGRITY VIOLATIONS FOUND:\n" + '\n'.join(errors)
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"✓ All {specs.count()} product specs pass the accounting equation."
            ))

        if warnings:
            self.stdout.write(self.style.WARNING(
                f"\n{len(warnings)} WAC cache mismatches (run refresh_wac):\n"
                + '\n'.join(warnings)
            ))
```

**Cron entry (add to server crontab):**

```bash
# Run integrity check every night at 23:55 (after shop closes)
55 23 * * * cd /var/www/kiyabo_duka && \
  venv/bin/python manage.py verify_accounting_integrity \
  >> /var/log/kiyabo_integrity.log 2>&1
```

---

### H12. New Service — `apps/reports/services/balance_sheet.py`

**Gap:** The current `AccountingService` produces only the Income Statement. The Balance Sheet (D2) and Cash Flow (D3) have no service yet, making those reports impossible to generate programmatically.

```python
# NEW FILE: apps/reports/services/balance_sheet.py

from decimal import Decimal
from datetime import date
from django.db.models import Sum
from django.db.models.functions import Coalesce


class BalanceSheetService:
    """
    Produces all figures required for:
      - Report D2 (Monthly Balance Sheet)
      - Report F2 (Annual Balance Sheet)
      - Report E1 (Quarterly — net assets section)

    All figures in TZS. All values as of self.as_of_date.
    """

    def __init__(self, as_of_date: date):
        self.as_of = as_of_date

    # ── NON-CURRENT ASSETS ──────────────────────────────────────────────────

    def fixed_assets_cost(self) -> Decimal:
        from apps.assets.models import Asset
        return Asset.objects.filter(
            acquisition_date__lte=self.as_of,
            disposal_date__isnull=True
        ).aggregate(
            t=Coalesce(Sum('cost_price'), Decimal('0'))
        )['t']

    def accumulated_depreciation(self) -> Decimal:
        from apps.assets.models import Asset
        assets = Asset.objects.filter(
            acquisition_date__lte=self.as_of,
            disposal_date__isnull=True
        )
        return sum(a.accumulated_depreciation for a in assets)

    def net_book_value_assets(self) -> Decimal:
        return self.fixed_assets_cost() - self.accumulated_depreciation()

    # ── CURRENT ASSETS ──────────────────────────────────────────────────────

    def inventory_value(self) -> Decimal:
        """Closing stock at weighted average cost as of as_of_date."""
        from apps.catalog.models import ProductSpec
        # Use cached_stock_value for speed; nightly integrity check validates it
        return ProductSpec.objects.aggregate(
            t=Coalesce(Sum('cached_stock_value'), Decimal('0'))
        )['t']

    def gross_receivables(self) -> Decimal:
        from apps.credit.models import Debt, DebtReturn
        from django.db.models import OuterRef, Subquery
        total_debts = Debt.objects.filter(
            sale_date__date__lte=self.as_of
        ).aggregate(t=Coalesce(Sum('amount_due'), Decimal('0')))['t']

        total_repaid = DebtReturn.objects.filter(
            return_date__date__lte=self.as_of
        ).aggregate(t=Coalesce(Sum('amount'), Decimal('0')))['t']

        return max(total_debts - total_repaid, Decimal('0'))

    def bad_debt_provision(self) -> Decimal:
        """
        Compute bad debt provision using aging buckets.
        Rate schedule: 90d+ = 10%, 61–90d = 5%, 31–60d = 1%.
        """
        from apps.credit.models import Debt
        from datetime import timedelta
        provision = Decimal('0')

        for debt in Debt.objects.filter(sale_date__date__lte=self.as_of):
            balance = debt.balance
            if balance <= 0:
                continue
            if not debt.expected_payment_date:
                continue
            days_overdue = (self.as_of - debt.expected_payment_date).days
            if days_overdue > 90:
                provision += balance * Decimal('0.10')
            elif days_overdue > 60:
                provision += balance * Decimal('0.05')
            elif days_overdue > 30:
                provision += balance * Decimal('0.01')

        return provision.quantize(Decimal('0.01'))

    def net_receivables(self) -> Decimal:
        return self.gross_receivables() - self.bad_debt_provision()

    def cash_balance(self) -> Decimal:
        """Latest closed CashRegisterSession physical_count_cash."""
        from apps.finance.models import CashRegisterSession
        session = CashRegisterSession.objects.filter(
            session_date__lte=self.as_of,
            status__in=['CLOSED', 'VARIANCE']
        ).order_by('-session_date').first()
        return session.physical_count_cash if session else Decimal('0')

    def mpesa_balance(self) -> Decimal:
        from apps.finance.models import CashRegisterSession
        session = CashRegisterSession.objects.filter(
            session_date__lte=self.as_of,
            status__in=['CLOSED', 'VARIANCE']
        ).order_by('-session_date').first()
        return session.physical_count_mpesa if session else Decimal('0')

    def total_current_assets(self) -> Decimal:
        return (
            self.inventory_value()
            + self.net_receivables()
            + self.cash_balance()
            + self.mpesa_balance()
        )

    def total_assets(self) -> Decimal:
        return self.net_book_value_assets() + self.total_current_assets()

    # ── LIABILITIES ──────────────────────────────────────────────────────────

    def long_term_liabilities(self) -> Decimal:
        from apps.finance.models import LiabilityItem
        return sum(
            item.current_balance
            for item in LiabilityItem.objects.filter(is_active=True)
            if item.maturity_date and item.maturity_date > self.as_of
        )

    def current_liabilities(self) -> Decimal:
        from apps.finance.models import PaymentObligation
        return PaymentObligation.objects.filter(
            due_date__lte=self.as_of,
            obligation_type='EXPENSE',
        ).exclude(
            amount_paid__gte=models.F('amount_due')
        ).aggregate(
            t=Coalesce(Sum('balance'), Decimal('0'))
        )['t']

    def total_liabilities(self) -> Decimal:
        return self.long_term_liabilities() + self.current_liabilities()

    # ── EQUITY ───────────────────────────────────────────────────────────────

    def total_equity(self) -> Decimal:
        return self.total_assets() - self.total_liabilities()

    # ── FULL DICT FOR TEMPLATE ───────────────────────────────────────────────

    def to_balance_sheet(self) -> dict:
        return {
            'as_of': self.as_of,
            'fixed_assets_cost': self.fixed_assets_cost(),
            'accumulated_depreciation': self.accumulated_depreciation(),
            'net_book_value': self.net_book_value_assets(),
            'inventory': self.inventory_value(),
            'gross_receivables': self.gross_receivables(),
            'bad_debt_provision': self.bad_debt_provision(),
            'net_receivables': self.net_receivables(),
            'cash': self.cash_balance(),
            'mpesa': self.mpesa_balance(),
            'total_current_assets': self.total_current_assets(),
            'total_assets': self.total_assets(),
            'long_term_liabilities': self.long_term_liabilities(),
            'current_liabilities': self.current_liabilities(),
            'total_liabilities': self.total_liabilities(),
            'total_equity': self.total_equity(),
            # Accounting equation check
            'equation_holds': abs(
                self.total_assets() - self.total_liabilities() - self.total_equity()
            ) < Decimal('1'),
        }
```

**Reports unlocked:** D2 (Balance Sheet), F2 (Annual Balance Sheet), E1 (Quarterly net assets).

---

### H13. Payment Method — Fix Hardcoded M-Pesa

**Gap:** Two problems exist simultaneously. First, `physical_count_cash` and `physical_count_mpesa` are hardcoded columns on `CashRegisterSession` — adding Tigo Pesa requires a new migration. Second, code filters by `payment_method__name='M-Pesa'` which is a string match against a name that could change. Both problems come from the same root cause: `PaymentMethod` has no structure — it is currently just a name field with no hierarchy. The fix requires building that hierarchy properly before touching anything else.

**Three changes required together:**

#### H13.1 — `PaymentMethod` — Add `method_type`

```python
# Modification to PaymentMethod in apps/finance/models.py

class PaymentMethod(TimestampedModel):
    METHOD_TYPES = [
        ('CASH', 'Physical Cash'),
        ('MOBILE_MONEY', 'Mobile Money'),   # M-Pesa, Tigo Pesa, Airtel Money, Halopesa etc.
        ('BANK', 'Bank Transfer'),
        ('CHEQUE', 'Cheque'),
    ]
    name = models.CharField(
        max_length=100, unique=True,
        help_text='e.g. "M-Pesa", "Tigo Pesa", "Airtel Money", "Cash", "CRDB Transfer"'
    )
    method_type = models.CharField(         # NEW FIELD
        max_length=20,
        choices=METHOD_TYPES,
        help_text='Category of this payment method. '
                  'Code always filters by method_type, never by name. '
                  'Adding a new mobile money provider requires only a new '
                  'PaymentMethod record — zero code changes.'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_method_type_display()})"
```

**Seed data (run once after migration):**

```python
# apps/finance/management/commands/seed_payment_methods.py

from django.core.management.base import BaseCommand
from apps.finance.models import PaymentMethod

class Command(BaseCommand):
    help = 'Seed default payment methods with correct method_type values.'

    def handle(self, *args, **options):
        methods = [
            ('Cash',          'CASH'),
            ('M-Pesa',        'MOBILE_MONEY'),
            ('Tigo Pesa',     'MOBILE_MONEY'),
            ('Airtel Money',  'MOBILE_MONEY'),
            ('Halopesa',      'MOBILE_MONEY'),
            ('Bank Transfer', 'BANK'),
        ]
        for name, method_type in methods:
            obj, created = PaymentMethod.objects.get_or_create(
                name=name, defaults={'method_type': method_type}
            )
            if not created and obj.method_type != method_type:
                obj.method_type = method_type
                obj.save(update_fields=['method_type'])
            self.stdout.write(f"{'Created' if created else 'Updated'}: {name}")
```

---

#### H13.2 — `CashRegisterSession` — Replace hardcoded fields with `SessionBalance`

**Gap:** `CashRegisterSession` currently has `physical_count_cash` and `physical_count_mpesa` as two fixed columns. Adding Tigo Pesa would require a new migration and a new hardcoded field every time. Instead, closing balances per payment method are stored in a child model — one row per channel per day.

```python
# UPDATED CashRegisterSession — remove physical_count_cash & physical_count_mpesa

class CashRegisterSession(TimestampedModel):
    session_date = models.DateField(unique=True)
    opened_by = models.CharField(max_length=255)
    closed_by = models.CharField(max_length=255, blank=True)
    opening_float = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text='Physical cash placed in till at start of day.'
    )
    # physical_count_cash   ← REMOVED
    # physical_count_mpesa  ← REMOVED
    # REPLACED BY SessionBalance child rows (one per PaymentMethod)
    variance_explanation = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('OPEN','Open'),('CLOSED','Closed'),('VARIANCE','Variance')],
        default='OPEN'
    )

    def closing_balance_for(self, method_type: str) -> Decimal:
        """
        Closing balance for all payment methods of a given type.
        e.g. session.closing_balance_for('CASH')
             session.closing_balance_for('MOBILE_MONEY')  — sums ALL mobile money providers
        Adding a new provider never changes this method.
        """
        return self.balances.filter(
            payment_method__method_type=method_type
        ).aggregate(
            t=Coalesce(Sum('physical_closing_balance'), Decimal('0'))
        )['t']

    def total_variance(self) -> Decimal:
        return self.balances.aggregate(
            t=Coalesce(Sum('variance_amount'), Decimal('0'))
        )['t']

    def compute_expected_cash(self) -> Decimal:
        """Filters by method_type='CASH', never by name."""
        from apps.sales.models import Sale, Drawing
        from apps.credit.models import DebtReturn
        from apps.finance.models import Payment
        d = self.session_date

        cash_in = Sale.objects.filter(
            sale_date__date=d, payment_method__method_type='CASH'
        ).aggregate(t=Coalesce(Sum('amount'), Decimal('0'}))['t']

        debt_cash = DebtReturn.objects.filter(
            return_date__date=d, payment_method__method_type='CASH'
        ).aggregate(t=Coalesce(Sum('amount'), Decimal('0'}))['t']

        cash_out = Payment.objects.filter(
            payment_date__date=d,
            payment_method__method_type='CASH',
            payment_type='EXPENSE'
        ).aggregate(t=Coalesce(Sum('amount_paid'), Decimal('0'}))['t']

        cash_drawings = Drawing.objects.filter(
            sale_date__date=d, drawing_type='CASH'
        ).aggregate(t=Coalesce(Sum('cash_amount'), Decimal('0'}))['t']

        return self.opening_float + cash_in + debt_cash - cash_out - cash_drawings


class SessionBalance(TimestampedModel):
    """
    One row per payment method per CashRegisterSession.
    Replaces the hardcoded physical_count_cash / physical_count_mpesa fields.
    Adding a new mobile money provider = one new PaymentMethod record.
    No migration, no code change, no new column.
    """
    session = models.ForeignKey(
        CashRegisterSession, on_delete=models.CASCADE, related_name='balances'
    )
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.PROTECT
    )
    physical_closing_balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Amount physically counted/confirmed in this channel at day close.'
    )
    system_expected_balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='What the system computed this channel should hold.'
    )
    variance_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='system_expected − physical. Positive = overage, Negative = shortage.'
    )

    class Meta:
        unique_together = [['session', 'payment_method']]
        ordering = ['payment_method__method_type', 'payment_method__name']

    def __str__(self):
        return (
            f"{self.session.session_date} | {self.payment_method.name} | "
            f"Physical: {self.physical_closing_balance:,.0f} | "
            f"Variance: {self.variance_amount:,.0f}"
        )
```

---

#### H13.3 — `BalanceSheetService` — Replace hardcoded `cash_balance()` / `mpesa_balance()`

```python
# Replace in apps/reports/services/balance_sheet.py

# REMOVE:
#   def cash_balance(self) -> Decimal: ...
#   def mpesa_balance(self) -> Decimal: ...

# REPLACE WITH:

    def closing_balance_by_type(self, method_type: str) -> Decimal:
        """
        Total physically confirmed closing balance for all methods of a given type
        from the most recent closed session on or before as_of_date.
        Works for any current or future method_type — no code changes ever needed.
        """
        from apps.finance.models import CashRegisterSession
        session = CashRegisterSession.objects.filter(
            session_date__lte=self.as_of,
            status__in=['CLOSED', 'VARIANCE']
        ).order_by('-session_date').first()
        if not session:
            return Decimal('0')
        return session.closing_balance_for(method_type)

    def total_cash_and_equivalents(self) -> Decimal:
        """Cash + all mobile money + bank float for the Balance Sheet line."""
        return (
            self.closing_balance_by_type('CASH')
            + self.closing_balance_by_type('MOBILE_MONEY')
            + self.closing_balance_by_type('BANK')
        )

# UPDATE to_balance_sheet() — replace old cash/mpesa keys:
    def to_balance_sheet(self) -> dict:
        return {
            'as_of': self.as_of,
            # ... other fields unchanged ...
            'cash':                   self.closing_balance_by_type('CASH'),
            'mobile_money':           self.closing_balance_by_type('MOBILE_MONEY'),
            'bank_float':             self.closing_balance_by_type('BANK'),
            'total_cash_equivalents': self.total_cash_and_equivalents(),
            # ... rest unchanged ...
        }
```

**Reports corrected:** B1 (Daily Cash Reconciliation — all payment channels shown separately), D2 (Balance Sheet — Cash & Equivalents covers all providers), G4 (Cash Flow Forecast — accurate opening cash position).

---

### H14. Summary Table — All Model Changes

```
MODEL CHANGE SUMMARY
══════════════════════════════════════════════════════════════════════════════════
#      Location                        Change Type      Purpose / Reports Unlocked
──────────────────────────────────────────────────────────────────────────────────
H1     apps/core/models.py             NEW FILE         TimestampedModel base — all reports
H2.1   catalog.ProductSpec             MODIFY           cached_wac, cached_stock_value — E2, D2
H2.2   catalog.ProductSpec             MODIFY           budget_monthly_sales_qty — F5, E1
H3.1   inventory.Purchase              MODIFY           carriage_inwards field — D1, COGS
H3.2   inventory.PurchaseDetail        MODIFY           delete() override — WAC integrity
H4.1   sales.Sale                      MODIFY           reference_number auto-gen — B1, B2
H4.2   sales.Drawing                   MODIFY           drawing_type + cash_amount — D7, D2
H5.1   credit.Debt                     MODIFY           reference_number, payment_method — D5, C2
H5.2   credit.Debtor                   MODIFY           credit_limit, is_blocked — D5, C2
H6.1   finance.ExpenseType             MODIFY           is_cogs, display_order — D1
H6.2   finance.Payment                 MODIFY           payment_reference, approved_by — B4, D4
H6.3   finance.LiabilityItem           MODIFY           interest_type + methods — D6, D1
H7.1   assets.Asset                    MAJOR MODIFY     Full depreciation — F4, D1, D3, D2
H8     finance.BudgetLine              NEW MODEL        Budget data — F5, E1, D4
H9     finance.CashRegisterSession     MODIFY           Remove hardcoded payment fields — B1
H9b    finance.SessionBalance          NEW MODEL        Per-channel daily balances — B1, D2
H10    reports.ReportSnapshot          NEW MODEL        Period locking — all monthly/quarterly
H11    reports/management/commands/    NEW COMMAND      Nightly integrity check — all reports
H12    reports/services/balance_sheet  NEW SERVICE      Balance Sheet data — D2, E1
H13.1  finance.PaymentMethod           MODIFY           method_type field — all payment reports
H13.3  reports/services/balance_sheet  MODIFY           Remove hardcoded mpesa_balance() — D2, B1
══════════════════════════════════════════════════════════════════════════════════



```
MODEL CHANGE SUMMARY
══════════════════════════════════════════════════════════════════════════════════
#     Location                        Change Type      Purpose / Reports Unlocked
──────────────────────────────────────────────────────────────────────────────────
H1    apps/core/models.py             NEW FILE         TimestampedModel base — all reports
H2.1  catalog.ProductSpec             MODIFY           cached_wac, cached_stock_value — E2, D2
H2.2  catalog.ProductSpec             MODIFY           budget_monthly_sales_qty — F5, E1
H3.1  inventory.Purchase              MODIFY           carriage_inwards field — D1, F1 COGS
H3.2  inventory.PurchaseDetail        MODIFY           delete() override — WAC integrity
H4.1  sales.Sale                      MODIFY           reference_number auto-gen — B1, B2
H4.2  sales.Drawing                   MODIFY           drawing_type + cash_amount — D7, D2
H5.1  credit.Debt                     MODIFY           reference_number, payment_method — D5, C2
H5.2  credit.Debtor                   MODIFY           credit_limit, is_blocked — D5, C2
H6.1  finance.ExpenseType             MODIFY           is_cogs, display_order — D1, F1
H6.2  finance.Payment                 MODIFY           payment_reference, approved_by — B4, D4
H6.3  finance.LiabilityItem           MODIFY           interest_type + methods — D6, D1
H7.1  assets.Asset                    MAJOR MODIFY     Full depreciation — F4, D1, D3, D2
H8    finance.BudgetLine              NEW MODEL        Budget data — F5, E1, D4
H9    finance.CashRegisterSession     NEW MODEL        Daily cash reconciliation — B1
H10   reports.ReportSnapshot          NEW MODEL        Period locking — all monthly/quarterly reports
H11   reports/management/commands/    NEW COMMAND      Nightly integrity check — all reports
H12   reports/services/balance_sheet  NEW SERVICE      Balance Sheet data — D2, F2, E1
══════════════════════════════════════════════════════════════════════════════════

NEW MIGRATIONS REQUIRED (in order):
  1. python manage.py makemigrations core
  2. python manage.py makemigrations catalog
  3. python manage.py makemigrations inventory
  4. python manage.py makemigrations sales
  5. python manage.py makemigrations credit
  6. python manage.py makemigrations finance      ← includes PaymentMethod.method_type,
                                                      BudgetLine, CashRegisterSession update,
                                                      SessionBalance (new)
  7. python manage.py makemigrations assets
  8. python manage.py makemigrations reports
  9. python manage.py migrate
 10. python manage.py seed_payment_methods        ← seeds M-Pesa, Tigo Pesa, Airtel etc.

DATA BACKFILL COMMANDS (run after migrate):
  python manage.py shell -c "
    from apps.catalog.models import ProductSpec
    for s in ProductSpec.objects.all():
        s.refresh_wac()
    print('WAC backfill complete.')
  "

  python manage.py shell -c "
    from apps.assets.models import Asset
    for a in Asset.objects.all():
        a.asset_reference = f'FA-{a.pk:03d}'
        a.save(update_fields=['asset_reference'])
    print('Asset reference backfill complete.')
  "
══════════════════════════════════════════════════════════════════════════════════
```

---

*Document: Kiyabo Duka Accounting & Financial Reports Reference*
*Version: 2.1 — May 2026 (added Section H — Model Changes; H13 payment method fix)*
*Prepared for: Upendo Stationery, Dar es Salaam, Tanzania*
*Currency: TZS (Tanzanian Shillings)*
*Costing Method: Weighted Average (WAC) | Basis: Accrual accounting*
*Focus: Internal business management accounting — building a solid foundation the business actually uses every day.*
