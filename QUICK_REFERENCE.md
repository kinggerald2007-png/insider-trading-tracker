# Insider Trading Tracker - Quick Reference

## Common Commands

### Run Script
```bash
python main.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Check Logs
```bash
# Windows
type insider_trading.log

# Mac/Linux
cat insider_trading.log
tail -50 insider_trading.log
```

### Update Configuration
```bash
# Edit .env file
notepad .env           # Windows
nano .env              # Mac/Linux
```

---

## Configuration Quick Edit

### Change Alert Thresholds

Edit `.env`:
```env
# More alerts (lower thresholds)
MIN_SHARES_THRESHOLD=50000
MIN_VALUE_THRESHOLD=5000000

# Fewer alerts (higher thresholds)
MIN_SHARES_THRESHOLD=500000
MIN_VALUE_THRESHOLD=50000000
```

### Add Email Recipients

Edit `.env`:
```env
EMAIL_TO=email1@gmail.com,email2@gmail.com,email3@gmail.com
```

### Update Telegram

Edit `.env`:
```env
TELEGRAM_CHAT_ID=your_new_chat_id
```

---

## Database Quick Queries

### View Today's Alerts
```sql
SELECT company_name, person_name, acquired_shares, acquisition_disposal
FROM insider_trading_data
WHERE fetch_date = CURRENT_DATE
  AND acquired_shares >= 100000
ORDER BY acquired_shares DESC;
```

### Top 10 Largest Transactions
```sql
SELECT company_name, person_name, acquired_shares, intimation_date
FROM insider_trading_data
ORDER BY ABS(acquired_shares) DESC
LIMIT 10;
```

### Promoter Activity This Month
```sql
SELECT company_name, COUNT(*) as transactions, SUM(acquired_shares) as total_shares
FROM insider_trading_data
WHERE person_category ILIKE '%promoter%'
  AND intimation_date >= CURRENT_DATE - 30
GROUP BY company_name
ORDER BY total_shares DESC;
```

---

## Troubleshooting Quick Fixes

### No Data Fetched
```bash
# Check BSE website manually
https://www.bseindia.com/corporates/Insider_Trading_new.aspx?expandable=2

# Run after 6 PM IST
# Wait 30 minutes and retry
```

### Email Not Sending
```env
# Regenerate Gmail App Password
# Update in .env
EMAIL_PASSWORD=new_16_char_password
```

### No Alerts
```env
# Lower thresholds temporarily
MIN_SHARES_THRESHOLD=10000
MIN_VALUE_THRESHOLD=1000000
```

### Database Error
```sql
-- Drop and recreate tables
DROP TABLE IF EXISTS insider_trading_data CASCADE;
DROP TABLE IF EXISTS alert_configurations CASCADE;
-- Then run full schema again
```

---

## File Locations

### Configuration
- `.env` - All settings

### Logs
- `insider_trading.log` - Execution logs

### Database
- Supabase: https://tyibyuwusjpogfknameh.supabase.co

### Code
- `main.py` - Main script
- `requirements.txt` - Dependencies

---

## Important URLs

### BSE Data Source
https://www.bseindia.com/corporates/Insider_Trading_new.aspx?expandable=2

### Supabase Dashboard
https://tyibyuwusjpogfknameh.supabase.co

### Gmail App Passwords
https://myaccount.google.com/apppasswords

### Telegram BotFather
https://t.me/BotFather

---

## Email Format

**Subject:** 🚨 INSIDER TRADING ALERT - X Significant Transactions

**Contains:**
- Summary (Total, Acquisitions, Disposals)
- Alert table (Company, Insider, Type, Shares, Mode, Date)

---

## Telegram Format

```
📊 Insider Trading Report (BSE)
DD Month YYYY

Total: X transactions
🟢 Acquisitions: X
🔴 Disposals: X

🚨 X SIGNIFICANT ALERTS

[List of alerts]
```

---

## Default Thresholds

- **Shares:** 1,00,000 (1 lakh)
- **Value:** ₹1,00,00,000 (1 crore)

---

## Automation Schedule

- **Runs:** Daily at 10:00 AM IST
- **Method:** Windows Task Scheduler / Cron / GitHub Actions

---

## Support Contacts

- **Email:** king.gerald2007@gmail.com
- **Logs:** Check `insider_trading.log`
- **Documentation:** README.md and SETUP_GUIDE.md

---

## Emergency Recovery

### Complete Reset

1. **Drop all tables:**
```sql
DROP TABLE IF EXISTS insider_trading_data CASCADE;
DROP TABLE IF EXISTS alert_configurations CASCADE;
```

2. **Recreate tables:**
Run `supabase_schema.sql`

3. **Test run:**
```bash
python main.py
```

### Reinstall Dependencies

```bash
pip uninstall -y -r requirements.txt
pip install -r requirements.txt
```

### Fresh Start

```bash
# Delete everything except source files
rm insider_trading.log
rm *.csv

# Reinstall
pip install -r requirements.txt

# Test
python main.py
```

---

## Version Info

- **Version:** 1.0
- **Last Updated:** October 2025
- **Python:** 3.8+
- **Data Source:** BSE India
- **Database:** Supabase
- **Cost:** ₹0/month (Free tiers)

---

**Quick Tip:** Keep this file bookmarked for instant reference!