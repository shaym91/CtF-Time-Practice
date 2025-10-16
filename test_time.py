#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from app import START_TIME, END_TIME, is_competition_active
from datetime import datetime
import pytz

BD_TZ = pytz.timezone('Asia/Dhaka')
now = datetime.now(BD_TZ)

print("=" * 50)
print("COMPETITION TIME STATUS (5 PM - 5 AM)")
print("=" * 50)
print(f"START TIME: {START_TIME}")
print(f"END TIME:   {END_TIME}")
print(f"NOW TIME:   {now}")
print(f"ACTIVE:     {is_competition_active()}")
print("=" * 50)

if is_competition_active():
    print("✅ Competition is ACTIVE!")
else:
    print("❌ Competition is NOT ACTIVE")
