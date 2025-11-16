"""
Content validator for generated posts.

Ensures generated content meets quality and safety standards
before posting to Bluesky.
"""

import re
import logging

class ContentValidator:
    """Validates generated content before posting."""
    
    def __init__(self, char_limit=280, min_length=10):
        """
        Initialize content validator.
        
        Args:
            char_limit: Maximum character limit
            min_length: Minimum acceptable length for a post
        """
        self.char_limit = char_limit
        self.min_length = min_length
        
        # Patterns for problematic content
        self.spam_patterns = [
            r'(click here|follow me|check out|dm me|buy now)',
            r'https?://bit\.ly',  # Shortened URLs often used for spam
            r'💰|💵|💴|💶|💷',  # Money emojis often in spam
            r'\b(crypto|nft|airdrop)\b',  # Common spam keywords
        ]
        
        # Patterns for potentially harmful content
        self.harmful_patterns = [
            r'\b(kill|die|suicide|harm yourself)\b',
            r'\b(hate|racist|bigot)\b',
        ]
        
        logging.info(f"Content validator initialized: {min_length}-{char_limit} chars")
    
    def validate(self, content):
        """
        Validate content for posting.
        
        Args:
            content: The text content to validate
            
        Returns:
            tuple: (is_valid, reason) where is_valid is bool and reason is str
        """
        if not content:
            return False, "Content is empty"
        
        content_stripped = content.strip()
        
        # Check if content is too short
        if len(content_stripped) < self.min_length:
            return False, f"Content too short ({len(content_stripped)} chars, minimum {self.min_length})"
        
        # Check if content exceeds character limit
        if len(content_stripped) > self.char_limit:
            return False, f"Content exceeds limit ({len(content_stripped)} chars, max {self.char_limit})"
        
        # Check for empty or whitespace-only content
        if not content_stripped or content_stripped.isspace():
            return False, "Content is empty or whitespace only"
        
        # Check for repetitive content (same character repeated)
        if self._is_repetitive(content_stripped):
            return False, "Content appears to be repetitive or low quality"
        
        # Check for spam patterns
        spam_found = self._check_patterns(content_stripped.lower(), self.spam_patterns)
        if spam_found:
            return False, f"Content contains spam-like patterns: {spam_found}"
        
        # Check for harmful content
        harmful_found = self._check_patterns(content_stripped.lower(), self.harmful_patterns)
        if harmful_found:
            return False, f"Content contains potentially harmful language: {harmful_found}"
        
        # Check if content looks like an error message
        if self._looks_like_error(content_stripped):
            return False, "Content appears to be an error message"
        
        # Check if content is just a URL
        if self._is_just_url(content_stripped):
            return False, "Content is just a URL without context"
        
        # All checks passed
        return True, "Content validated successfully"
    
    def _is_repetitive(self, content, threshold=0.5):
        """Check if content has too many repeated characters."""
        if len(content) < 10:
            return False
        
        # Count most common character
        char_counts = {}
        for char in content:
            if char.isalnum():  # Only count alphanumeric
                char_counts[char] = char_counts.get(char, 0) + 1
        
        if not char_counts:
            return True  # No alphanumeric characters
        
        most_common_count = max(char_counts.values())
        total_alnum = sum(char_counts.values())
        
        # If one character makes up more than threshold of content
        return (most_common_count / total_alnum) > threshold
    
    def _check_patterns(self, content, patterns):
        """Check content against a list of regex patterns."""
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(0)
        return None
    
    def _looks_like_error(self, content):
        """Check if content looks like an error message."""
        error_indicators = [
            'error:',
            'exception:',
            'failed to',
            'could not',
            'unable to',
            'traceback',
            'stack trace'
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in error_indicators)
    
    def _is_just_url(self, content):
        """Check if content is just a URL."""
        # Simple URL pattern
        url_pattern = r'^https?://[^\s]+$'
        return bool(re.match(url_pattern, content.strip()))
    
    def sanitize(self, content):
        """
        Sanitize content by removing or fixing common issues.
        
        Args:
            content: The content to sanitize
            
        Returns:
            str: Sanitized content
        """
        if not content:
            return ""
        
        # Strip whitespace
        sanitized = content.strip()
        
        # Remove multiple consecutive spaces
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Remove quotes that might have been added by the LLM
        if sanitized.startswith('"') and sanitized.endswith('"'):
            sanitized = sanitized[1:-1].strip()
        if sanitized.startswith("'") and sanitized.endswith("'"):
            sanitized = sanitized[1:-1].strip()
        
        # Remove common LLM artifacts
        artifacts = [
            "Here's a post:",
            "Here is a post:",
            "Generated post:",
            "Post:",
        ]
        for artifact in artifacts:
            if sanitized.lower().startswith(artifact.lower()):
                sanitized = sanitized[len(artifact):].strip()
        
        return sanitized
    
    def get_content_stats(self, content):
        """Get statistics about the content."""
        return {
            'length': len(content),
            'words': len(content.split()),
            'lines': len(content.splitlines()),
            'has_urls': bool(re.search(r'https?://', content)),
            'has_hashtags': bool(re.search(r'#\w+', content)),
            'has_mentions': bool(re.search(r'@\w+', content)),
        }
