use chrono::{DateTime, Local, Duration};
use tracing::{info, warn};

pub struct RateLimiter {
    hourly_posts: Vec<DateTime<Local>>,
    daily_posts: Vec<DateTime<Local>>,
    max_hourly_posts: usize,
    max_daily_posts: usize,
}

impl RateLimiter {
    pub fn new() -> Self {
        Self {
            hourly_posts: Vec::new(),
            daily_posts: Vec::new(),
            max_hourly_posts: 1600,
            max_daily_posts: 11000,
        }
    }

    pub fn can_post(&mut self) -> (bool, Option<&'static str>) {
        let now = Local::now();
        let one_hour_ago = now - Duration::hours(1);
        let one_day_ago = now - Duration::days(1);

        self.hourly_posts.retain(|&ts| ts > one_hour_ago);
        self.daily_posts.retain(|&ts| ts > one_day_ago);

        if self.hourly_posts.len() >= self.max_hourly_posts {
            warn!("Hourly rate limit reached: {}/{}", self.hourly_posts.len(), self.max_hourly_posts);
            return (false, Some("hourly"));
        }

        if self.daily_posts.len() >= self.max_daily_posts {
            warn!("Daily rate limit reached: {}/{}", self.daily_posts.len(), self.max_daily_posts);
            return (false, Some("daily"));
        }

        (true, None)
    }

    pub fn record_post(&mut self) {
        let now = Local::now();
        self.hourly_posts.push(now);
        self.daily_posts.push(now);
        info!("Rate limit status: {} posts this hour, {} posts today", self.hourly_posts.len(), self.daily_posts.len());
    }

    pub fn get_wait_time(&self, limit_type: &str) -> Option<DateTime<Local>> {
        if limit_type == "hourly" && !self.hourly_posts.is_empty() {
            let oldest = self.hourly_posts.iter().min()?;
            Some(*oldest + Duration::hours(1))
        } else if limit_type == "daily" && !self.daily_posts.is_empty() {
            let oldest = self.daily_posts.iter().min()?;
            Some(*oldest + Duration::days(1))
        } else {
            None
        }
    }
}
