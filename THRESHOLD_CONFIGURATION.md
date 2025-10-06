# Alert Threshold Configuration Guide

Complete guide to configuring alert thresholds for the BSE Insider Trading Tracker.

---

## Understanding Thresholds

The system uses **TWO** thresholds to trigger alerts:

1. **MIN_SHARES_THRESHOLD** - Minimum number of shares
2. **MIN_VALUE_THRESHOLD** - Minimum transaction value in INR

**Important:** Alerts trigger if **EITHER** condition is met (OR logic, not AND).

### Example:
```
MIN_SHARES_THRESHOLD=100000
MIN_VALUE_THRESHOLD=10000000
```

This triggers alerts when:
- Transaction has ≥1,00,000 shares **OR**
- Transaction value ≥₹1,00,00,000 **OR**
- Both conditions met

---

## Method 1: Environment Variable (Simple)

### Step 1: Open .env File

**Windows:**
```bash
notepad .env
```

**Mac/Linux:**
```bash
nano .env
```

### Step 2: Edit Thresholds

Find these lines:
```env
MIN_SHARES_THRESHOLD=100000
MIN_VALUE_THRESHOLD=10000000
```

Change to your desired values:
```env
MIN_SHARES_THRESHOLD=50000
MIN_VALUE_THRESHOLD=5000000
```

### Step 3: Save and Close

**Windows Notepad:** File → Save → Close

**Mac/Linux nano:** 
- Press `Ctrl+O` to save
- Press `Enter` to confirm
- Press `Ctrl+X` to exit

### Step 4: Restart Script

```bash
python main.py
```

Changes take effect immediately.

---

## Method 2: Database Configuration (Advanced)

Allows multiple rules with different priorities.

### Step 1: Open Supabase

Go to: https://tyibyuwusjpogfknameh.supabase.co

### Step 2: Open SQL Editor

Click "SQL Editor" → "New Query"

### Step 3: Add Custom Rule

Paste and modify:

```sql
INSERT INTO alert_configurations (
    alert_name,
    min_shares,
    min_value,
    is_active,
    priority
) VALUES (
    'Medium Threshold Alert',  -- Change this name
    50000,                      -- Change share threshold
    5000000,                    -- Change value threshold
    true,                       -- Keep as true
    50                          -- Higher number = higher priority
);
```

### Step 4: Run Query

Click "Run" or press `Ctrl+Enter`

### Step 5: Verify

Click "Table Editor" → "alert_configurations"

You should see your new rule.

---

## Recommended Threshold Presets

### Conservative (Fewer Alerts)

Only very significant transactions:

```env
MIN_SHARES_THRESHOLD=500000        # 5 lakh shares
MIN_VALUE_THRESHOLD=50000000       # ₹5 crores
```

**Expected alerts per day:** 1-3

**Use when:**
- You only want major insider moves
- Tracking large cap companies
- Want to reduce email noise

---

### Moderate (Balanced) - **DEFAULT**

Balance between coverage and noise:

```env
MIN_SHARES_THRESHOLD=100000        # 1 lakh shares
MIN_VALUE_THRESHOLD=10000000       # ₹1 crore
```

**Expected alerts per day:** 5-10

**Use when:**
- General market monitoring
- Mix of large and mid cap companies
- Standard insider tracking

---

### Aggressive (More Alerts)

Catch smaller but still significant transactions:

```env
MIN_SHARES_THRESHOLD=50000         # 50 thousand shares
MIN_VALUE_THRESHOLD=5000000        # ₹50 lakhs
```

**Expected alerts per day:** 15-25

**Use when:**
- Tracking mid/small cap companies
- Want comprehensive coverage
- Researching insider patterns

---

### Very Aggressive (Maximum Coverage)

Almost all insider transactions:

```env
MIN_SHARES_THRESHOLD=10000         # 10 thousand shares
MIN_VALUE_THRESHOLD=1000000        # ₹10 lakhs
```

**Expected alerts per day:** 30-50

**Use when:**
- Analyzing specific companies deeply
- Academic research
- Complete insider activity tracking

---

## Threshold Calculation Guide

### By Share Count

Calculate based on typical transaction sizes:

```
Small transaction:  10,000 - 50,000 shares
Medium transaction: 50,000 - 100,000 shares
Large transaction:  100,000 - 500,000 shares
Very large:         500,000+ shares
```

**Recommendation:** Set threshold at "Large" level (100,000) for meaningful signals.

### By Transaction Value

Calculate based on investment size:

```
₹10 lakhs    = Small investor level
₹50 lakhs    = Serious investor level
₹1 crore     = Institutional/HNI level
₹5 crores    = Major transaction
₹10 crores+  = Significant market event
```

**Recommendation:** Set at ₹1 crore for professional investor signals.

### By Company Market Cap

Adjust thresholds based on company size:

**Large Cap (₹20,000 Cr+)**
```env
MIN_SHARES_THRESHOLD=100000
MIN_VALUE_THRESHOLD=10000000
```

**Mid Cap (₹5,000-20,000 Cr)**
```env
MIN_SHARES_THRESHOLD=50000
MIN_VALUE_THRESHOLD=5000000
```

**Small Cap (Below ₹5,000 Cr)**
```env
MIN_SHARES_THRESHOLD=25000
MIN_VALUE_THRESHOLD=2500000
```

---

## Multiple Threshold Rules

Create different rules for different purposes using database configuration.

### Example: Three-Tier System

```sql
-- Tier 1: Major transactions (highest priority)
INSERT INTO alert_configurations (
    alert_name, min_shares, min_value, is_active, priority
) VALUES (
    'Major Transactions', 500000, 50000000, true, 100
);

-- Tier 2: Significant transactions
INSERT INTO alert_configurations (
    alert_name, min_shares, min_value, is_active, priority
) VALUES (
    'Significant Transactions', 100000, 10000000, true, 80
);

-- Tier 3: Notable transactions
INSERT INTO alert_configurations (
    alert_name, min_shares, min_value, is_active, priority
) VALUES (
    'Notable Transactions', 50000, 5000000, true, 60
);
```

### Example: By Transaction Type

```sql
-- Only promoter acquisitions (buying signal)
INSERT INTO alert_configurations (
    alert_name, min_shares,
    person_categories, transaction_types,
    is_active, priority
) VALUES (
    'Promoter Buying',
    50000,
    ARRAY['Promoter', 'Promoter Group'],
    ARRAY['ACQUISITION'],
    true,
    90
);

-- Large disposals (warning signal)
INSERT INTO alert_configurations (
    alert_name, min_shares,
    transaction_types, is_active, priority
) VALUES (
    'Large Selling',
    200000,
    ARRAY['DISPOSAL'],
    true,
    85
);

-- Pledge warnings (risk signal)
INSERT INTO alert_configurations (
    alert_name, min_shares,
    transaction_types, is_active, priority
) VALUES (
    'Pledge Alert',
    500000,
    ARRAY['PLEDGE'],
    true,
    95
);
```

### Example: Watchlist Companies

```sql
-- Lower threshold for specific companies
INSERT INTO alert_configurations (
    alert_name, min_shares,
    symbols, is_active, priority
) VALUES (
    'My Watchlist',
    10000,
    ARRAY['532890', '521248', '543425'],  -- Replace with your scrip codes
    true,
    75
);
```

---

## Testing Your Thresholds

### Step 1: Set Test Thresholds

Lower thresholds temporarily to see more alerts:

```env
MIN_SHARES_THRESHOLD=10000
MIN_VALUE_THRESHOLD=1000000
```

### Step 2: Run Script

```bash
python main.py
```

### Step 3: Review Alerts

Check email/Telegram to see how many alerts you get.

### Step 4: Adjust

**Too many alerts?** Increase thresholds:
```env
MIN_SHARES_THRESHOLD=150000
MIN_VALUE_THRESHOLD=15000000
```

**Too few alerts?** Decrease thresholds:
```env
MIN_SHARES_THRESHOLD=50000
MIN_VALUE_THRESHOLD=5000000
```

### Step 5: Finalize

Once satisfied, keep those values.

---

## Disabling Alerts Temporarily

### Method 1: Set Very High Thresholds

```env
MIN_SHARES_THRESHOLD=10000000      # 1 crore shares (unrealistic)
MIN_VALUE_THRESHOLD=1000000000     # ₹100 crores (very rare)
```

### Method 2: Disable in Database

```sql
UPDATE alert_configurations
SET is_active = false
WHERE alert_name = 'High Value Transactions';
```

To re-enable:

```sql
UPDATE alert_configurations
SET is_active = true
WHERE alert_name = 'High Value Transactions';
```

---

## Understanding Alert Counts

### By Current Threshold (1L shares / ₹1Cr)

Based on typical BSE data:

- **Total daily transactions:** 30-50
- **Alerts generated:** 5-10 (10-20%)
- **Email size:** 1-2 pages
- **Telegram length:** 10-20 lines per alert

### By Lower Threshold (50K shares / ₹50L)

- **Total daily transactions:** 30-50
- **Alerts generated:** 15-25 (30-50%)
- **Email size:** 3-5 pages
- **Telegram length:** May hit character limit

### By Higher Threshold (5L shares / ₹5Cr)

- **Total daily transactions:** 30-50
- **Alerts generated:** 1-3 (2-5%)
- **Email size:** <1 page
- **Telegram length:** 3-6 lines per alert

---

## Monitoring Threshold Effectiveness

### Weekly Review Query

```sql
SELECT 
    acquisition_disposal,
    COUNT(*) as total_transactions,
    COUNT(CASE WHEN acquired_shares >= 100000 THEN 1 END) as above_threshold,
    AVG(acquired_shares) as avg_shares,
    MAX(acquired_shares) as max_shares
FROM insider_trading_data
WHERE intimation_date >= CURRENT_DATE - 7
GROUP BY acquisition_disposal;
```

### Monthly Alert Summary

```sql
SELECT 
    DATE(intimation_date) as date,
    COUNT(CASE WHEN acquired_shares >= 100000 THEN 1 END) as potential_alerts,
    COUNT(*) as total_transactions
FROM insider_trading_data
WHERE intimation_date >= CURRENT_DATE - 30
GROUP BY DATE(intimation_date)
ORDER BY date DESC;
```

---

## Common Scenarios

### Scenario 1: Too Many Alerts

**Problem:** Getting 50+ alerts per day

**Solution:**
```env
# Increase both thresholds
MIN_SHARES_THRESHOLD=200000
MIN_VALUE_THRESHOLD=20000000
```

Or disable lower priority rules in database:
```sql
UPDATE alert_configurations
SET is_active = false
WHERE priority < 80;
```

---

### Scenario 2: Missing Important Alerts

**Problem:** Missed a significant transaction

**Check what you missed:**
```sql
SELECT company_name, person_name, acquired_shares, securities_value
FROM insider_trading_data
WHERE intimation_date >= CURRENT_DATE - 7
  AND acquired_shares < 100000
ORDER BY acquired_shares DESC
LIMIT 20;
```

**Solution:** Lower thresholds:
```env
MIN_SHARES_THRESHOLD=50000
MIN_VALUE_THRESHOLD=5000000
```

---

### Scenario 3: Only Want Promoter Trades

**Solution:** Add specific rule in database:

```sql
INSERT INTO alert_configurations (
    alert_name, min_shares,
    person_categories, is_active, priority
) VALUES (
    'Promoter Only',
    25000,
    ARRAY['Promoter', 'Promoter Group'],
    true,
    100
);

-- Disable default rule
UPDATE alert_configurations
SET is_active = false
WHERE alert_name = 'High Value Transactions';
```

---

### Scenario 4: Weekend Batch

**Want all transactions, not just alerts**

**Temporary change for weekend review:**
```env
MIN_SHARES_THRESHOLD=1
MIN_VALUE_THRESHOLD=1
```

Run script, review email with ALL transactions.

**Then restore:**
```env
MIN_SHARES_THRESHOLD=100000
MIN_VALUE_THRESHOLD=10000000
```

---

## Best Practices

### 1. Start Conservative

Begin with high thresholds, lower gradually:
```
Week 1: 500K shares / ₹5Cr
Week 2: 200K shares / ₹2Cr
Week 3: 100K shares / ₹1Cr (settle here)
```

### 2. Review Monthly

Check if thresholds are still appropriate:
- Market conditions change
- Company sizes in your watchlist vary
- Your investment strategy evolves

### 3. Separate Rules for Different Purposes

Don't use one rule for everything:
- One for promoter activity
- One for large transactions
- One for specific companies

### 4. Test Before Committing

Always test threshold changes:
```bash
# Test run
python main.py

# Check alerts
# Adjust if needed
# Test again
```

### 5. Document Your Changes

Keep a log of threshold changes:
```
2025-10-06: Set to 100K shares / ₹1Cr (initial)
2025-10-15: Lowered to 50K shares / ₹50L (too quiet)
2025-10-20: Raised to 100K shares / ₹1Cr (too noisy)
```

---

## Emergency Reset

If you lose track of your configurations:

### Reset to Default

**In .env:**
```env
MIN_SHARES_THRESHOLD=100000
MIN_VALUE_THRESHOLD=10000000
```

**In Database:**
```sql
-- Delete all custom rules
DELETE FROM alert_configurations
WHERE id > 1;

-- Reset default rule
UPDATE alert_configurations
SET min_shares = 100000,
    min_value = 10000000,
    is_active = true
WHERE id = 1;
```

---

## Quick Reference

### Environment File Location
```
C:\Users\DELL\Desktop\insider-trading-tracker\.env
```

### Edit Command
```bash
notepad .env
```

### Restart Script
```bash
python main.py
```

### View Current Rules (Database)
```sql
SELECT alert_name, min_shares, min_value, is_active, priority
FROM alert_configurations
ORDER BY priority DESC;
```

---

## Support

For threshold-related questions:
- Check current settings: `cat .env` or `type .env`
- View database rules: Supabase → alert_configurations table
- Test safely: Use high thresholds first, lower gradually
- Email: king.gerald2007@gmail.com

---

**Remember:** Start high, adjust down. It's easier to lower thresholds than deal with email overload!