"""
HTML report generation for surveillance analysis.

Creates professional, interactive HTML reports with charts, tables,
and threat analysis summaries for easy sharing and analysis.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from core.detector_engine import ThreatScore
from data.location import Location


class HTMLReporter:
    """
    Generate professional HTML reports from surveillance analysis.
    
    Features:
    - Threat summary with statistics
    - Device listing with threat levels
    - Location clustering visualization
    - Timeline of detections
    - Charts and graphs
    - Responsive design
    - Print-friendly styling
    """
    
    def __init__(self, logger: logging.Logger = None):
        """
        Initialize HTML reporter.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def create_report(self, threats: Dict[str, ThreatScore],
                     locations: List[Location],
                     title: str = "Surveillance Detection Report",
                     session_info: Optional[Dict] = None) -> str:
        """
        Create HTML report from threat and location data.
        
        Args:
            threats: Dictionary of MAC -> ThreatScore
            locations: List of Location objects
            title: Report title
            session_info: Optional session information dict
            
        Returns:
            HTML report string
        """
        html_parts = [
            self._create_header(title),
            self._create_summary(threats, locations, session_info),
            self._create_threat_analysis(threats),
            self._create_device_table(threats),
            self._create_location_analysis(locations),
            self._create_timeline(threats),
            self._create_footer(),
        ]
        
        html = "\n".join(html_parts)
        self.logger.info("HTML report generated")
        return html
    
    def _create_header(self, title: str) -> str:
        """Create HTML header and styling."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .timestamp {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .summary-card .number {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .summary-card .label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .threat-high {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        .threat-medium {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }}
        
        .threat-low {{
            background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        th {{
            background: #f5f5f5;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #667eea;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}
        
        tr:hover {{
            background: #f9f9f9;
        }}
        
        .threat-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .badge-high {{
            background: #ff4757;
            color: white;
        }}
        
        .badge-medium {{
            background: #ffa502;
            color: white;
        }}
        
        .badge-low {{
            background: #ffd700;
            color: #333;
        }}
        
        .badge-none {{
            background: #2ed573;
            color: white;
        }}
        
        .badge-following {{
            background: #ee5a6f;
            color: white;
            font-weight: 700;
        }}
        
        .score-bar {{
            background: #eee;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .score-fill {{
            height: 100%;
            background: linear-gradient(90deg, #30cfd0 0%, #330867 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.75em;
            font-weight: bold;
        }}
        
        .chart {{
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .chart-row {{
            display: flex;
            margin-bottom: 15px;
            align-items: center;
        }}
        
        .chart-label {{
            width: 150px;
            font-weight: 600;
        }}
        
        .chart-bar {{
            flex: 1;
            background: #eee;
            height: 25px;
            border-radius: 4px;
            overflow: hidden;
            margin: 0 15px;
        }}
        
        .chart-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            padding-right: 10px;
            color: white;
            font-weight: 600;
            font-size: 0.85em;
            justify-content: flex-end;
        }}
        
        .chart-value {{
            width: 50px;
            text-align: right;
            font-weight: 600;
        }}
        
        footer {{
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 40px;
            border-radius: 8px;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                padding: 0;
            }}
            .section {{
                page-break-inside: avoid;
                box-shadow: none;
                border: 1px solid #ddd;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        """
    
    def _create_summary(self, threats: Dict[str, ThreatScore],
                       locations: List[Location],
                       session_info: Optional[Dict]) -> str:
        """Create summary section with statistics."""
        # Calculate threat distribution
        threat_counts = {'high': 0, 'medium': 0, 'low': 0, 'none': 0, 'following': 0}
        total_score = 0
        
        for threat in threats.values():
            threat_counts[threat.level] += 1
            if threat.is_following:
                threat_counts['following'] += 1
            total_score += threat.score
        
        avg_score = total_score / len(threats) if threats else 0
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""
        <header>
            <h1>🔍 Surveillance Detection Report</h1>
            <p class="timestamp">Generated: {timestamp}</p>
        </header>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="number">{len(threats)}</div>
                    <div class="label">Total Devices Tracked</div>
                </div>
                <div class="summary-card threat-high">
                    <div class="number">{threat_counts['high']}</div>
                    <div class="label">High Threats</div>
                </div>
                <div class="summary-card threat-medium">
                    <div class="number">{threat_counts['medium']}</div>
                    <div class="label">Medium Threats</div>
                </div>
                <div class="summary-card threat-low">
                    <div class="number">{threat_counts['low']}</div>
                    <div class="label">Low Threats</div>
                </div>
                <div class="summary-card" style="background: linear-gradient(135deg, #ee5a6f 0%, #f5b747 100%);">
                    <div class="number">{threat_counts['following']}</div>
                    <div class="label">Following Behavior</div>
                </div>
                <div class="summary-card">
                    <div class="number">{len(locations)}</div>
                    <div class="label">Locations Detected</div>
                </div>
            </div>
            
            <div class="chart">
                <h3>Threat Distribution</h3>
                <div class="chart-row">
                    <div class="chart-label">High Threats</div>
                    <div class="chart-bar">
                        <div class="chart-bar-fill" style="width: {threat_counts['high'] * 100 // max(len(threats), 1)}%">
                            {threat_counts['high']}
                        </div>
                    </div>
                    <div class="chart-value">{threat_counts['high']}</div>
                </div>
                <div class="chart-row">
                    <div class="chart-label">Medium Threats</div>
                    <div class="chart-bar">
                        <div class="chart-bar-fill" style="width: {threat_counts['medium'] * 100 // max(len(threats), 1)}%">
                            {threat_counts['medium']}
                        </div>
                    </div>
                    <div class="chart-value">{threat_counts['medium']}</div>
                </div>
                <div class="chart-row">
                    <div class="chart-label">Low Threats</div>
                    <div class="chart-bar">
                        <div class="chart-bar-fill" style="width: {threat_counts['low'] * 100 // max(len(threats), 1)}%">
                            {threat_counts['low']}
                        </div>
                    </div>
                    <div class="chart-value">{threat_counts['low']}</div>
                </div>
            </div>
            
            <p><strong>Average Threat Score:</strong> {avg_score:.1f}/100</p>
        </div>
        """
        return html
    
    def _create_threat_analysis(self, threats: Dict[str, ThreatScore]) -> str:
        """Create detailed threat analysis section."""
        if not threats:
            return "<div class='section'><h2>Threat Analysis</h2><p>No threats detected.</p></div>"
        
        # Sort by score
        sorted_threats = sorted(threats.items(), key=lambda x: x[1].score, reverse=True)
        
        html = """
        <div class="section">
            <h2>Top Threats</h2>
            <table>
                <thead>
                    <tr>
                        <th>Device MAC</th>
                        <th>Threat Level</th>
                        <th>Threat Score</th>
                        <th>Detections</th>
                        <th>Dwell Time</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for mac, threat in sorted_threats[:20]:  # Top 20
            badge_class = f"badge-{threat.level}"
            following = "⚠️ FOLLOWING" if threat.is_following else "Normal"
            
            html += f"""
                    <tr>
                        <td><code>{mac}</code></td>
                        <td><span class="threat-badge {badge_class}">{threat.level.upper()}</span></td>
                        <td>
                            <div class="score-bar">
                                <div class="score-fill" style="width: {threat.score}%">
                                    {threat.score:.1f}
                                </div>
                            </div>
                        </td>
                        <td>{threat.detection_count}</td>
                        <td>{int(threat.dwell_time)}s</td>
                        <td>{following}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        return html
    
    def _create_device_table(self, threats: Dict[str, ThreatScore]) -> str:
        """Create full device listing table."""
        html = """
        <div class="section">
            <h2>All Devices</h2>
            <table>
                <thead>
                    <tr>
                        <th>MAC Address</th>
                        <th>Threat Level</th>
                        <th>Score</th>
                        <th>Locations</th>
                        <th>Avg RSSI</th>
                        <th>Trend</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for mac, threat in sorted(threats.items(), key=lambda x: x[1].score, reverse=True):
            badge_class = f"badge-{threat.level}"
            html += f"""
                    <tr>
                        <td><code>{mac}</code></td>
                        <td><span class="threat-badge {badge_class}">{threat.level.upper()}</span></td>
                        <td>{threat.score:.1f}</td>
                        <td>{threat.location_count}</td>
                        <td>{threat.avg_rssi or 'N/A'}</td>
                        <td>{threat.rssi_trend or 'N/A'}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        return html
    
    def _create_location_analysis(self, locations: List[Location]) -> str:
        """Create location clustering analysis."""
        if not locations:
            return "<div class='section'><h2>Location Analysis</h2><p>No locations detected.</p></div>"
        
        html = """
        <div class="section">
            <h2>Location Clustering</h2>
            <table>
                <thead>
                    <tr>
                        <th>Location</th>
                        <th>Coordinates</th>
                        <th>Duration</th>
                        <th>Device Count</th>
                        <th>Detections</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for location in locations:
            duration = f"{int(location.duration)}s"
            coords = f"{location.centroid.latitude:.6f}, {location.centroid.longitude:.6f}"
            
            html += f"""
                    <tr>
                        <td>{location.name}</td>
                        <td><code>{coords}</code></td>
                        <td>{duration}</td>
                        <td>{location.device_count}</td>
                        <td>{len(location.coordinates)}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        return html
    
    def _create_timeline(self, threats: Dict[str, ThreatScore]) -> str:
        """Create detection timeline."""
        html = """
        <div class="section">
            <h2>Detection Timeline</h2>
            <p>Analysis of device detections over time.</p>
            <div class="chart">
                <h3>Detection Activity</h3>
        """
        
        # Count detections by level
        level_counts = {'high': 0, 'medium': 0, 'low': 0, 'none': 0}
        for threat in threats.values():
            level_counts[threat.level] += 1
        
        for level in ['high', 'medium', 'low', 'none']:
            count = level_counts[level]
            if count > 0:
                pct = int(count * 100 / max(sum(level_counts.values()), 1))
                html += f"""
                <div class="chart-row">
                    <div class="chart-label">{level.capitalize()}</div>
                    <div class="chart-bar">
                        <div class="chart-bar-fill" style="width: {pct}%">
                            {count}
                        </div>
                    </div>
                    <div class="chart-value">{count}</div>
                </div>
                """
        
        html += """
            </div>
        </div>
        """
        return html
    
    def _create_footer(self) -> str:
        """Create footer section."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""
        <footer>
            <p>Surveillance Detection System v3.0.0</p>
            <p>Report generated on {timestamp}</p>
            <p>For security and investigative use only.</p>
        </footer>
    </div>
</body>
</html>
        """
    
    def save(self, html: str, filepath: str) -> bool:
        """
        Save HTML report to file.
        
        Args:
            html: HTML content
            filepath: Destination file path
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            self.logger.info(f"HTML report saved to: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving HTML report: {e}")
            return False