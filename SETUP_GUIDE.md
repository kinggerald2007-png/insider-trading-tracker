# Insider Trading Tracker - Complete Setup Guide

This guide will walk you through setting up the BSE Insider Trading Tracker from absolute scratch, step by step.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Initial Setup](#initial-setup)
3. [File Creation](#file-creation)
4. [Database Setup](#database-setup)
5. [Configuration](#configuration)
6. [Testing](#testing)
7. [Automation Setup](#automation-setup)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Software Needed

- **Python 3.8 or higher**
  - Download from: https://www.python.org/downloads/
  - During Windows installation: CHECK "Add Python to PATH"
  
- **Text Editor**
  - VS Code (recommended): https://code.visualstudio.com/
  - Or Notepad++: https://notepad-plus-plus.org/
  
- **Internet Connection**
  - Required for fetching BSE data and sending alerts

### Accounts Needed

- **Gmail Account** - For sending email alerts (already configured)
- **Supabase Account** - Database (already configured)
- **Telegram Account** - For instant notifications (optional but recommended)

---

## Initial Setup

### Step 1: Check Python Installation

Open Command Prompt (Windows) or Terminal (Mac/Linux):

```bash
python --version
```

You should see: `Python 3.x.x`

If not:
1. Download Python from python.org
2. Install with "Add to PATH" checked
3. Restart computer
4. Try again

### Step 2: Create Project Folder

**Windows:**
```bash
cd C:\Users\DELL\Desktop
mkdir insider-trading-tracker
cd insider-trading-tracker
```

**Mac/Linux:**
```bash
cd ~/Desktop
mkdir insider-trading-tracker
cd insider-trading-tracker
```

### Step 3: Open Folder in Text Editor

**VS Code:**
1. Open VS Code
2. File → Open Folder
3. Select `insider-trading-tracker` folder

**Notepad++:**
1. Open Notepad++
2. Create files one by one (shown below)

---

## File Creation

Create these 5 files in your project folder:

### File 1: requirements.txt

Create a new file named `requirements.txt` and paste:

```
requests==2.31.0
pandas==2.1.4
supabase==2.3.0
yagmail==0.15.293
python-dotenv==1.0.0
beautifulsoup4==4.12.2
lxml==4.9.3
```

Save the file.

### File 2: .env

Create a new file named `.env` (with dot at start) and paste:

```env
# Supabase Configuration (Already Set Up)
SUPABASE_URL=https://tyibyuwusjpogfknameh.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5aWJ5dXd1c2pwb2dma25hbWVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1NDgxMDMsImV4cCI6MjA3NTEyNDEwM30.xS8SYGmUYKIG41IfnpwDkrkkPeDttADY6qSf3MRPvx8

# Email Configuration (Already Set Up)
EMAIL_USER=quantkingdaily@gmail.com
EMAIL_PASSWORD=tsxa oiiy mztw artq

# CUSTOMIZE THIS: Your Email Recipients (comma-separated, no spaces)
EMAIL_TO=king.gerald2007@gmail.com,mahesh22an@gmail.com

# Telegram Configuration
TELEGRAM_BOT_TOKEN=8272854685:AAEYFdXp0TRXpiMLaE1-7AYoyTNjE_vuvOI
TELEGRAM_CHAT_ID=1524238363

# Alert Thresholds
# MIN_SHARES_THRESHOLD: Alert if transaction has >= this many shares
MIN_SHARES_THRESHOLD=100000

# MIN_VALUE_THRESHOLD: Alert if transaction value >= this amount (in INR)
MIN_VALUE_THRESHOLD=10000000

# Logging Level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

**IMPORTANT:** Update `EMAIL_TO` with your email addresses!

Save the file.

### File 3: .gitignore

Create a new file named `.gitignore` and paste:

```
# Environment variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/

# Logs
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# CSV exports (optional)
*.csv
```

Save the file.

### File 4: main.py

Create a new file named `main.py` and paste the **entire Python code** from the artifact provided earlier.

This is your main automation script. Save the file.

### File 5: supabase_schema.sql

Create a new file named `supabase_schema.sql` and paste:

```sql
-- Supabase Database Schema for BSE Insider Trading Tracker

-- ============================================================================
-- INSIDER TRADING DATA TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS insider_trading_data (
    id BIGSERIAL PRIMARY KEY,
    fetch_date DATE NOT NULL,
    source TEXT DEFAULT 'BSE',
    
    -- Company Information
    scrip_code TEXT,
    company_name TEXT,
    symbol TEXT,
    
    -- Person Information
    person_name TEXT,
    person_category TEXT,
    
    -- Transaction Details
    acquisition_disposal TEXT,
    security_type TEXT,
    acquisition_mode TEXT,
    
    -- Share Details
    before_shares NUMERIC,
    acquired_shares NUMERIC,
    after_shares NUMERIC,
    
    -- Value Information
    securities_value NUMERIC,
    
    -- Dates
    acquisition_period_from DATE,
    acquisition_period_to DATE,
    intimation_date DATE,
    
    -- Derivatives Trading
    trading_derivative_type TEXT,
    trading_derivative_value NUMERIC,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_insider_fetch_date ON insider_trading_data(fetch_date DESC);
CREATE INDEX IF NOT EXISTS idx_insider_company ON insider_trading_data(company_name);
CREATE INDEX IF NOT EXISTS idx_insider_person ON insider_trading_data(person_name);
CREATE INDEX IF NOT EXISTS idx_insider_category ON insider_trading_data(person_category);
CREATE INDEX IF NOT EXISTS idx_insider_transaction ON insider_trading_data(acquisition_disposal);
CREATE INDEX IF NOT EXISTS idx_insider_intimation_date ON insider_trading_data(intimation_date DESC);

-- ============================================================================
-- ALERT CONFIGURATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS alert_configurations (
    id BIGSERIAL PRIMARY KEY,
    alert_name TEXT NOT NULL,
    
    -- Threshold Settings
    min_shares INTEGER DEFAULT 100000,
    min_value NUMERIC DEFAULT 10000000,
    
    -- Filter Settings
    person_categories TEXT[],
    symbols TEXT[],
    transaction_types TEXT[],
    
    -- Alert Settings
    is_active BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default alert configuration
INSERT INTO alert_configurations (alert_name, min_shares, min_value, is_active, priority)
VALUES ('High Value Transactions', 100000, 10000000, true, 10)
ON CONFLICT DO NOTHING;
```

Save the file.

---

## Database Setup

### Step 1: Open Supabase

1. Open browser
2. Go to: https://tyibyuwusjpogfknameh.supabase.co
3. Sign in with your credentials

### Step 2: Run SQL Schema

1. Click **"SQL Editor"** in left sidebar
2. Click **"+ New Query"** button
3. Open `supabase_schema.sql` file
4. Copy ALL the contents
5. Paste into the query editor
6. Click **"Run"** (or press Ctrl+Enter)
7. Wait for: **"Success. No rows returned"**

### Step 3: Verify Tables Created

1. Click **"Table Editor"** in left sidebar
2. You should see 2 tables:
   - `insider_trading_data`
   - `alert_configurations`
3. Click on `alert_configurations`
4. Verify there's 1 row with default settings

**If tables don't appear:** Refresh the page and check again.

---

## Configuration

### Step 1: Install Python Dependencies

Open Command Prompt/Terminal in your project folder:

```bash
cd C:\Users\DELL\Desktop\insider-trading-tracker
```

Install packages:

```bash
pip install -r requirements.txt
```

Wait 2-3 minutes. You should see:
```
Successfully installed requests-2.31.0 pandas-2.1.4 ...
```

### Step 2: Verify Email Recipients

Open `.env` file and check `EMAIL_TO` line:

```env
# Single recipient
EMAIL_TO=your@email.com

# Multiple recipients
EMAIL_TO=email1@gmail.com,email2@gmail.com,email3@gmail.com
```

**No spaces between emails!**

### Step 3: Adjust Alert Thresholds (Optional)

Default settings:
- `MIN_SHARES_THRESHOLD=100000` (1 lakh shares)
- `MIN_VALUE_THRESHOLD=10000000` (₹1 crore)

**To get more alerts, lower the thresholds:**

```env
MIN_SHARES_THRESHOLD=50000      # 50 thousand shares
MIN_VALUE_THRESHOLD=5000000     # ₹50 lakhs
```

**To get fewer alerts, raise them:**

```env
MIN_SHARES_THRESHOLD=500000     # 5 lakh shares
MIN_VALUE_THRESHOLD=50000000    # ₹5 crores
```

---

## Testing

### Test Run

In Command Prompt/Terminal:

```bash
python main.py
```

### Expected Output

You should see:

```
2025-10-06 - INFO - BSE fetcher initialized
2025-10-06 - INFO - Supabase client initialized successfully
2025-10-06 - INFO - Email client initialized successfully
2025-10-06 - INFO - Telegram notifier initialized
2025-10-06 - INFO - ======================================================================
2025-10-06 - INFO - STARTING INSIDER TRADING DAILY AUTOMATION (BSE)
2025-10-06 - INFO - ======================================================================
2025-10-06 - INFO - [STEP 1/6] Loading alert configurations...
2025-10-06 - INFO - Loaded 1 alert configurations
2025-10-06 - INFO - [STEP 2/6] Fetching insider trading data from BSE...
2025-10-06 - INFO - Fetching BSE insider trading data...
2025-10-06 - INFO - Table 1: shape=(39, 16), columns=16, size=624
2025-10-06 - INFO - Fetched 39 insider trading records from BSE
2025-10-06 - INFO - [STEP 3/6] Processing alerts...
2025-10-06 - INFO - Found 8 alerts matching criteria
2025-10-06 - INFO - [STEP 4/6] Storing data in Supabase...
2025-10-06 - INFO - Successfully stored 39/39 records
2025-10-06 - INFO - [STEP 5/6] Generating summary...
2025-10-06 - INFO - [STEP 6/6] Sending notifications...
2025-10-06 - INFO - Email report sent successfully
2025-10-06 - INFO - Telegram notification sent
2025-10-06 - INFO - AUTOMATION COMPLETED SUCCESSFULLY!
```

### Check Results

1. **Check Email**
   - Subject: "🚨 INSIDER TRADING ALERT - X Significant Transactions"
   - Should have HTML table with alerts

2. **Check Telegram**
   - Should receive message with transaction summary
   - Lists all significant alerts

3. **Check Supabase**
   - Go to Table Editor → insider_trading_data
   - Should see 39 rows of data

---

## Automation Setup

### Option 1: Windows Task Scheduler (Recommended for Windows)

1. **Open Task Scheduler**
   - Press Windows key
   - Type "Task Scheduler"
   - Open it

2. **Create Basic Task**
   - Click "Create Basic Task" (right sidebar)
   - Name: `Insider Trading Tracker`
   - Description: `Daily BSE insider trading alerts`
   - Click "Next"

3. **Set Trigger**
   - Select "Daily"
   - Start date: Today
   - Start time: `10:00 AM`
   - Recur every: `1 days`
   - Click "Next"

4. **Set Action**
   - Select "Start a program"
   - Program/script: `python.exe`
   - Add arguments: `main.py`
   - Start in: `C:\Users\DELL\Desktop\insider-trading-tracker`
   - Click "Next"

5. **Finish**
   - Check "Open Properties dialog"
   - Click "Finish"

6. **Advanced Settings**
   - In Properties dialog:
   - Check "Run whether user is logged on or not"
   - Check "Run with highest privileges"
   - Click "OK"

### Option 2: Mac/Linux Cron Job

1. **Open Terminal**

2. **Edit Crontab**
```bash
crontab -e
```

3. **Add Line**
```bash
0 10 * * * cd /Users/yourname/Desktop/insider-trading-tracker && /usr/bin/python3 main.py >> /Users/yourname/Desktop/insider-trading-tracker/cron.log 2>&1
```

4. **Save and Exit**
   - Press `Ctrl+O` to save
   - Press `Ctrl+X` to exit

### Option 3: GitHub Actions (Cloud Automation)

1. **Create GitHub Repository**
   - Go to github.com
   - Create new repository: `insider-trading-tracker`
   - Keep it private

2. **Upload Files**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/insider-trading-tracker.git
   git push -u origin main
   ```

3. **Add GitHub Secrets**
   - Go to: Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Add each secret:
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
     - `EMAIL_USER`
     - `EMAIL_PASSWORD`
     - `EMAIL_TO`
     - `TELEGRAM_BOT_TOKEN`
     - `TELEGRAM_CHAT_ID`
     - `MIN_SHARES_THRESHOLD`
     - `MIN_VALUE_THRESHOLD`

4. **Create Workflow File**
   
   Create `.github/workflows/daily_insider.yml`:

   ```yaml
   name: Daily Insider Trading Automation

   on:
     schedule:
       - cron: '30 4 * * *'  # 10:00 AM IST daily
     workflow_dispatch:

   jobs:
     run-tracker:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.10'
         
         - name: Install dependencies
           run: pip install -r requirements.txt
         
         - name: Run insider trading tracker
           env:
             SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
             SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
             EMAIL_USER: ${{ secrets.EMAIL_USER }}
             EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
             EMAIL_TO: ${{ secrets.EMAIL_TO }}
             TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
             TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
             MIN_SHARES_THRESHOLD: ${{ secrets.MIN_SHARES_THRESHOLD }}
             MIN_VALUE_THRESHOLD: ${{ secrets.MIN_VALUE_THRESHOLD }}
           run: python main.py
         
         - name: Upload logs
           if: always()
           uses: actions/upload-artifact@v3
           with:
             name: logs
             path: insider_trading.log
   ```

5. **Test Workflow**
   - Go to Actions tab
   - Click "Daily Insider Trading Automation"
   - Click "Run workflow"
   - Check your email/Telegram

---

## Troubleshooting

### Issue 1: "python: command not found"

**Solution:**
```bash
# Try python3 instead
python3 --version
python3 main.py

# Or add alias (Mac/Linux)
echo "alias python=python3" >> ~/.bashrc
source ~/.bashrc
```

### Issue 2: "No module named 'requests'"

**Solution:**
```bash
# Install requirements again
pip install -r requirements.txt

# Or use pip3
pip3 install -r requirements.txt
```

### Issue 3: "ModuleNotFoundError: No module named 'pandas'"

**Solution:**
```bash
# Install pandas explicitly
pip install pandas==2.1.4

# Then install all requirements
pip install -r requirements.txt
```

### Issue 4: "Supabase connection failed"

**Causes:**
1. Wrong SUPABASE_URL or SUPABASE_KEY
2. Tables not created
3. Internet connection issue

**Solution:**
1. Verify `.env` file has correct values
2. Re-run SQL schema in Supabase
3. Check internet connection
4. Try running script again

### Issue 5: "Email authentication failed"

**Causes:**
1. Wrong email password
2. 2FA not enabled
3. App password not generated

**Solution:**
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Create App Password:
   - Search "App passwords"
   - Select "Mail" and "Other"
   - Copy 16-character password
4. Update EMAIL_PASSWORD in `.env`

### Issue 6: "No data fetched from BSE"

**Causes:**
1. BSE website down
2. Internet connectivity
3. BSE changed structure

**Solution:**
1. Visit https://www.bseindia.com/corporates/Insider_Trading_new.aspx?expandable=2
2. Check if data loads manually
3. Run script during market hours or after 6 PM IST
4. Wait 30 minutes and try again

### Issue 7: "0 alerts generated"

**Causes:**
1. Thresholds too high
2. No large transactions today
3. Data parsing issue

**Solution:**
1. Lower thresholds in `.env`:
   ```env
   MIN_SHARES_THRESHOLD=10000
   MIN_VALUE_THRESHOLD=1000000
   ```
2. Check Supabase → insider_trading_data table
3. Verify acquired_shares column has values
4. Run script again

### Issue 8: "Telegram notification failed"

**Causes:**
1. Wrong bot token
2. Wrong chat ID
3. Bot blocked

**Solution:**
1. Verify TELEGRAM_BOT_TOKEN in `.env`
2. Verify TELEGRAM_CHAT_ID in `.env`
3. Open Telegram and send `/start` to your bot
4. Make sure bot is not blocked
5. Test with simple message first

### Issue 9: "Database insert error"

**Error:** `Could not find column 'xyz'`

**Solution:**
1. Drop and recreate tables in Supabase:
   ```sql
   DROP TABLE IF EXISTS insider_trading_data CASCADE;
   DROP TABLE IF EXISTS alert_configurations CASCADE;
   ```
2. Re-run entire schema from `supabase_schema.sql`
3. Run script again

### Issue 10: "Task Scheduler not running"

**Solution:**
1. Open Task Scheduler
2. Find your task
3. Right-click → Run
4. Check "Last Run Result" - should be 0x0 (success)
5. Check "History" tab for details
6. Verify paths are absolute, not relative

---

## Best Practices

### Daily Routine

1. **Morning (10 AM)**: Script runs automatically
2. **Check Alerts**: Review email/Telegram by 11 AM
3. **Investigate**: Research companies with large transactions
4. **Log Review**: Check `insider_trading.log` weekly

### Weekly Tasks

1. Verify script ran successfully all 7 days
2. Review Supabase storage usage
3. Check for any error patterns in logs
4. Update thresholds if needed

### Monthly Tasks

1. Review alert thresholds effectiveness
2. Analyze insider trading patterns
3. Check Python package updates:
   ```bash
   pip list --outdated
   ```
4. Backup Supabase data
5. Clean old log files

### Security Checklist

- [ ] `.env` file is NOT in git
- [ ] `.gitignore` includes `.env`
- [ ] GitHub repository is private (if using)
- [ ] Secrets are stored in GitHub Secrets
- [ ] 2FA enabled on Gmail
- [ ] App password used (not main password)
- [ ] Supabase project has RLS enabled (optional)

---

## Advanced Usage

### Custom Alert Rules

Add in Supabase SQL Editor:

```sql
-- Only promoter acquisitions above 50k shares
INSERT INTO alert_configurations (
    alert_name, min_shares, 
    person_categories, transaction_types,
    is_active, priority
) VALUES (
    'Promoter Confidence Signal',
    50000,
    ARRAY['Promoter', 'Promoter Group'],
    ARRAY['ACQUISITION'],
    true,
    100
);

-- Large pledges warning
INSERT INTO alert_configurations (
    alert_name, min_shares,
    transaction_types, is_active, priority
) VALUES (
    'Pledge Warning',
    500000,
    ARRAY['PLEDGE'],
    true,
    90
);

-- Specific companies watchlist
INSERT INTO alert_configurations (
    alert_name, min_shares,
    symbols, is_active, priority
) VALUES (
    'My Watchlist',
    10000,
    ARRAY['532890', '521248', '543425'],
    true,
    80
);
```

### Export Data to Excel

```python
import pandas as pd
from supabase import create_client

client = create_client(SUPABASE_URL, SUPABASE_KEY)
response = client.table('insider_trading_data').select('*').execute()
df = pd.DataFrame(response.data)
df.to_excel('insider_trading_export.xlsx', index=False)
print(f"Exported {len(df)} records to Excel")
```

### Analyze Patterns

```python
# Find companies with heavy insider selling
import pandas as pd
from supabase import create_client

client = create_client(SUPABASE_URL, SUPABASE_KEY)
response = client.table('insider_trading_data')\
    .select('*')\
    .eq('acquisition_disposal', 'DISPOSAL')\
    .execute()

df = pd.DataFrame(response.data)
summary = df.groupby('company_name').agg({
    'acquired_shares': 'sum',
    'person_name': 'count'
}).sort_values('acquired_shares')

print(summary.head(10))
```

---

## Performance Optimization

### Speed Up Execution

1. **Reduce data fetch range:**
   ```python
   # In main.py, change:
   df = self.fetcher.fetch_insider_trading(days_back=7)  # Instead of 30
   ```

2. **Limit alert checks:**
   ```python
   # Process only recent data
   df = df[df['intimation_date'] >= datetime.now().date() - timedelta(days=7)]
   ```

3. **Batch database inserts:**
   Already optimized to 100 records per batch

### Reduce Email Size

1. **Limit alerts in email:**
   ```python
   # Show only top 20 alerts
   for alert in alerts[:20]:
   ```

2. **Remove summary box** (optional)

### Save Bandwidth

1. Run only on weekdays:
   ```yaml
   # In GitHub Actions
   schedule:
     - cron: '30 4 * * 1-5'  # Monday to Friday only
   ```

---

## FAQ

**Q: How often should I run this?**
A: Daily at 10 AM IST is recommended. BSE updates data after market closes.

**Q: Can I run it multiple times per day?**
A: Yes, but BSE data updates once daily. Multiple runs will fetch same data.

**Q: What if I miss a day?**
A: No problem. BSE shows historical data. Just run script and it will fetch latest.

**Q: Can I track NSE data too?**
A: Currently BSE only. NSE has strict anti-scraping. Can be added if needed.

**Q: How long is data stored?**
A: Forever in Supabase (free tier: 500MB). Delete old data if needed.

**Q: Can I add more email recipients?**
A: Yes! Edit EMAIL_TO in `.env` with comma-separated emails.

**Q: Telegram not working?**
A: Make sure you sent `/start` to your bot first.

**Q: How to change alert thresholds?**
A: Edit MIN_SHARES_THRESHOLD and MIN_VALUE_THRESHOLD in `.env`

**Q: Can I filter by specific companies?**
A: Yes! Add custom rule in alert_configurations table with symbols array.

**Q: Is this legal?**
A: Yes! BSE publishes insider trading data publicly. This just automates monitoring.

---

## Getting Help

**Check Logs First:**
```bash
# View last 50 lines
tail -50 insider_trading.log

# View errors only
grep ERROR insider_trading.log
```

**Test Components Individually:**

```bash
# Test BSE connection
python -c "import requests; r=requests.get('https://www.bseindia.com'); print(r.status_code)"

# Test Supabase connection
python -c "from supabase import create_client; client=create_client('URL', 'KEY'); print('Connected')"

# Test email
python -c "import yagmail; yag=yagmail.SMTP('EMAIL', 'PASS'); yag.send('TO', 'Test', 'Body')"
```

**Contact:**
- Email: king.gerald2007@gmail.com
- Check README.md for more info

---

## Appendix: File Checklist

Before running, verify you have:

```
insider-trading-tracker/
├── ✓ main.py (Python script - 1000+ lines)
├── ✓ requirements.txt (7 lines)
├── ✓ .env (Configuration with YOUR email)
├── ✓ .gitignore (Git ignore rules)
├── ✓ supabase_schema.sql (Database schema)
├── ✓ README.md (Documentation)
└── ✓ SETUP_GUIDE.md (This file)
```

**In Supabase:**
- ✓ insider_trading_data table (with indexes)
- ✓ alert_configurations table (with 1 default row)

**Accounts Verified:**
- ✓ Gmail with App Password
- ✓ Supabase project active
- ✓ Telegram bot created (optional)

---

## Success Checklist

After setup, you should have:

- [ ] Python installed and working
- [ ] All 5 files created in project folder
- [ ] Supabase tables created successfully
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with YOUR email
- [ ] Test run completed successfully
- [ ] Email received with alerts
- [ ] Telegram notification received (if enabled)
- [ ] Data visible in Supabase table
- [ ] Automation scheduled (Task Scheduler or Cron)

**If all checked, you're done! The system will run automatically daily.**

---

**Last Updated:** October 2025  
**Version:** 1.0  
**Status:** Production Ready