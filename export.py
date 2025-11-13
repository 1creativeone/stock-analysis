#!/usr/bin/env python3
# export.py
"""
Export utilities for Smart Pattern Backtester.

Provides functionality to export results in various formats:
- CSV exports (detailed)
- Text reports
- Markdown reports
"""
import pandas as pd
import os
from datetime import datetime
from pathlib import Path


class ResultsExporter:
    """Export backtest results to various formats."""

    def __init__(self, results_df, output_dir='exports'):
        """
        Initialize exporter.

        Args:
            results_df: DataFrame with backtest results
            output_dir: Directory to save exports
        """
        self.results_df = results_df
        self.output_dir = output_dir
        Path(output_dir).mkdir(exist_ok=True)

    def export_csv(self, filename=None):
        """
        Export results to CSV.

        Args:
            filename: Output filename (default: auto-generated)

        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"backtest_results_{timestamp}.csv"

        filepath = os.path.join(self.output_dir, filename)
        self.results_df.to_csv(filepath, index=False)

        print(f"✅ Exported to: {filepath}")
        return filepath

    def export_markdown_report(self, filename=None):
        """
        Export detailed markdown report.

        Args:
            filename: Output filename (default: auto-generated)

        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"backtest_report_{timestamp}.md"

        filepath = os.path.join(self.output_dir, filename)

        # Build report
        report_lines = []

        # Header
        report_lines.append("# Smart Pattern Backtester Report")
        report_lines.append(f"\n**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        report_lines.append("\n---\n")

        # Summary statistics
        report_lines.append("## Summary Statistics\n")
        report_lines.append(f"- **Total Signals:** {len(self.results_df)}")
        report_lines.append(f"- **Average Sharpe:** {self.results_df['sharpe'].mean():.2f}")
        report_lines.append(f"- **Average CAGR:** {self.results_df['cagr'].mean():.2%}")
        report_lines.append(f"- **Average Max DD:** {self.results_df['max_dd'].mean():.2%}")
        report_lines.append(f"- **Average Win Rate:** {self.results_df['win_rate'].mean():.2%}")
        report_lines.append("\n---\n")

        # Pattern breakdown
        report_lines.append("## Performance by Pattern\n")

        for pattern in self.results_df['pattern'].unique():
            pattern_data = self.results_df[self.results_df['pattern'] == pattern]

            report_lines.append(f"### {pattern}\n")
            report_lines.append(f"- **Occurrences:** {len(pattern_data)}")
            report_lines.append(f"- **Avg Sharpe:** {pattern_data['sharpe'].mean():.2f}")
            report_lines.append(f"- **Avg CAGR:** {pattern_data['cagr'].mean():.2%}")
            report_lines.append(f"- **Avg Win Rate:** {pattern_data['win_rate'].mean():.2%}")
            report_lines.append("")

        report_lines.append("\n---\n")

        # Top signals
        report_lines.append("## Top 10 Signals (by Sharpe)\n")
        report_lines.append("\n| Rank | Ticker | Pattern | Sharpe | CAGR | Max DD | Win Rate | Trades |")
        report_lines.append("|------|--------|---------|--------|------|--------|----------|--------|")

        top10 = self.results_df.nlargest(10, 'sharpe')
        for idx, (_, row) in enumerate(top10.iterrows(), 1):
            report_lines.append(
                f"| {idx} | {row['ticker']} | {row['pattern']} | "
                f"{row['sharpe']:.2f} | {row['cagr']:.2%} | {row['max_dd']:.2%} | "
                f"{row['win_rate']:.2%} | {int(row['num_trades'])} |"
            )

        report_lines.append("\n---\n")

        # Full results
        report_lines.append("## All Signals\n")
        report_lines.append("\n| Ticker | Pattern | Sharpe | CAGR | Max DD | Win Rate | Trades | Latest Signal |")
        report_lines.append("|--------|---------|--------|------|--------|----------|--------|---------------|")

        for _, row in self.results_df.iterrows():
            latest = row.get('latest_signal', 'N/A')
            if pd.notna(latest) and hasattr(latest, 'strftime'):
                latest = latest.strftime('%Y-%m-%d')

            report_lines.append(
                f"| {row['ticker']} | {row['pattern']} | {row['sharpe']:.2f} | "
                f"{row['cagr']:.2%} | {row['max_dd']:.2%} | {row['win_rate']:.2%} | "
                f"{int(row['num_trades'])} | {latest} |"
            )

        report_lines.append("\n---\n")

        # Footer
        report_lines.append("## Methodology\n")
        report_lines.append("All backtests use:")
        report_lines.append("- 10 years of historical daily data")
        report_lines.append("- Vectorized backtest engine (no look-ahead bias)")
        report_lines.append("- Entry/exit on close prices")
        report_lines.append("- Long-only, no leverage")
        report_lines.append("- No transaction costs\n")

        report_lines.append("**Disclaimer:** Past performance does not guarantee future results.")
        report_lines.append("This is for educational purposes only.\n")

        # Write to file
        with open(filepath, 'w') as f:
            f.write('\n'.join(report_lines))

        print(f"✅ Exported markdown report to: {filepath}")
        return filepath

    def export_text_report(self, filename=None):
        """
        Export simple text report.

        Args:
            filename: Output filename (default: auto-generated)

        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"backtest_report_{timestamp}.txt"

        filepath = os.path.join(self.output_dir, filename)

        # Build report
        lines = []
        lines.append("=" * 80)
        lines.append("SMART PATTERN BACKTESTER - RESULTS REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        lines.append("=" * 80)

        # Summary
        lines.append("\nSUMMARY STATISTICS:")
        lines.append("-" * 80)
        lines.append(f"Total Signals:      {len(self.results_df)}")
        lines.append(f"Average Sharpe:     {self.results_df['sharpe'].mean():.2f}")
        lines.append(f"Average CAGR:       {self.results_df['cagr'].mean():.2%}")
        lines.append(f"Average Max DD:     {self.results_df['max_dd'].mean():.2%}")
        lines.append(f"Average Win Rate:   {self.results_df['win_rate'].mean():.2%}")

        # Top 5
        lines.append("\n" + "=" * 80)
        lines.append("TOP 5 SIGNALS (BY SHARPE RATIO)")
        lines.append("=" * 80)

        for idx, (_, row) in enumerate(self.results_df.head(5).iterrows(), 1):
            lines.append(f"\n#{idx} — {row['ticker']} — {row['pattern']}")
            lines.append("-" * 80)
            lines.append(f"  Sharpe Ratio:     {row['sharpe']:.2f}")
            lines.append(f"  CAGR:             {row['cagr']:.2%}")
            lines.append(f"  Max Drawdown:     {row['max_dd']:.2%}")
            lines.append(f"  Win Rate:         {row['win_rate']:.2%}")
            lines.append(f"  Number of Trades: {int(row['num_trades'])}")

            latest = row.get('latest_signal', 'N/A')
            if pd.notna(latest) and hasattr(latest, 'strftime'):
                latest = latest.strftime('%Y-%m-%d')
            lines.append(f"  Latest Signal:    {latest}")

        lines.append("\n" + "=" * 80)

        # Write to file
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))

        print(f"✅ Exported text report to: {filepath}")
        return filepath

    def export_all(self):
        """Export to all formats."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        csv_path = self.export_csv(f"results_{timestamp}.csv")
        md_path = self.export_markdown_report(f"report_{timestamp}.md")
        txt_path = self.export_text_report(f"report_{timestamp}.txt")

        print(f"\n✅ All exports complete!")
        return {
            'csv': csv_path,
            'markdown': md_path,
            'text': txt_path
        }


def export_results(results_df, format='all', output_dir='exports'):
    """
    Convenience function to export results.

    Args:
        results_df: DataFrame with backtest results
        format: Export format ('csv', 'markdown', 'text', 'all')
        output_dir: Output directory

    Returns:
        Path(s) to exported file(s)
    """
    exporter = ResultsExporter(results_df, output_dir)

    if format == 'csv':
        return exporter.export_csv()
    elif format == 'markdown':
        return exporter.export_markdown_report()
    elif format == 'text':
        return exporter.export_text_report()
    elif format == 'all':
        return exporter.export_all()
    else:
        raise ValueError(f"Unknown format: {format}")


if __name__ == "__main__":
    """Test export functionality."""
    print("Testing export functionality...\n")

    # Create sample data
    sample_data = pd.DataFrame({
        'ticker': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
        'pattern': ['Double Bottom', '52W Breakout', 'RSI Divergence', 'Double Bottom', '52W Breakout'],
        'sharpe': [2.1, 1.9, 1.7, 1.5, 1.4],
        'cagr': [0.25, 0.22, 0.18, 0.15, 0.14],
        'max_dd': [-0.15, -0.18, -0.20, -0.22, -0.25],
        'win_rate': [0.65, 0.62, 0.60, 0.58, 0.55],
        'num_trades': [12, 15, 18, 10, 20],
        'latest_signal': pd.to_datetime(['2024-11-10', '2024-11-08', '2024-11-05', '2024-11-01', '2024-10-28'])
    })

    # Export all formats
    exporter = ResultsExporter(sample_data, output_dir='exports_test')
    paths = exporter.export_all()

    print(f"\n{'='*80}")
    print("Test complete! Check the exports_test/ directory for output files.")
    print(f"{'='*80}")
