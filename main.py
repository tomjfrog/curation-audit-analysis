import datetime
import json
import os
from collections import Counter

import requests
from requests.auth import HTTPBasicAuth


def process_events(output):
    """
    Process events from API output:
    - Count all actions
    - Filter out 'approved' events
    - Extract 'blocked' and 'passed' events separately
    Returns tuple: (filtered_output, action_counts, blocked_events, passed_events)
    """
    # Count actions
    action_counts = Counter()
    events = output.get('data', [])
    
    blocked_events = []
    passed_events = []
    
    for event in events:
        action = event.get('action', 'unknown')
        action_counts[action] += 1
        
        # Separate blocked and passed events
        if action == 'blocked':
            blocked_events.append(event)
        elif action == 'passed':
            passed_events.append(event)
    
    # Filter out approved events
    filtered_data = [event for event in events if event.get('action') != 'approved']
    
    # Create filtered output with original structure
    filtered_output = {
        'data': filtered_data,
        'meta': output.get('meta', {})
    }
    
    return filtered_output, action_counts, blocked_events, passed_events


session = requests.Session()
auth = HTTPBasicAuth(os.environ.get('JF_USER', 'username'), os.environ.get('JF_PASSWORD', 'password'))
base_url = os.environ.get('JF_URL', 'https://env_domain')


now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
print(now.isoformat(), 'start')
last_print = now


start = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
curr = start - datetime.timedelta(days=30)


events_fetched = 0
total_action_counts = Counter()
blocked_events = []
while curr < start:
    offset = 0
    while True:
        now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        if now != last_print:
            last_print = now
            print(now.isoformat(), 'created_at_start: %s, events_fetched: %d, offset: %d' % (curr.isoformat(), events_fetched, offset))
        response = session.get(
            f'{base_url}/xray/api/v1/curation/audit/packages',
            params={
                'include_total': 'false',
                'order_by': 'id',
                'direction': 'asc',
                'num_of_rows': 1000,
                'created_at_start': curr.isoformat(),
                'offset': offset,
            },
            auth=auth)
        response.raise_for_status()
        output = response.json()
        
        # Process events: filter approved and count actions
        _, action_counts, batch_blocked, _ = process_events(output)
        total_action_counts.update(action_counts)
        
        # Collect blocked events for analysis
        blocked_events.extend(batch_blocked)
        next_offset = output['meta']['next_offset']
        if not next_offset:
            break
        offset = next_offset
        events_fetched += output['meta']['result_count']
    curr += datetime.timedelta(days=7)


now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
print(now.isoformat(), 'fetched %d events' % events_fetched)
print(now.isoformat(), 'action counts:', dict(total_action_counts))

# Count blocked packages by policy_name
policy_counts = Counter()
for event in blocked_events:
    policies = event.get('policies', [])
    for policy in policies:
        policy_name = policy.get('policy_name', 'unknown')
        policy_counts[policy_name] += 1

# Generate report data
approved = total_action_counts.get('approved', 0)
blocked_total = len(blocked_events)

# Output policy counts as JSON to console
print(now.isoformat(), 'blocked packages by policy:')
print('# This report shows the count of blocked packages grouped by policy_name.')
print('# blocked_total is the count of blocked packages.')
print('# Each count represents how many times a policy blocked a package during the audit period.')
print('# Note: Each package may be blocked by multiple policies, so blocked_total and the sum of policy counts will not match.')
print(json.dumps({
    'approved': approved,
    'blocked': {
        'blocked_total': blocked_total,
        **dict(policy_counts)
    }
}, indent=2))

