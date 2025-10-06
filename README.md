# BSE Insider Trading Tracker

Automated Python system that fetches daily insider trading data from BSE (Bombay Stock Exchange), stores it in Supabase, and sends email + Telegram alerts for significant transactions.

## Features

- Automated BSE data fetching from official website
- Configurable alert thresholds (shares and value)
- Email reports with HTML formatting
- Telegram instant notifications
- Supabase database storage with full history
- Filters for large transactions (default: 1 lakh shares or ₹1 crore)
- Handles promoter, director, and employee transactions
- Tracks acquisitions, disposals, and pledges

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Gmail account with App Password enabled
- Supabase account (already configured)
- Telegram bot (optional)

### Installation (10 minutes)

1. **Clone or create project folder:**
```bash
mkdir insider-trading-tracker
cd insider-trading-tracker
```

2. **Create files:**
   - `main.py` - Main script
   - `requirements.txt` - Dependencies
   - `.env` - Configuration
   - `.gitignore` - Git ignore file

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure `.env` file:**
```env
# Supabase (Already configured)
SUPABASE_URL=https://tyibyuwusjpogfknameh.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5aWJ5dXd1c2pwb2dma25hbWVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1NDgxMDMsImV4cCI6MjA3NTEyNDEwM30.xS8SYGmUYKIG41IfnpwDkrkkPeDttADY6qSf3MRPvx8

# Email (Already configured)
EMAIL_USER=quantkingdaily@gmail.com
EMAIL_PASSWORD=tsxa oiiy mztw artq
EMAIL_TO=king.gerald2007@gmail.com,mahesh22an@gmail.com

# Telegram
TELEGRAM_BOT_TOKEN=8272854685:AAEYFdXp0TRXpiMLaE1-7AYoyTNjE_vuvOI
TELEGRAM_CHAT_ID=1524238363

# Alert Thresholds
MIN_SHARES_THRESHOLD=100000
MIN_VALUE_THRESHOLD=10000000

# Logging
LOG_LEVEL=INFO
```

5. **Set up Supabase database:**
   - Go to https://tyibyuwusjpogfknameh.supabase.co
   - Click SQL Editor
   - Run the schema from `supabase_schema.sql`

6. **Test run:**
```bash
python main.py
```

You should receive email and Telegram notifications within 2-3 minutes.

## Configuration

### Alert Thresholds

**MIN_SHARES_THRESHOLD:** Minimum shares to trigger alert
- Default: 100000 (1 lakh shares)
- Examples: 50000 (50k), 100000 (1L), 1000000 (10L)

**MIN_VALUE_THRESHOLD:** Minimum value in INR to trigger alert
- Default: 10000000 (₹1 crore)
- Examples: 5000000 (₹50L), 10000000 (₹1Cr), 50000000 (₹5Cr)

**Note:** Alerts trigger if EITHER threshold is met (OR logic)

### Email Recipients

Edit EMAIL_TO in `.env`:
```env
# Single recipient
EMAIL_TO=your@email.com

# Multiple recipients (comma-separated, no spaces)
EMAIL_TO=email1@gmail.com,email2@gmail.com,email3@gmail.com
```

### Telegram Setup

1. Create bot with @BotFather:
   - Send `/newbot` to @BotFather
   - Follow instructions
   - Copy bot token

2. Get your chat ID:
   - Send message to @userinfobot
   - Copy your chat ID

3. Update `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## Database Schema

### insider_trading_data Table

Stores all insider transactions:

```sql
- scrip_code: BSE security code
- company_name: Full company name
- person_name: Name of insider
- person_category: Promoter, Director, Employee, etc.
- security_type: Type of security (Equity Shares, etc.)
- acquisition_disposal: ACQUISITION, DISPOSAL, or PLEDGE
- acquired_shares: Number of shares (positive or negative)
- before_shares: Holdings before transaction
- after_shares: Holdings after transaction
- securities_value: Transaction value in INR
- acquisition_mode: Market Sale, Off Market, ESOP, etc.
- acquisition_period_from: Transaction start date
- acquisition_period_to: Transaction end date
- intimation_date: Date disclosed to exchange
- fetch_date: Date data was fetched
- source: BSE
```

### alert_configurations Table

Custom alert rules:

```sql
- alert_name: Descriptive name
- min_shares: Minimum shares threshold
- min_value: Minimum value threshold (INR)
- person_categories: Filter by insider type (array)
- symbols: Filter by specific companies (array)
- transaction_types: ACQUISITION, DISPOSAL, PLEDGE (array)
- is_active: Enable/disable rule
- priority: Display order in alerts
```

## Email Report Format

Subject: `🚨 INSIDER TRADING ALERT - X Significant Transactions - DD Month YYYY`

Content:
- Summary box with total transactions, acquisitions, disposals
- Alert table with:
  - Company name (with scrip code)
  - Insider name and category
  - Transaction type (color-coded)
  - Number of shares
  - Acquisition mode
  - Date

Example:

| Company | Insider | Type | Shares | Mode | Date |
|---------|---------|------|--------|------|------|
| **Take Solutions Ltd**<br>Code: 532890 | Eesypro Infotech Limited<br>Promoter Group | DISPOSAL | 72,48,766 | Off Market | 30/09/2025 |
| **Bajel Projects Ltd**<br>Code: 532779 | Nimisha Bajaj Family Trust<br>Trust | DISPOSAL | 2,06,575 | N/A | 05/10/2025 |

## Telegram Notification Format

```
📊 Insider Trading Report (BSE)
06 October 2025

Total: 29 transactions
🟢 Acquisitions: 10
🔴 Disposals: 12

🚨 8 SIGNIFICANT ALERTS

🔴 Take Solutions Ltd
   Eesypro Infotech Limited
   DISPOSAL: 7,248,766 shares
   Mode: Off Market

🔴 Bajel Projects Ltd
   Nimisha Bajaj Family Trust
   DISPOSAL: 206,575 shares
   Mode: N/A

Check email for detailed report
```

## Useful Database Queries

### Today's Large Transactions

```sql
SELECT 
    company_name,
    person_name,
    person_category,
    acquisition_disposal,
    acquired_shares,
    securities_value,
    acquisition_mode
FROM insider_trading_data
WHERE fetch_date = CURRENT_DATE
  AND acquired_shares >= 100000
ORDER BY acquired_shares DESC;
```

### Promoter Activity (Last 30 Days)

```sql
SELECT 
    company_name,
    person_name,
    COUNT(*) as transaction_count,
    SUM(acquired_shares) as total_shares,
    SUM(securities_value) as total_value
FROM insider_trading_data
WHERE person_category ILIKE '%promoter%'
  AND intimation_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY company_name, person_name
ORDER BY total_shares DESC;
```

### Companies with Heavy Selling

```sql
SELECT 
    company_name,
    COUNT(*) as disposal_count,
    SUM(ABS(acquired_shares)) as shares_sold
FROM insider_trading_data
WHERE acquisition_disposal = 'DISPOSAL'
  AND intimation_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY company_name
HAVING COUNT(*) >= 3
ORDER BY shares_sold DESC;
```

### Large Pledges (Warning Sign)

```sql
SELECT 
    company_name,
    person_name,
    person_category,
    acquired_shares,
    intimation_date
FROM insider_trading_data
WHERE acquisition_disposal = 'PLEDGE'
  AND acquired_shares >= 500000
ORDER BY intimation_date DESC;
```

## Scheduling Options

### Option 1: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Insider Trading Tracker"
4. Trigger: Daily at 10:00 AM
5. Action: Start a program
   - Program: `python.exe`
   - Arguments: `C:\path\to\main.py`
   - Start in: `C:\path\to\insider-trading-tracker`

### Option 2: Linux Cron

```bash
crontab -e
```

Add line:
```
0 10 * * * cd /path/to/insider-trading-tracker && /usr/bin/python3 main.py
```

### Option 3: GitHub Actions

Create `.github/workflows/daily_insider.yml`:

```yaml
name: Daily Insider Trading

on:
  schedule:
    - cron: '30 4 * * *'  # 10:00 AM IST
  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python main.py
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
```

## Troubleshooting

### No Data Fetched

**Problem:** Script reports 0 records

**Solutions:**
1. Check BSE website manually
2. BSE may be down temporarily
3. Run script after market hours (after 6 PM IST)
4. Check internet connection

### Email Not Sending

**Problem:** Gmail authentication fails

**Solutions:**
1. Verify 2FA is enabled on Gmail
2. Generate new App Password:
   - Google Account → Security → 2-Step Verification → App passwords
3. Use 16-character password (no spaces)
4. Update EMAIL_PASSWORD in `.env`

### No Alerts Generated

**Problem:** Email shows 0 alerts but data exists

**Solutions:**
1. Lower thresholds temporarily:
   ```env
   MIN_SHARES_THRESHOLD=10000
   MIN_VALUE_THRESHOLD=1000000
   ```
2. Check Supabase data manually
3. Verify alert_configurations table has active rules

### Database Insert Fails

**Problem:** Error inserting into Supabase

**Solutions:**
1. Verify SUPABASE_URL and SUPABASE_KEY
2. Check tables exist (run schema SQL)
3. Check Supabase project is active
4. Verify internet connection

### Telegram Not Working

**Problem:** No Telegram notifications

**Solutions:**
1. Verify bot token is correct
2. Verify chat ID is correct
3. Send `/start` to your bot first
4. Check bot is not blocked
5. Test with small message first

## File Structure

```
insider-trading-tracker/
├── main.py                          # Main automation script
├── requirements.txt                 # Python dependencies
├── .env                             # Configuration (DO NOT commit)
├── .gitignore                       # Git ignore rules
├── insider_trading.log              # Auto-generated logs
├── README.md                        # This file
├── SETUP_GUIDE.md                   # Step-by-step setup
└── supabase_schema.sql             # Database schema
```

## Security Best Practices

1. Never commit `.env` file to GitHub
2. Use GitHub Secrets for automation
3. Rotate passwords every 90 days
4. Enable 2FA on all accounts
5. Use Supabase RLS (Row Level Security) in production
6. Monitor access logs regularly
7. Limit email recipients to trusted users

## Advanced Configuration

### Multiple Alert Rules

Add custom rules in Supabase:

```sql
-- High priority promoter acquisitions
INSERT INTO alert_configurations (
    alert_name, min_shares, min_value,
    person_categories, transaction_types,
    is_active, priority
) VALUES (
    'Promoter Buying Alert',
    50000,
    5000000,
    ARRAY['Promoter', 'Promoter Group'],
    ARRAY['ACQUISITION'],
    true,
    100
);

-- Pledge warnings
INSERT INTO alert_configurations (
    alert_name, min_shares,
    transaction_types, is_active, priority
) VALUES (
    'Large Pledge Warning',
    500000,
    ARRAY['PLEDGE'],
    true,
    90
);
```

### Filter by Specific Companies

```sql
INSERT INTO alert_configurations (
    alert_name, min_shares,
    symbols, is_active, priority
) VALUES (
    'Watchlist Companies',
    10000,
    ARRAY['532890', '521248', '543425'],
    true,
    80
);
```

## Performance & Costs

- **Execution time:** 2-5 minutes per run
- **Data volume:** 30-50 transactions/day average
- **Memory usage:** <50MB RAM
- **Storage:** ~1MB per month in Supabase
- **Cost:** ₹0/month (free tiers)

### Free Tier Limits

- Supabase: 500MB database, unlimited API requests
- Gmail: 500 emails/day
- Telegram: Unlimited messages
- GitHub Actions: 2,000 minutes/month

## Investment Strategies

### Strategy 1: Follow Smart Money

Track when multiple insiders buy:

```sql
SELECT 
    company_name,
    COUNT(DISTINCT person_name) as buyers,
    SUM(acquired_shares) as total_shares
FROM insider_trading_data
WHERE acquisition_disposal = 'ACQUISITION'
  AND intimation_date >= CURRENT_DATE - 30
GROUP BY company_name
HAVING COUNT(DISTINCT person_name) >= 3
ORDER BY total_shares DESC;
```

### Strategy 2: Promoter Confidence Signal

Heavy promoter buying indicates confidence:
- Set alert for promoter acquisitions above 1 lakh shares
- Monitor if multiple promoters are buying
- Check if buying during market dip

### Strategy 3: Warning Signs

Watch for red flags:
- Multiple insiders selling
- Large pledges by promoters
- Continuous disposal pattern

## Maintenance

### Daily
- Check email/Telegram alerts
- Review significant transactions

### Weekly
- Verify script is running
- Check Supabase storage usage

### Monthly
- Review alert thresholds
- Analyze insider patterns
- Clean old logs if needed

### Quarterly
- Rotate passwords
- Update Python dependencies
- Review GitHub Actions usage

## Support

For issues or questions:
- Check logs: `insider_trading.log`
- Review troubleshooting section
- Email: king.gerald2007@gmail.com

## Disclaimer

This tool is for informational purposes only:
- Not financial advice
- Past insider trading doesn't guarantee future performance
- Always do your own research
- Consult financial advisor before investing
- We are not responsible for trading losses

## License

MIT License - Free for personal and commercial use

## Contributing

Contributions welcome:
1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## Version History

- **v1.0** (Oct 2025) - Initial release with BSE support
  - Email and Telegram alerts
  - Configurable thresholds
  - Supabase integration

---

**Built for Indian Stock Market Investors**

Track insider moves. Make informed decisions.