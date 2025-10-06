"""
BSE Insider Trading Daily Automation Script
WITH EMAIL ALERTS AND CONFIGURABLE THRESHOLDS
Repository: https://github.com/your-username/insider-trading-tracker
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import traceback

import pandas as pd
import requests
from supabase import create_client, Client
import yagmail
from io import StringIO

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration class"""
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://tyibyuwusjpogfknameh.supabase.co')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5aWJ5dXd1c2pwb2dma25hbWVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1NDgxMDMsImV4cCI6MjA3NTEyNDEwM30.xS8SYGmUYKIG41IfnpwDkrkkPeDttADY6qSf3MRPvx8')
    
    # Email Configuration
    EMAIL_USER = os.getenv('EMAIL_USER', 'quantkingdaily@gmail.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'tsxa oiiy mztw artq')
    EMAIL_TO = os.getenv('EMAIL_TO', 'king.gerald2007@gmail.com,mahesh22an@gmail.com').split(',')
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8272854685:AAEYFdXp0TRXpiMLaE1-7AYoyTNjE_vuvOI')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '1524238363')
    
    # Alert Thresholds (configurable)
    MIN_SHARES_THRESHOLD = int(os.getenv('MIN_SHARES_THRESHOLD', '100000'))  # 1 lakh shares
    MIN_VALUE_THRESHOLD = float(os.getenv('MIN_VALUE_THRESHOLD', '10000000'))  # 1 crore
    
    # Database Table Names
    TABLE_INSIDER_TRADING = "insider_trading_data"
    TABLE_ALERT_CONFIG = "alert_configurations"
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('insider_trading.log')
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()


# ============================================================================
# BSE INSIDER TRADING FETCHER
# ============================================================================

class BSEInsiderTradingFetcher:
    """Fetch insider trading data from BSE"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.bseindia.com"
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        logger.info("BSE fetcher initialized")
    
    def fetch_insider_trading(self, days_back: int = 30) -> Optional[pd.DataFrame]:
        """Fetch insider trading data from BSE"""
        try:
            logger.info("Fetching BSE insider trading data...")
            
            # BSE Insider Trading URL (new format)
            url = f"{self.base_url}/corporates/Insider_Trading_new.aspx?expandable=2"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML tables
            tables = pd.read_html(response.content)
            
            if not tables or len(tables) == 0:
                logger.warning("No BSE insider trading data found")
                return None
            
            # Find the main data table (table with most columns and rows)
            df = None
            max_size = 0
            
            for i, table in enumerate(tables):
                table_size = len(table.columns) * len(table)
                logger.info(f"Table {i}: shape={table.shape}, columns={len(table.columns)}, size={table_size}")
                
                # Look for table with at least 8 columns (insider trading tables are wide)
                if len(table.columns) >= 8 and table_size > max_size:
                    df = table
                    max_size = table_size
                    logger.info(f"Found better candidate: Table {i}")
            
            if df is None or df.empty:
                logger.warning("No valid BSE insider trading table found")
                logger.info("Available tables info:")
                for i, table in enumerate(tables):
                    logger.info(f"  Table {i}: {table.shape}, columns: {list(table.columns)[:5]}")
                return None
            
            logger.info(f"Using table with shape {df.shape} for insider trading data")
            
            df = self._clean_data(df)
            logger.info(f"Fetched {len(df)} insider trading records from BSE")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching BSE insider trading data: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize insider trading data"""
        logger.info(f"BSE insider trading raw columns: {df.columns.tolist()}")
        
        # BSE table often has numeric column headers, set proper names manually
        # Based on BSE insider trading page structure
        if all(isinstance(col, int) for col in df.columns):
            logger.info("Detected numeric column headers, applying standard BSE column names")
            
            # Standard BSE insider trading column order (new format has 16 columns)
            if len(df.columns) == 16:
                expected_columns = [
                    'scrip_code',                    # Column 0: Security Code
                    'company_name',                  # Column 1: Security Name  
                    'person_name',                   # Column 2: Name of Person
                    'person_category',               # Column 3: Category of Person
                    'before_shares',                 # Column 4: Securities held pre transaction
                    'security_type',                 # Column 5: Type of Securities
                    'acquired_shares',               # Column 6: Number (THIS IS THE KEY COLUMN!)
                    'securities_value',              # Column 7: Value
                    'acquisition_disposal',          # Column 8: Transaction Type
                    'after_shares',                  # Column 9: Securities held post transaction
                    'acquisition_period_from',       # Column 10: Period ## from
                    'acquisition_period_to',         # Column 11: Period ## to
                    'acquisition_mode',              # Column 12: Mode of Acquisition
                    'trading_derivative_type',       # Column 13: Trading in Derivatives - Type
                    'trading_derivative_value',      # Column 14: Trading in Derivatives - Buy Value
                    'intimation_date'                # Column 15: Reported to Exchange
                ]
            elif len(df.columns) == 12:
                expected_columns = [
                    'scrip_code', 'company_name', 'person_name', 'person_category',
                    'security_type', 'acquisition_disposal', 'before_shares',
                    'acquired_shares', 'after_shares', 'acquisition_date',
                    'intimation_date', 'acquisition_mode'
                ]
            else:
                # Fallback - create generic column names
                expected_columns = [f'column_{i}' for i in range(len(df.columns))]
            
            # Assign column names
            df.columns = expected_columns
            logger.info(f"Assigned {len(df.columns)} column names: {df.columns.tolist()}")
        else:
            # If columns have names, try to map them
            column_mapping = {
                'Scrip Code': 'scrip_code',
                'Company Name': 'company_name',
                'Name of the Acquirer/Seller': 'person_name',
                'Category of Person': 'person_category',
                'Type of security (prior)': 'security_type_prior',
                'Type of security (Acquired)': 'security_type',
                'No. of securities held prior': 'before_shares',
                'Acquisition/ Disposal': 'acquisition_disposal',
                'No. of Securities acquired / Disposed': 'acquired_shares',
                'Post Acqusition/ Disposal': 'after_shares',
                'Date of allotment advice/ acquisition of shares/ sale of shares specify': 'acquisition_date',
                'Date of Intimation to company': 'intimation_date',
                'Mode of acquisition / disposal': 'acquisition_mode'
            }
            
            existing_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
            df = df.rename(columns=existing_cols)
        
        # Parse dates - handle both old and new format
        date_columns = ['acquisition_date', 'intimation_date', 'acquisition_period_from', 'acquisition_period_to']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Clean numeric columns - especially acquired_shares which is the key for alerts
        numeric_columns = ['before_shares', 'acquired_shares', 'after_shares', 'securities_value']
        for col in numeric_columns:
            if col in df.columns:
                # Remove commas and convert to numeric
                df[col] = df[col].astype(str).str.replace(',', '').str.replace(' ', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Clean text columns to replace NaN with empty string
        text_columns = ['acquisition_mode', 'person_name', 'person_category', 'company_name']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].fillna('')
                df[col] = df[col].replace('nan', '')
                df[col] = df[col].astype(str).str.strip()
        
        # Standardize acquisition/disposal
        if 'acquisition_disposal' in df.columns:
            df['acquisition_disposal'] = df['acquisition_disposal'].str.upper()
            df['acquisition_disposal'] = df['acquisition_disposal'].replace({
                'ACQUISITION': 'ACQUISITION',
                'DISPOSAL': 'DISPOSAL',
                'SELL': 'DISPOSAL',
                'PURCHASE': 'ACQUISITION',
                'BUY': 'ACQUISITION'
            })
        
        # Calculate securities value (approximate using shares * assumed price)
        # Note: BSE doesn't always provide transaction value
        if 'acquired_shares' in df.columns:
            df['securities_value'] = None  # Will be null unless we can calculate
        
        # Add metadata
        df['fetch_date'] = datetime.now().date()
        df['source'] = 'BSE'
        
        # Create symbol from scrip code if needed
        if 'scrip_code' in df.columns:
            df['symbol'] = df['scrip_code'].astype(str)
        
        # Remove any rows that are just headers (sometimes BSE includes header rows in data)
        if 'company_name' in df.columns:
            df = df[df['company_name'].notna()]
            df = df[~df['company_name'].str.upper().str.contains('COMPANY NAME|NAME OF', na=False)]
            logger.info(f"After removing header rows: {len(df)} records")
        
        # NOTE: Not filtering by date - taking all available data from BSE
        # BSE page shows current insider trading disclosures
        logger.info(f"Processing {len(df)} records from BSE")
        
        # Convert dates back to date objects for storage
        for col in date_columns:
            if col in df.columns:
                df[col] = df[col].dt.date
        
        return df


# ============================================================================
# DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """Handles Supabase database operations"""
    
    def __init__(self):
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            raise ValueError("Supabase credentials not configured")
        
        try:
            self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    def get_alert_configurations(self) -> List[Dict]:
        """Get alert configurations from database"""
        try:
            response = self.client.table(Config.TABLE_ALERT_CONFIG)\
                .select("*")\
                .eq("is_active", True)\
                .execute()
            
            configs = response.data if response.data else []
            logger.info(f"Found {len(configs)} active alert configurations")
            return configs
            
        except Exception as e:
            logger.error(f"Error fetching alert configurations: {e}")
            return []
    
    def store_data(self, df: pd.DataFrame, table_name: str) -> bool:
        """Store DataFrame to Supabase table"""
        try:
            if df is None or df.empty:
                logger.warning(f"No data to store in {table_name}")
                return False
            
            records = df.to_dict('records')
            
            # Clean records
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
                    elif hasattr(value, 'item'):
                        record[key] = value.item()
                    elif isinstance(value, (datetime, pd.Timestamp)):
                        record[key] = value.date().isoformat()
                    elif hasattr(value, 'isoformat'):
                        record[key] = value.isoformat()
            
            # Insert in batches
            batch_size = 100
            total_inserted = 0
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                try:
                    response = self.client.table(table_name).insert(batch).execute()
                    total_inserted += len(batch)
                    logger.info(f"Inserted batch of {len(batch)} records into {table_name}")
                except Exception as e:
                    logger.error(f"Error inserting batch into {table_name}: {e}")
            
            logger.info(f"Successfully stored {total_inserted}/{len(records)} records in {table_name}")
            return total_inserted > 0
            
        except Exception as e:
            logger.error(f"Error storing data in {table_name}: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def get_today_summary(self) -> Dict[str, int]:
        """Get summary of today's insider trades"""
        summary = {}
        today = datetime.now().date().isoformat()
        
        try:
            response = self.client.table(Config.TABLE_INSIDER_TRADING)\
                .select("*", count="exact")\
                .eq("fetch_date", today)\
                .execute()
            
            summary['total_records'] = response.count if hasattr(response, 'count') else len(response.data)
            
            # Count acquisitions vs disposals
            if response.data:
                df = pd.DataFrame(response.data)
                if 'acquisition_disposal' in df.columns:
                    summary['acquisitions'] = len(df[df['acquisition_disposal'].str.upper() == 'ACQUISITION'])
                    summary['disposals'] = len(df[df['acquisition_disposal'].str.upper() == 'DISPOSAL'])
                else:
                    summary['acquisitions'] = 0
                    summary['disposals'] = 0
            
            logger.info(f"Found {summary['total_records']} insider trading records for today")
            
        except Exception as e:
            logger.error(f"Error getting summary: {e}")
            summary = {'total_records': 0, 'acquisitions': 0, 'disposals': 0}
        
        return summary


# ============================================================================
# ALERT PROCESSOR
# ============================================================================

class AlertProcessor:
    """Process insider trading data and generate alerts"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.alert_configs = []
    
    def load_alert_configurations(self):
        """Load alert configurations"""
        self.alert_configs = self.db_manager.get_alert_configurations()
        
        # If no DB config, use environment variables
        if not self.alert_configs:
            self.alert_configs = [{
                'min_shares': Config.MIN_SHARES_THRESHOLD,
                'min_value': Config.MIN_VALUE_THRESHOLD,
                'alert_name': 'Default Threshold Alert'
            }]
        
        logger.info(f"Loaded {len(self.alert_configs)} alert configurations")
    
    def find_alerts(self, df: pd.DataFrame) -> List[Dict]:
        """Find insider trades that meet alert criteria"""
        alerts = []
        
        if df is None or df.empty:
            logger.warning("No data to process for alerts")
            return alerts
        
        for config in self.alert_configs:
            min_shares = config.get('min_shares', Config.MIN_SHARES_THRESHOLD)
            min_value = config.get('min_value', Config.MIN_VALUE_THRESHOLD)
            
            # Filter based on thresholds
            filtered = df.copy()
            
            # Apply share threshold
            if 'acquired_shares' in filtered.columns:
                filtered = filtered[filtered['acquired_shares'].abs() >= min_shares]
            
            # Apply value threshold if available
            if 'securities_value' in filtered.columns and min_value:
                value_filter = filtered['securities_value'] >= min_value
                share_filter = filtered['acquired_shares'].abs() >= min_shares
                filtered = filtered[value_filter | share_filter]
            
            for _, row in filtered.iterrows():
                alerts.append({
                    'alert_name': config.get('alert_name', 'Threshold Alert'),
                    'symbol': row.get('symbol', row.get('scrip_code', '')),
                    'company_name': row.get('company_name', ''),
                    'person_name': row.get('person_name', ''),
                    'person_category': row.get('person_category', ''),
                    'transaction_type': row.get('acquisition_disposal', ''),
                    'acquired_shares': row.get('acquired_shares', 0),
                    'before_shares': row.get('before_shares', 0),
                    'after_shares': row.get('after_shares', 0),
                    'securities_value': row.get('securities_value', 0),
                    'acquisition_mode': row.get('acquisition_mode', ''),
                    'intimation_date': row.get('intimation_date', ''),
                    'acquisition_date': row.get('acquisition_date', '')
                })
        
        # Remove duplicates
        seen = set()
        unique_alerts = []
        for alert in alerts:
            key = (alert['symbol'], alert['person_name'], alert['acquired_shares'])
            if key not in seen:
                seen.add(key)
                unique_alerts.append(alert)
        
        logger.info(f"Found {len(unique_alerts)} alerts matching criteria")
        return unique_alerts


# ============================================================================
# EMAIL REPORTER
# ============================================================================

class EmailReporter:
    """Handles email report generation and sending"""
    
    def __init__(self):
        if not Config.EMAIL_USER or not Config.EMAIL_PASSWORD:
            raise ValueError("Email credentials not configured")
        
        try:
            self.yag = yagmail.SMTP(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            logger.info("Email client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize email client: {e}")
            raise
    
    def send_report(self, summary: Dict, alerts: List[Dict] = None):
        """Send daily email report with alerts"""
        try:
            today_str = datetime.now().strftime('%d %B %Y')
            
            if alerts and len(alerts) > 0:
                subject = f"🚨 INSIDER TRADING ALERT - {len(alerts)} Significant Transactions - {today_str}"
            else:
                subject = f"Daily Insider Trading Report - {today_str}"
            
            body = self._create_email_body(summary, alerts)
            
            self.yag.send(to=Config.EMAIL_TO, subject=subject, contents=body)
            logger.info(f"Email report sent successfully to {Config.EMAIL_TO}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email report: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _create_alerts_html(self, alerts: List[Dict]) -> str:
        """Create HTML for alerts"""
        if not alerts:
            return ""
        
        html = """
        <div style="background-color: #fff3cd; border-left: 5px solid #ff6b6b; padding: 15px; margin: 0 0 20px 0; border-radius: 5px;">
            <h2 style="color: #d32f2f; margin: 0 0 10px 0; font-size: 18px;">🚨 SIGNIFICANT INSIDER TRANSACTIONS</h2>
            <p style="font-size: 13px; color: #666; margin: 0 0 10px 0;">The following insider trades exceed your alert thresholds:</p>
            <table style="width: 100%; border-collapse: collapse; background-color: white; margin: 0;">
                <thead>
                    <tr style="background-color: #d32f2f; color: white;">
                        <th style="padding: 8px; text-align: left; font-size: 13px;">Company</th>
                        <th style="padding: 8px; text-align: left; font-size: 13px;">Insider</th>
                        <th style="padding: 8px; text-align: center; font-size: 13px;">Type</th>
                        <th style="padding: 8px; text-align: right; font-size: 13px;">Shares</th>
                        <th style="padding: 8px; text-align: left; font-size: 13px;">Mode</th>
                        <th style="padding: 8px; text-align: left; font-size: 13px;">Date</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for alert in alerts:
            action_color = "#4caf50" if alert['transaction_type'].upper() == 'ACQUISITION' else "#f44336"
            shares = alert['acquired_shares']
            mode = alert.get('acquisition_mode', 'N/A')
            
            # Handle NaN or empty mode
            if not mode or mode == 'nan' or mode == '' or pd.isna(mode):
                mode = 'N/A'
            
            html += f"""
                <tr style="border-bottom: 1px solid #e0e0e0;">
                    <td style="padding: 8px; font-size: 13px;">
                        <strong>{alert['company_name'][:40]}</strong><br>
                        <small style="color: #999; font-size: 11px;">Code: {alert['symbol']}</small>
                    </td>
                    <td style="padding: 8px; font-size: 13px;">
                        {alert['person_name']}<br>
                        <small style="color: #999; font-size: 11px;">{alert['person_category']}</small>
                    </td>
                    <td style="padding: 8px; text-align: center; color: {action_color}; font-weight: bold; font-size: 13px;">
                        {alert['transaction_type']}
                    </td>
                    <td style="padding: 8px; text-align: right; font-size: 13px;">
                        {shares:,.0f}
                    </td>
                    <td style="padding: 8px; font-size: 11px;">
                        {mode}
                    </td>
                    <td style="padding: 8px; font-size: 11px;">
                        {alert['intimation_date']}
                    </td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        return html
    
    def _create_email_body(self, summary: Dict, alerts: List[Dict] = None) -> str:
        """Create HTML email body"""
        today_str = datetime.now().strftime('%d %B %Y, %I:%M %p IST')
        alerts_html = self._create_alerts_html(alerts) if alerts else ""
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 5px; }}
                .container {{ max-width: 900px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 20px; }}
                .header p {{ margin: 3px 0 0 0; font-size: 12px; opacity: 0.9; }}
                .content {{ padding: 15px; }}
                .summary {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .summary-item {{ display: inline-block; margin-right: 30px; }}
                .summary-value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
                .summary-label {{ font-size: 12px; color: #666; }}
                .footer {{ background-color: #f8f9fa; padding: 10px; text-align: center; color: #666; font-size: 11px; margin: 0; }}
                .footer p {{ margin: 3px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Daily Insider Trading Report (BSE)</h1>
                    <p>{today_str}</p>
                </div>
                <div class="content">
                    <div class="summary">
                        <div class="summary-item">
                            <div class="summary-value">{summary.get('total_records', 0)}</div>
                            <div class="summary-label">Total Transactions</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-value" style="color: #4caf50;">{summary.get('acquisitions', 0)}</div>
                            <div class="summary-label">Acquisitions</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-value" style="color: #f44336;">{summary.get('disposals', 0)}</div>
                            <div class="summary-label">Disposals</div>
                        </div>
                    </div>
                    {alerts_html if alerts_html else '<p style="text-align: center; color: #666; padding: 15px 0; margin: 0; font-size: 13px;">No significant insider trading activity matching your alert criteria</p>'}
                </div>
                <div class="footer">
                    <p><strong>Insider Trading Tracker (BSE)</strong></p>
                    <p>Alert Threshold: {Config.MIN_SHARES_THRESHOLD:,} shares</p>
                    <p>Automated Reporting System</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html


# ============================================================================
# TELEGRAM NOTIFIER
# ============================================================================

class TelegramNotifier:
    """Handles Telegram notifications"""
    
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials not configured")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("Telegram notifier initialized")
    
    def send_message(self, message: str) -> bool:
        """Send Telegram message"""
        if not self.enabled:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            response = requests.post(url, json={
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }, timeout=10)
            
            if response.status_code == 200:
                logger.info("Telegram notification sent")
                return True
            else:
                logger.error(f"Telegram failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending Telegram: {e}")
            return False
    
    def send_alerts(self, summary: Dict, alerts: List[Dict]):
        """Send alert summary via Telegram"""
        today_str = datetime.now().strftime('%d %B %Y')
        
        message = f"*📊 Insider Trading Report (BSE)*\n_{today_str}_\n\n"
        message += f"Total: {summary.get('total_records', 0)} transactions\n"
        message += f"🟢 Acquisitions: {summary.get('acquisitions', 0)}\n"
        message += f"🔴 Disposals: {summary.get('disposals', 0)}\n\n"
        
        if alerts and len(alerts) > 0:
            message += f"*🚨 {len(alerts)} SIGNIFICANT ALERTS*\n\n"
            
            # Show all alerts (Telegram allows up to 4096 characters)
            for i, alert in enumerate(alerts):
                if len(message) > 3500:  # Leave room for footer
                    remaining = len(alerts) - i
                    message += f"_...and {remaining} more alerts (check email)_\n\n"
                    break
                    
                emoji = "🟢" if alert['transaction_type'].upper() == 'ACQUISITION' else "🔴"
                mode = alert.get('acquisition_mode', 'N/A')
                if not mode or mode == 'nan' or mode == '' or str(mode) == 'nan':
                    mode = 'N/A'
                    
                message += f"{emoji} *{alert['company_name'][:30]}*\n"
                message += f"   {alert['person_name']}\n"
                message += f"   {alert['transaction_type']}: {alert['acquired_shares']:,.0f} shares\n"
                message += f"   Mode: {mode}\n\n"
        
        message += "_Check email for detailed report_"
        self.send_message(message)


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

class InsiderTradingAutomation:
    """Main orchestrator"""
    
    def __init__(self):
        self.fetcher = BSEInsiderTradingFetcher()
        self.db_manager = DatabaseManager()
        self.alert_processor = AlertProcessor(self.db_manager)
        self.email_reporter = EmailReporter()
        self.telegram_notifier = TelegramNotifier()
    
    def run(self):
        """Main execution"""
        try:
            logger.info("=" * 70)
            logger.info("STARTING INSIDER TRADING DAILY AUTOMATION (BSE)")
            logger.info("=" * 70)
            logger.info(f"Time: {datetime.now().strftime('%d %B %Y, %I:%M:%S %p IST')}")
            
            logger.info("\n[STEP 1/6] Loading alert configurations...")
            self.alert_processor.load_alert_configurations()
            
            logger.info("\n[STEP 2/6] Fetching insider trading data from BSE...")
            df = self.fetcher.fetch_insider_trading(days_back=30)
            
            if df is None or df.empty:
                logger.warning("No new insider trading data found")
                return
            
            logger.info("\n[STEP 3/6] Processing alerts...")
            alerts = self.alert_processor.find_alerts(df)
            
            logger.info("\n[STEP 4/6] Storing data in Supabase...")
            self.db_manager.store_data(df, Config.TABLE_INSIDER_TRADING)
            
            logger.info("\n[STEP 5/6] Generating summary...")
            # Create summary from the data we just processed
            summary = {
                'total_records': len(df),
                'acquisitions': len(df[df['acquisition_disposal'].str.upper() == 'ACQUISITION']) if 'acquisition_disposal' in df.columns else 0,
                'disposals': len(df[df['acquisition_disposal'].str.upper() == 'DISPOSAL']) if 'acquisition_disposal' in df.columns else 0
            }
            logger.info(f"Summary: {summary}")
            
            logger.info("\n[STEP 6/6] Sending notifications...")
            self.email_reporter.send_report(summary, alerts)
            self.telegram_notifier.send_alerts(summary, alerts)
            
            logger.info("\n" + "=" * 70)
            logger.info("AUTOMATION COMPLETED SUCCESSFULLY!")
            logger.info(f"Total Records: {summary.get('total_records', 0)}")
            logger.info(f"Acquisitions: {summary.get('acquisitions', 0)}")
            logger.info(f"Disposals: {summary.get('disposals', 0)}")
            logger.info(f"Alerts Generated: {len(alerts)}")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            logger.error(traceback.format_exc())
            sys.exit(1)


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Entry point"""
    try:
        automation = InsiderTradingAutomation()
        automation.run()
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()