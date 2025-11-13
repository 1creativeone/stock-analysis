#!/usr/bin/env python3
# email_alerts.py
"""
Email Alert System

Sends automated email alerts with top signals.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pandas as pd
import os


class EmailAlerter:
    """Email alert system for top signals."""

    def __init__(self, smtp_server='smtp.gmail.com', smtp_port=587,
                 sender_email=None, sender_password=None):
        """
        Initialize email alerter.

        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port
            sender_email: Sender email address
            sender_password: Sender email password/app password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email or os.environ.get('EMAIL_SENDER')
        self.sender_password = sender_password or os.environ.get('EMAIL_PASSWORD')

    def generate_html_report(self, results_df: pd.DataFrame, top_n: int = 5) -> str:
        """
        Generate HTML email report.

        Args:
            results_df: DataFrame with backtest results
            top_n: Number of top signals to include

        Returns:
            HTML string
        """
        top_signals = results_df.head(top_n)

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1 {{ color: #1f77b4; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th {{ background-color: #1f77b4; color: white; padding: 12px; text-align: left; }}
                td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .metric {{ font-weight: bold; color: #2ca02c; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <h1>📈 Smart Pattern Backtester - Top {top_n} Signals</h1>
            <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>

            <h2>Top Signals (Ranked by Sharpe Ratio)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Ticker</th>
                        <th>Pattern</th>
                        <th>Sharpe</th>
                        <th>CAGR</th>
                        <th>Max DD</th>
                        <th>Win Rate</th>
                        <th>Trades</th>
                        <th>Latest Signal</th>
                    </tr>
                </thead>
                <tbody>
        """

        for idx, (_, row) in enumerate(top_signals.iterrows(), 1):
            latest = row.get('latest_signal', 'N/A')
            if pd.notna(latest) and hasattr(latest, 'strftime'):
                latest = latest.strftime('%Y-%m-%d')

            html += f"""
                    <tr>
                        <td>{idx}</td>
                        <td><strong>{row['ticker']}</strong></td>
                        <td>{row['pattern']}</td>
                        <td class="metric">{row['sharpe']:.2f}</td>
                        <td>{row['cagr']:.1%}</td>
                        <td>{row['max_dd']:.1%}</td>
                        <td>{row['win_rate']:.1%}</td>
                        <td>{int(row['num_trades'])}</td>
                        <td>{latest}</td>
                    </tr>
            """

        html += """
                </tbody>
            </table>

            <h2>Summary Statistics</h2>
            <ul>
                <li><strong>Average Sharpe:</strong> <span class="metric">{:.2f}</span></li>
                <li><strong>Average CAGR:</strong> {:.1%}</li>
                <li><strong>Total Signals:</strong> {}</li>
            </ul>

            <div class="footer">
                <p>This is an automated email from Smart Pattern Backtester.</p>
                <p><em>Disclaimer: Past performance does not guarantee future results. This is for educational purposes only.</em></p>
            </div>
        </body>
        </html>
        """.format(
            results_df['sharpe'].mean(),
            results_df['cagr'].mean(),
            len(results_df)
        )

        return html

    def send_alert(self, results_df: pd.DataFrame, recipient_email: str,
                   subject: str = None, top_n: int = 5) -> bool:
        """
        Send email alert with top signals.

        Args:
            results_df: DataFrame with backtest results
            recipient_email: Recipient email address
            subject: Email subject (default: auto-generated)
            top_n: Number of top signals to include

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.sender_email or not self.sender_password:
            print("❌ Email credentials not configured. Set EMAIL_SENDER and EMAIL_PASSWORD environment variables.")
            return False

        try:
            # Generate subject
            if subject is None:
                subject = f"Top {top_n} Pattern Signals - {datetime.now().strftime('%b %d, %Y')}"

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = recipient_email

            # Generate HTML content
            html_content = self.generate_html_report(results_df, top_n)

            # Attach HTML
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            print(f"✅ Email sent successfully to {recipient_email}")
            return True

        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False

    def send_to_leads(self, results_df: pd.DataFrame, leads_file: str = "leads.csv",
                      top_n: int = 5) -> dict:
        """
        Send alerts to all leads in the database.

        Args:
            results_df: DataFrame with backtest results
            leads_file: Path to leads CSV file
            top_n: Number of top signals to include

        Returns:
            Dictionary with send statistics
        """
        if not os.path.exists(leads_file):
            print(f"❌ Leads file not found: {leads_file}")
            return {'sent': 0, 'failed': 0}

        # Load leads
        try:
            leads_df = pd.read_csv(leads_file, names=['email', 'timestamp'])
        except Exception as e:
            print(f"❌ Error loading leads: {e}")
            return {'sent': 0, 'failed': 0}

        # Send to each lead
        sent = 0
        failed = 0

        for email in leads_df['email'].unique():
            if self.send_alert(results_df, email, top_n=top_n):
                sent += 1
            else:
                failed += 1

        print(f"\n📊 Email Campaign Summary:")
        print(f"  ✅ Sent: {sent}")
        print(f"  ❌ Failed: {failed}")

        return {'sent': sent, 'failed': failed}


def send_test_email(recipient: str):
    """
    Send a test email to verify configuration.

    Args:
        recipient: Test recipient email address
    """
    # Create sample data
    sample_data = pd.DataFrame({
        'ticker': ['AAPL', 'MSFT', 'GOOGL'],
        'pattern': ['EMA Crossover', 'MACD Cross', 'Cup & Handle'],
        'sharpe': [2.1, 1.9, 1.7],
        'cagr': [0.25, 0.22, 0.18],
        'max_dd': [-0.15, -0.18, -0.20],
        'win_rate': [0.65, 0.62, 0.60],
        'num_trades': [12, 15, 18],
        'latest_signal': pd.to_datetime(['2024-11-10', '2024-11-08', '2024-11-05'])
    })

    alerter = EmailAlerter()
    success = alerter.send_alert(sample_data, recipient, subject="Test Email - Pattern Backtester")

    if success:
        print("\n✅ Test email sent successfully!")
    else:
        print("\n❌ Test email failed. Check your configuration.")


if __name__ == "__main__":
    """Test email system."""
    print("Email Alert System")
    print("=" * 50)
    print("\nTo use this module:")
    print("1. Set environment variables:")
    print("   export EMAIL_SENDER='your-email@gmail.com'")
    print("   export EMAIL_PASSWORD='your-app-password'")
    print("\n2. For Gmail, use an App Password:")
    print("   https://support.google.com/accounts/answer/185833")
    print("\n3. Test the system:")
    print("   from email_alerts import send_test_email")
    print("   send_test_email('recipient@example.com')")
    print("=" * 50)
