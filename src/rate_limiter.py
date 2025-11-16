"""
Rate limiter for Bluesky API operations.

Based on Bluesky's official rate limits:
- 5,000 points per hour
- 35,000 points per day
- Creates: 3 points
- Updates: 2 points
- Deletes: 1 point

For a posting bot, we mainly care about creates (posts).
Maximum posts per hour: 1,666
Maximum posts per day: 11,666

We'll be conservative and track our own limits.
"""

import time
import logging
from datetime import datetime, timedelta
from collections import deque

class RateLimiter:
    """Rate limiter to respect Bluesky's API limits."""
    
    def __init__(self, hourly_limit=100, daily_limit=500):
        """
        Initialize rate limiter.
        
        Args:
            hourly_limit: Maximum operations per hour (default: 100, well below Bluesky's 1,666)
            daily_limit: Maximum operations per day (default: 500, well below Bluesky's 11,666)
        """
        self.hourly_limit = hourly_limit
        self.daily_limit = daily_limit
        
        # Track timestamps of operations
        self.hourly_operations = deque()  # timestamps in last hour
        self.daily_operations = deque()   # timestamps in last day
        
        logging.info(f"Rate limiter initialized: {hourly_limit}/hour, {daily_limit}/day")
    
    def _clean_old_operations(self):
        """Remove operations outside the time windows."""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        
        # Remove hourly operations older than 1 hour
        while self.hourly_operations and self.hourly_operations[0] < hour_ago:
            self.hourly_operations.popleft()
        
        # Remove daily operations older than 1 day
        while self.daily_operations and self.daily_operations[0] < day_ago:
            self.daily_operations.popleft()
    
    def can_proceed(self):
        """
        Check if we can proceed with an operation.
        
        Returns:
            tuple: (bool, str) - (can_proceed, reason_if_not)
        """
        self._clean_old_operations()
        
        if len(self.hourly_operations) >= self.hourly_limit:
            return False, f"Hourly rate limit reached ({self.hourly_limit} operations/hour)"
        
        if len(self.daily_operations) >= self.daily_limit:
            return False, f"Daily rate limit reached ({self.daily_limit} operations/day)"
        
        return True, ""
    
    def record_operation(self):
        """Record that an operation was performed."""
        now = datetime.now()
        self.hourly_operations.append(now)
        self.daily_operations.append(now)
        
        self._clean_old_operations()
        
        hourly_count = len(self.hourly_operations)
        daily_count = len(self.daily_operations)
        
        logging.debug(
            f"Operation recorded. Current counts: {hourly_count}/{self.hourly_limit} (hour), "
            f"{daily_count}/{self.daily_limit} (day)"
        )
    
    def get_stats(self):
        """Get current rate limit statistics."""
        self._clean_old_operations()
        return {
            'hourly_count': len(self.hourly_operations),
            'hourly_limit': self.hourly_limit,
            'hourly_remaining': self.hourly_limit - len(self.hourly_operations),
            'daily_count': len(self.daily_operations),
            'daily_limit': self.daily_limit,
            'daily_remaining': self.daily_limit - len(self.daily_operations)
        }
    
    def wait_if_needed(self):
        """
        Wait if rate limit is reached.
        
        Returns:
            bool: True if had to wait, False otherwise
        """
        can_proceed, reason = self.can_proceed()
        
        if not can_proceed:
            logging.warning(f"Rate limit reached: {reason}")
            
            # Calculate wait time
            self._clean_old_operations()
            
            if len(self.hourly_operations) >= self.hourly_limit:
                # Wait until oldest hourly operation expires
                oldest = self.hourly_operations[0]
                wait_until = oldest + timedelta(hours=1)
                wait_seconds = (wait_until - datetime.now()).total_seconds()
                
                if wait_seconds > 0:
                    logging.info(f"Waiting {wait_seconds:.0f} seconds for hourly rate limit to reset...")
                    print(f"⏳ Rate limit reached. Waiting {wait_seconds:.0f} seconds...")
                    time.sleep(wait_seconds + 1)  # Add 1 second buffer
                    return True
            
            if len(self.daily_operations) >= self.daily_limit:
                # Wait until oldest daily operation expires
                oldest = self.daily_operations[0]
                wait_until = oldest + timedelta(days=1)
                wait_seconds = (wait_until - datetime.now()).total_seconds()
                
                if wait_seconds > 0:
                    logging.info(f"Waiting {wait_seconds:.0f} seconds for daily rate limit to reset...")
                    print(f"⏳ Daily rate limit reached. Waiting {wait_seconds:.0f} seconds...")
                    time.sleep(wait_seconds + 1)  # Add 1 second buffer
                    return True
        
        return False
