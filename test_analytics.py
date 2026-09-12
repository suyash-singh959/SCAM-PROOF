from data_layer.analytics import (
    get_total_scans,
    get_high_risk_count,
    get_average_scam_score,
    get_scan_statistics,
    get_recent_scan_history,
    get_risk_distribution,
    get_dashboard_data
)


try:
    print("Total scans:", get_total_scans())
    print("High-risk scans:", get_high_risk_count())
    print("Average scam score:", get_average_scam_score())
    print("Scan statistics:", get_scan_statistics())
    print("\nRecent scan history:")

    for scan in get_recent_scan_history(5):
        print(scan)
    print("\nRisk distribution:")
    print(get_risk_distribution())

    print("\nDashboard data:")
    print(get_dashboard_data())

except Exception as e:
    print(f"Analytics failed: {e}")