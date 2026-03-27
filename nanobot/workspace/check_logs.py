#!/usr/bin/env python3
"""Check for errors in the last hour from VictoriaLogs."""

import httpx
import json
from datetime import datetime, timedelta, timezone

VICTORIALOGS_URL = "http://localhost:42010"

def check_last_hour():
    """Query VictoriaLogs for errors in the last hour."""
    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)
    
    print(f"Checking for errors since: {one_hour_ago.isoformat()}")
    print(f"Current time: {now.isoformat()}\n")
    
    try:
        query = "severity:ERROR"
        url = f"{VICTORIALOGS_URL}/select/logsql/query"
        params = {"query": query, "limit": 100}
        
        with httpx.Client() as client:
            resp = client.get(url, params=params, timeout=30.0)
            resp.raise_for_status()
            
            lines = resp.text.strip().split("\n")
            errors = []
            for line in lines:
                if line.strip():
                    try:
                        log = json.loads(line)
                        errors.append(log)
                    except json.JSONDecodeError:
                        errors.append({"raw": line})
            
            # Filter to last hour
            recent_errors = []
            for err in errors:
                time_str = err.get("_time", "")
                if time_str:
                    try:
                        # Parse ISO format timestamp
                        log_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                        if log_time >= one_hour_ago:
                            recent_errors.append(err)
                    except:
                        recent_errors.append(err)  # Include if can't parse
            
            if not recent_errors:
                print("✅ No errors found in the last hour!")
                print(f"\nNote: Found {len(errors)} total errors in the logs, but all are older than 1 hour.")
                if errors:
                    oldest = min(e.get("_time", "") for e in errors if e.get("_time"))
                    newest = max(e.get("_time", "") for e in errors if e.get("_time"))
                    print(f"  Oldest error: {oldest}")
                    print(f"  Newest error: {newest}")
                return
            
            print(f"⚠️ Found {len(recent_errors)} error(s) in the last hour:\n")
            for i, err in enumerate(recent_errors[:10], 1):
                timestamp = err.get("_time", "unknown")
                service = err.get("service.name", err.get("otelServiceName", "unknown"))
                msg = err.get("error", err.get("exception.message", err.get("_msg", "no message")))
                print(f"{i}. [{timestamp}] {service}")
                print(f"   {msg[:150]}...")
                print()
            if len(recent_errors) > 10:
                print(f"... and {len(recent_errors) - 10} more errors")
                    
    except httpx.ConnectError as e:
        print(f"❌ Could not connect to VictoriaLogs: {e}")
    except httpx.HTTPError as e:
        print(f"❌ HTTP error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_last_hour()
