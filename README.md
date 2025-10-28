# Curation Audit Analysis

A Python script that analyzes JFrog Xray curation audit package events, filtering out approved packages and providing detailed statistics on blocked packages grouped by policy.

## Overview

This script fetches curation audit data from a JFrog Xray API endpoint and generates a comprehensive report on package approval and blocking statistics. It processes events over a 30-day period, with 7-day intervals, to provide insights into security policy enforcement.

## Features

- **Efficient Data Retrieval**: Automatically handles pagination to fetch all audit events
- **Smart Filtering**: Separates approved, blocked, and passed packages
- **Policy Analysis**: Groups blocked packages by the policies that triggered the block
- **Progress Tracking**: Real-time console output showing fetch progress
- **JSON Report**: Clean, structured JSON output with actionable insights

## Prerequisites

- Python 3.6+
- Required Python packages:
  - `requests`
- **JFrog User Permissions**: Requires a valid user with the "VIEW_POLICIES" permission.

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install requests
```

## Configuration

The script requires three environment variables to connect to your JFrog instance:

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `JF_URL` | Base URL of your JFrog instance | `https://mycompany.jfrog.io` |
| `JF_USER` | JFrog username for authentication | `admin` |
| `JF_PASSWORD` | JFrog password or API key | `your-password` |

### Setting Environment Variables

**Linux/macOS:**
```bash
export JF_URL="https://mycompany.jfrog.io"
export JF_USER="your-username"
export JF_PASSWORD="your-password"
```

**Windows (PowerShell):**
```powershell
$env:JF_URL="https://mycompany.jfrog.io"
$env:JF_USER="your-username"
$env:JF_PASSWORD="your-password"
```

**Windows (Command Prompt):**
```cmd
set JF_URL=https://mycompany.jfrog.io
set JF_USER=your-username
set JF_PASSWORD=your-password
```

Alternatively, you can create a `.env` file (not recommended for passwords) or pass variables inline when running the script.

## Usage

1. Set the required environment variables (see Configuration above)
2. Run the script:

```bash
python main.py
```

## How It Works

### Data Retrieval Process

1. **Time Period**: The script queries the last 30 days of curation audit data
2. **Pagination**: Automatically handles paginated API responses (1000 records per page)
3. **Batch Processing**: Processes events in 7-day intervals to manage large datasets efficiently

### Data Processing

The script processes each event to:
- **Count Actions**: Tracks all action types (approved, blocked, passed, etc.)
- **Filter Approved**: Separates approved packages for reporting
- **Extract Blocked Events**: Collects all blocked package events
- **Group by Policy**: Aggregates blocked packages by policy name

### Output

The script generates console output with:

1. **Progress Updates**: Real-time status showing:
   - Current timestamp
   - Time period being queried
   - Total events fetched
   - Current pagination offset

2. **Action Counts**: Summary of all event types found:
   ```python
   action counts: {'approved': 1234, 'blocked': 45, 'passed': 12}
   ```

3. **Final Report**: JSON-formatted summary with:
   ```json
   {
     "approved": 1234,
     "blocked": {
       "blocked_total": 45,
       "tsj-malicious-package": 30,
       "another-policy": 15
     }
   }
   ```

### Understanding the Report

- **`approved`**: Total count of packages that were approved during the audit period
- **`blocked.blocked_total`**: Total number of unique packages that were blocked
- **`blocked.{policy_name}`**: Number of times each policy blocked a package

> **Important Note**: A single package can be blocked by multiple policies. Therefore, the sum of policy counts may exceed `blocked_total`. This is expected behavior.

## Example Output

```
2025-10-15T10:30:00+00:00 start
2025-10-15T10:30:01+00:00 created_at_start: 2025-09-15T10:30:00+00:00, events_fetched: 0, offset: 0
2025-10-15T10:30:02+00:00 created_at_start: 2025-09-15T10:30:00+00:00, events_fetched: 1000, offset: 1000
...
2025-10-15T10:35:00+00:00 fetched 15234 events
2025-10-15T10:35:00+00:00 action counts: {'approved': 14789, 'blocked': 445, 'passed': 0}
2025-10-15T10:35:00+00:00 blocked packages by policy:
# This report shows the count of blocked packages grouped by policy_name.
# blocked_total is the count of blocked packages.
# Each count represents how many times a policy blocked a package during the audit period.
# Note: Each package may be blocked by multiple policies, so blocked_total and the sum of policy counts will not match.
{
  "approved": 14789,
  "blocked": {
    "blocked_total": 445,
    "tsj-malicious-package": 280,
    "security-policy-vulnerability": 165,
    "license-compliance-check": 89
  }
}
```

## API Endpoint

This script is built on the JFrog REST API for [Approved/Blocked Audit Logs](https://jfrog.com/help/r/jfrog-rest-apis/get-approved/blocked-audit-logs-api).

The script queries:
```
GET {JF_URL}/xray/api/v1/curation/audit/packages
```

With the following parameters:
- `include_total`: false
- `order_by`: id
- `direction`: asc
- `num_of_rows`: 1000
- `created_at_start`: ISO timestamp (automatically managed)
- `offset`: pagination offset (automatically managed)

## Troubleshooting

### Authentication Errors
- Verify your `JF_USER` and `JF_PASSWORD` environment variables are set correctly
- Check that your credentials have permissions to access the Xray API
- For JFrog Cloud instances, ensure you're using an API key if required

### Connection Errors
- Verify the `JF_URL` environment variable is correct
- Check network connectivity to your JFrog instance
- Ensure the URL uses the correct protocol (https/http)

### No Data Returned
- Verify there are events in the specified time period
- Check that Xray is properly configured and monitoring packages
- Review JFrog logs for any API issues

## Development

### Code Structure

- **`process_events()`**: Function that processes API response data, filtering and categorizing events
- **Main Loop**: Handles time-based iteration and pagination
- **Policy Aggregation**: Counts blocked packages by policy name
- **Report Generation**: Creates the final JSON output

### Customization

To modify the analysis period, change line 58:
```python
curr = start - datetime.timedelta(days=30)  # Change 30 to desired days
```

To modify the batch size, change line 59:
```python
curr += datetime.timedelta(days=7)  # Change 7 to desired interval
```

## License

[Add your license information here]

## Contributing

[Add contributing guidelines if applicable]

## Support

For issues or questions:
- Check the JFrog documentation: https://www.jfrog.com/confluence/
- Review Xray API documentation for endpoint details
- Contact your JFrog administrator for environment-specific help

