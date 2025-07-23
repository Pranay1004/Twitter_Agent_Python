"""
Thread Builder Utility
Converts long-form content into properly formatted Twitter threads
"""

import re
from typing import List, Dict, Tuple
from .logger import setup_logger

logger = setup_logger(__name__)

class ThreadBuilder:
    def __init__(self):
        self.max_tweet_length = 280
        self.hashtag_space = 25  # Reserve space for hashtags
        self.thread_numbering_space = 10  # Reserve space for "1/5" etc.
        self.effective_length = self.max_tweet_length - self.hashtag_space - self.thread_numbering_space
        
        # Enhanced engagement patterns
        self.engaging_starters = [
            "Here's what nobody tells you about",
            "The data reveals something shocking:",
            "After analyzing 1000+ cases:",
            "Industry insiders are talking about",
            "The numbers don't lie:",
            "What we learned from recent deployments:",
            "Breaking down the real impact:",
            "The truth behind the hype:",
            "Here's why this matters:",
            "Most people miss this critical detail:"
        ]
        
        self.transition_phrases = [
            "But here's where it gets interesting...",
            "The real game-changer?",
            "This is just the beginning.",
            "Wait, there's more.",
            "The plot thickens:",
            "Here's the kicker:",
            "And then something unexpected happened:",
            "The results speak for themselves:",
            "But the story doesn't end there:",
            "This changes everything:"
        ]
        
        self.power_words = [
            "breakthrough", "revolutionary", "game-changing", "unprecedented", 
            "cutting-edge", "transformative", "disruptive", "innovative",
            "explosive", "dramatic", "stunning", "remarkable"
        ]
        
    def split_content(self, content: str, max_tweets: int = 10) -> List[str]:
        """Split long content into tweet-sized chunks with improved natural flow"""
        logger.info(f"Splitting content of {len(content)} characters into tweets")
        
        if len(content) <= self.effective_length:
            return [content]
            
        # Enhanced splitting strategy
        tweets = []
        remaining_content = content
        tweet_count = 0
        
        while remaining_content and tweet_count < max_tweets:
            chunk = self._get_next_chunk_enhanced(remaining_content, tweet_count)
            if chunk:
                tweets.append(chunk)
                # Remove processed content more intelligently
                remaining_content = self._remove_processed_content(remaining_content, chunk)
                tweet_count += 1
            else:
                break
                
        if remaining_content and len(remaining_content.strip()) > 50:
            logger.warning(f"Content truncated: {len(remaining_content)} characters remaining")
            # Try to create a final tweet with remaining important content
            final_chunk = self._create_closing_tweet(remaining_content)
            if final_chunk and len(tweets) < max_tweets:
                tweets.append(final_chunk)
                
        return tweets
    
    def _get_next_chunk_enhanced(self, content: str, tweet_index: int) -> str:
        """Enhanced chunk extraction with context awareness"""
        if len(content) <= self.effective_length:
            return content.strip()
        
        # Different strategies based on tweet position
        if tweet_index == 0:
            return self._create_hook_tweet(content)
        
        # Look for natural breaking points
        best_break = self._find_best_break_point(content[:self.effective_length + 100])
        
        if best_break > 0:
            chunk = content[:best_break].strip()
            # Add transition elements for middle tweets
            if tweet_index > 0 and len(chunk) < self.effective_length - 30:
                chunk = self._add_transition_element(chunk, tweet_index)
            return chunk
        
        # Fallback to word boundary
        return self._fallback_word_split(content)
    
    def _create_hook_tweet(self, content: str) -> str:
        """Create an engaging opening tweet"""
        # Extract key topic/theme from first part of content
        first_part = content[:200]
        
        # Look for numbers, statistics, or strong claims
        numbers = re.findall(r'\d+%|\$\d+[MBK]?|\d+x|\d+ years?|\d+ months?', first_part)
        strong_words = [word for word in self.power_words if word.lower() in first_part.lower()]
        
        # Create hook based on available elements
        if numbers and strong_words:
            hook = f"🧵 THREAD: The {strong_words[0]} {numbers[0]} story that's reshaping drone ops."
        elif numbers:
            hook = f"🧵 THREAD: {numbers[0]} - the number that's changing everything in drone tech."
        elif strong_words:
            hook = f"🧵 THREAD: The {strong_words[0]} shift happening in drone operations right now."
        else:
            # Extract first meaningful sentence
            sentences = re.split(r'[.!?]+', content)
            first_sentence = sentences[0].strip() if sentences else content[:100]
            hook = f"🧵 THREAD: {first_sentence[:150]}..."
        
        # Ensure it fits and ends with engagement
        if len(hook) > self.effective_length - 5:
            hook = hook[:self.effective_length - 8] + "... 👇"
        elif not hook.endswith('👇'):
            hook += " 👇"
            
        return hook
    
    def _find_best_break_point(self, content: str) -> int:
        """Find the best place to break content for natural flow"""
        # Priority order: sentence end, paragraph break, clause break, word boundary
        
        # Sentence boundaries
        sentence_ends = [(m.end(), 3) for m in re.finditer(r'[.!?]\s+', content)]
        
        # Paragraph breaks
        para_breaks = [(m.start(), 4) for m in re.finditer(r'\n\s*\n', content)]
        
        # Natural clause breaks
        clause_breaks = [(m.end(), 2) for m in re.finditer(r'[,;]\s+(?:but|however|meanwhile|also|additionally)', content, re.IGNORECASE)]
        
        # Combine all break points with priorities
        all_breaks = sentence_ends + para_breaks + clause_breaks
        all_breaks.sort(key=lambda x: (-x[1], -x[0]))  # Sort by priority, then position
        
        # Find the best break within our target range
        for pos, priority in all_breaks:
            if self.effective_length - 50 <= pos <= self.effective_length:
                return pos
        
        # Fallback to last sentence that fits
        for pos, priority in sentence_ends:
            if pos <= self.effective_length:
                return pos
                
        return 0
    
    def _add_transition_element(self, chunk: str, tweet_index: int) -> str:
        """Add smooth transitions between tweets"""
        if tweet_index < 3 and len(self.transition_phrases) > tweet_index - 1:
            transition = self.transition_phrases[min(tweet_index - 1, len(self.transition_phrases) - 1)]
            if len(chunk + f" {transition}") <= self.effective_length:
                chunk = f"{transition} {chunk}"
        
        return chunk
    
    def _remove_processed_content(self, content: str, processed_chunk: str) -> str:
        """Intelligently remove processed content to avoid repetition"""
        # Remove the exact processed text
        clean_chunk = processed_chunk.strip()
        
        # Remove thread indicators and transitions for matching
        clean_chunk = re.sub(r'^🧵 THREAD:\s*', '', clean_chunk)
        clean_chunk = re.sub(r'👇$', '', clean_chunk).strip()
        clean_chunk = re.sub(r'^(' + '|'.join(re.escape(t) for t in self.transition_phrases) + r')\s*', '', clean_chunk, flags=re.IGNORECASE)
        
        # Find and remove the matching content
        if clean_chunk in content:
            remaining = content.replace(clean_chunk, '', 1)
        else:
            # Fallback: remove first N characters where N is length of clean chunk
            remaining = content[len(clean_chunk):]
        
        return remaining.strip()
    
    def _create_closing_tweet(self, remaining_content: str) -> str:
        """Create a compelling closing tweet from remaining content"""
        # Extract key points or call to action
        if len(remaining_content) <= self.effective_length:
            return remaining_content.strip()
        
        # Look for conclusions, results, or calls to action
        conclusion_patterns = [
            r'(in conclusion|finally|the result|outcome|impact).*?[.!?]',
            r'(this means|therefore|consequently).*?[.!?]',
            r'(ready to|time to|start|begin).*?[.!?]'
        ]
        
        for pattern in conclusion_patterns:
            match = re.search(pattern, remaining_content, re.IGNORECASE | re.DOTALL)
            if match:
                conclusion = match.group(0)
                if len(conclusion) <= self.effective_length:
                    return conclusion.strip()
        
        # Fallback to first sentence of remaining content
        sentences = re.split(r'[.!?]+', remaining_content)
        return sentences[0].strip()[:self.effective_length] if sentences else ""
    
    def _fallback_word_split(self, content: str) -> str:
        """Fallback word boundary splitting"""
        words = content[:self.effective_length].split()
        while words and len(' '.join(words)) > self.effective_length:
            words.pop()
        return ' '.join(words)
    
    def add_thread_numbers(self, tweets: List[str]) -> List[str]:
        """Add thread numbering to tweets - removed as per requirement"""
        # This function now just returns the original tweets without numbering
        # to ensure we have maximum space for drone content
        
        # Ensure tweets are within character limits
        limited_tweets = []
        for tweet in tweets:
            if len(tweet) > self.max_tweet_length:
                limited_tweets.append(tweet[:self.max_tweet_length-3] + "...")
            else:
                limited_tweets.append(tweet)
                
        return limited_tweets
    
    def optimize_thread_flow(self, tweets: List[str]) -> List[str]:
        """Enhanced thread flow optimization"""
        if not tweets:
            return tweets
            
        optimized = tweets.copy()
        
        # Enhance first tweet if it's not already a hook
        if not any(indicator in optimized[0] for indicator in ['🧵', '📖', 'THREAD:']):
            if len(optimized[0]) < self.max_tweet_length - 10:
                optimized[0] = "🧵 " + optimized[0]
        
        # Add varied continuation elements
        continuation_elements = ['👇', '⬇️', '(continued)', '>>']
        for i in range(len(optimized) - 1):
            if len(optimized[i]) < self.max_tweet_length - 5:
                if not any(elem in optimized[i] for elem in continuation_elements):
                    # Use different continuation based on content tone
                    if any(word in optimized[i].lower() for word in ['data', 'analysis', 'study', 'research']):
                        optimized[i] += " 📊"
                    elif any(word in optimized[i].lower() for word in ['breakthrough', 'innovation', 'new']):
                        optimized[i] += " ⚡"
                    else:
                        optimized[i] += " 👇"
        
        # Create compelling final tweet
        if len(optimized) > 1:
            optimized = self._enhance_final_tweet(optimized)
        
        return optimized
    
    def _enhance_final_tweet(self, tweets: List[str]) -> List[str]:
        """Create a compelling final tweet with strong CTA"""
        last_tweet = tweets[-1]
        
        # Check if it already has a strong CTA
        cta_indicators = ['ready', 'join', 'start', 'get', 'download', 'follow', 'drop', '?']
        has_cta = any(indicator in last_tweet.lower() for indicator in cta_indicators)
        
        if not has_cta and len(last_tweet) < self.max_tweet_length - 50:
            # Add contextual CTA based on content theme
            if 'technical' in ' '.join(tweets).lower() or 'spec' in ' '.join(tweets).lower():
                cta = "\n\nReady to dive deeper? 🤿 What's your biggest technical challenge?"
            elif 'business' in ' '.join(tweets).lower() or 'ROI' in ' '.join(tweets):
                cta = "\n\nThoughts on implementation? 💭 Share your experience below!"
            elif 'future' in ' '.join(tweets).lower() or 'trend' in ' '.join(tweets).lower():
                cta = "\n\nWhat trends are you watching? 🔍 Drop your predictions!"
            else:
                cta = "\n\nWhat's your take? 💭 Share your thoughts!"
            
            if len(last_tweet + cta) <= self.max_tweet_length:
                tweets[-1] = last_tweet + cta
        
        return tweets
    
    def add_hashtags_to_thread(self, tweets: List[str], hashtags: List[str]) -> List[str]:
        """Strategically distribute hashtags to maximize reach without spam"""
        if not hashtags:
            return tweets
            
        tagged_tweets = tweets.copy()
        
        # Prioritize hashtag placement
        # 1. Last tweet gets priority
        # 2. First tweet for visibility
        # 3. Distribute remainder
        
        hashtag_string = ' '.join(hashtags)
        
        # Try last tweet first
        last_tweet = tagged_tweets[-1]
        if len(last_tweet + f"\n\n{hashtag_string}") <= self.max_tweet_length:
            tagged_tweets[-1] = last_tweet + f"\n\n{hashtag_string}"
        else:
            # Smart distribution
            priority_tweets = [len(tagged_tweets) - 1, 0]  # Last, then first
            hashtags_placed = 0
            
            for tweet_idx in priority_tweets:
                if hashtags_placed >= len(hashtags):
                    break
                    
                available_space = self.max_tweet_length - len(tagged_tweets[tweet_idx])
                hashtags_to_place = []
                
                for hashtag in hashtags[hashtags_placed:]:
                    if len(' '.join(hashtags_to_place + [hashtag])) + 2 <= available_space:
                        hashtags_to_place.append(hashtag)
                    else:
                        break
                
                if hashtags_to_place:
                    tagged_tweets[tweet_idx] += f" {' '.join(hashtags_to_place)}"
                    hashtags_placed += len(hashtags_to_place)
            
            # Distribute remaining hashtags
            remaining_hashtags = hashtags[hashtags_placed:]
            for i, hashtag in enumerate(remaining_hashtags):
                tweet_idx = (i + 1) % (len(tagged_tweets) - 1)  # Skip first and last
                if len(tagged_tweets[tweet_idx] + f" {hashtag}") <= self.max_tweet_length:
                    tagged_tweets[tweet_idx] += f" {hashtag}"
        
        return tagged_tweets
    
    def validate_thread(self, tweets: List[str]) -> Dict:
        """Enhanced validation with better feedback"""
        issues = []
        warnings = []
        MIN_LENGTH = 240
        TARGET_MIN = 250
        TARGET_MAX = 275
        
        for i, tweet in enumerate(tweets, 1):
            tweet_length = len(tweet)
            
            # Length validation
            if tweet_length > self.max_tweet_length:
                issues.append(f"Tweet {i} exceeds character limit ({tweet_length}/{self.max_tweet_length})")
            elif tweet_length < MIN_LENGTH:
                issues.append(f"Tweet {i} is too short ({tweet_length} chars). Minimum: {MIN_LENGTH}")
            elif tweet_length < TARGET_MIN:
                warnings.append(f"Tweet {i} below target ({tweet_length} chars). Target: {TARGET_MIN}-{TARGET_MAX}")
            elif tweet_length > TARGET_MAX:
                warnings.append(f"Tweet {i} above target ({tweet_length} chars). Target: {TARGET_MIN}-{TARGET_MAX}")
            
            # Quality checks
            if tweet.strip() != tweet:
                issues.append(f"Tweet {i} has leading/trailing whitespace")
                
            if '  ' in tweet:
                issues.append(f"Tweet {i} has double spaces")
            
            # Repetition check
            if i > 1:
                similarity_score = self._calculate_similarity(tweet, tweets[i-2])
                if similarity_score > 0.7:
                    warnings.append(f"Tweet {i} is very similar to tweet {i-1} (similarity: {similarity_score:.1%})")
            
            # Content quality
            if not any(keyword in tweet.lower() for keyword in ['drone', 'aerial', 'uav', 'quadcopter', 'flight', 'camera', 'autonomous']):
                warnings.append(f"Tweet {i} lacks drone-specific terminology")
        
        # Thread-level validations
        engagement_score = self.analyze_engagement_potential(tweets)['score']
        if engagement_score < 15:
            warnings.append("Low engagement potential - consider adding questions, CTAs, or emojis")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'tweet_count': len(tweets),
            'total_characters': sum(len(tweet) for tweet in tweets),
            'average_length': sum(len(tweet) for tweet in tweets) / len(tweets) if tweets else 0,
            'tweets_in_range': sum(1 for t in tweets if TARGET_MIN <= len(t) <= TARGET_MAX),
            'tweets_below_min': sum(1 for t in tweets if len(t) < MIN_LENGTH),
            'engagement_score': engagement_score
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two tweets to detect repetition"""
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def format_drone_content(self, content: str, content_type: str = "general") -> List[str]:
        """Enhanced drone-specific content formatting"""
        
        # Pre-process content to remove repetitive elements
        content = self._remove_repetitive_phrases(content)
        
        # Add drone-specific formatting based on content type
        if content_type == "tutorial":
            content = self._format_tutorial_content(content)
        elif content_type == "technical":
            content = self._format_technical_content(content)
        elif content_type == "news":
            content = self._format_news_content(content)
        elif content_type == "analysis":
            content = self._format_analysis_content(content)
        
        # Enhanced splitting with context awareness
        tweets = self.split_content(content)
        
        # Add thread numbering
        tweets = self.add_thread_numbers(tweets)
        
        # Optimize flow with better transitions
        tweets = self.optimize_thread_flow(tweets)
        
        return tweets
    
    def _remove_repetitive_phrases(self, content: str) -> str:
        """Remove repetitive phrases that make content boring"""
        repetitive_patterns = [
            r'\bKey benefits include enhanced precision and reliability\.?',
            r'\bThis technology offers improved performance\.?',
            r'\bThe system provides better results\.?',
            r'\bAdvanced features ensure optimal operation\.?'
        ]
        
        for pattern in repetitive_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\s*\.\s*\.', '.', content)
        
        return content.strip()
    
    def _format_tutorial_content(self, content: str) -> str:
        """Enhanced tutorial formatting"""
        # Add step markers with more variety
        step_emojis = ['🔧', '⚙️', '🛠️', '📐', '🎯']
        content = re.sub(r'^(\d+\.)', lambda m: f'{step_emojis[(int(m.group(1)[0])-1) % len(step_emojis)]} Step {m.group(1)}', content, flags=re.MULTILINE)
        
        # Enhanced callouts
        content = re.sub(r'(Important|Critical|Essential):', r'🚨 \1:', content, flags=re.IGNORECASE)
        content = re.sub(r'(Note|Remember):', r'📝 \1:', content, flags=re.IGNORECASE)
        content = re.sub(r'(Warning|Caution):', r'⚠️ \1:', content, flags=re.IGNORECASE)
        content = re.sub(r'(Tip|Pro tip|Hack):', r'💡 \1:', content, flags=re.IGNORECASE)
        content = re.sub(r'(Result|Outcome):', r'✅ \1:', content, flags=re.IGNORECASE)
        
        return content
    
    def _format_technical_content(self, content: str) -> str:
        """Enhanced technical formatting"""
        # Technical indicators with context
        content = re.sub(r'(Specification|Specs?|Technical details):', r'📊 \1:', content, flags=re.IGNORECASE)
        content = re.sub(r'(Performance|Speed|Velocity|Range):', r'⚡ \1:', content, flags=re.IGNORECASE)
        content = re.sub(r'(Battery|Power|Energy):', r'🔋 \1:', content, flags=re.IGNORECASE)
        content = re.sub(r'(Camera|Sensor|Imaging):', r'📷 \1:', content, flags=re.IGNORECASE)
        content = re.sub(r'(GPS|Navigation|Positioning):', r'🛰️ \1:', content, flags=re.IGNORECASE)
        content = re.sub(r'(Software|Firmware|Algorithm):', r'💻 \1:', content, flags=re.IGNORECASE)
        
        return content
    
    def _format_news_content(self, content: str) -> str:
        """Enhanced news formatting"""
        # News indicators
        content = re.sub(r'^(Breaking|News|Update|Alert):', r'🚨 \1:', content, flags=re.IGNORECASE | re.MULTILINE)
        content = re.sub(r'(Release|Launch|Announcement|Debut):', r'🚀 \1:', content, flags=re.IGNORECASE)
        content = re.sub(r'(Acquisition|Partnership|Deal):', r'🤝 \1:', content, flags=re.IGNORECASE)
        content = re.sub(r'(Regulation|Policy|Legal):', r'⚖️ \1:', content, flags=re.IGNORECASE)
        
        return content
    
    def _format_analysis_content(self, content: str) -> str:
        """Format analytical content"""
        content = re.sub(r'(Analysis|Research|Study):', r'🔍 \1:', content, flags=re.IGNORECASE)
        content = re.sub(r'(Data|Statistics|Numbers):', r'📈 \1:', content, flags=re.IGNORECASE)
        content = re.sub(r'(Trend|Pattern|Insight):', r'📊 \1:', content, flags=re.IGNORECASE)
        content = re.sub(r'(Conclusion|Finding|Result):', r'💡 \1:', content, flags=re.IGNORECASE)
        
        return content
    
    def create_promotional_thread(self, title: str, description: str, link: str, hashtags: List[str]) -> List[str]:
        """Create engaging promotional thread"""
        tweets = []
        
        # Hook with value proposition
        opener = f"🧵 THREAD: {title}\n\nAfter 5+ years building drone systems, I've cracked the code on what actually works (and what doesn't) 👇"
        tweets.append(opener)
        
        # Problem/pain point
        problem = f"Most drone operators struggle with the same issues:\n\n❌ Inconsistent performance\n❌ Complex setup processes\n❌ Limited real-world guidance\n\nSound familiar?"
        tweets.append(problem)
        
        # Solution preview
        solution = f"That's why I created this comprehensive system:\n\n✅ Step-by-step frameworks\n✅ Real deployment examples\n✅ Troubleshooting guides\n✅ Performance optimization"
        tweets.append(solution)
        
        # Social proof/results
        results = f"{description}\n\nEarly users report 3x faster deployment times and 90% fewer operational issues. The difference? Having the right playbook."
        tweets.append(results)
        
        # Call to action
        cta = f"🔗 Get instant access: {link}\n\n🎯 Complete system + templates\n📧 Exclusive updates\n🚁 Join 2,000+ drone professionals\n\nReady to level up?"
        tweets.append(cta)
        
        # Engagement closer
        closer = "What's your biggest drone challenge right now? Drop a comment below! 🚁"
        if hashtags:
            closer += f"\n\n{' '.join(hashtags)}"
        tweets.append(closer)
        
        # Add numbering and optimize
        tweets = self.add_thread_numbers(tweets)
        tweets = self.optimize_thread_flow(tweets)
        
        return tweets
    
    def analyze_engagement_potential(self, tweets: List[str]) -> Dict:
        """Enhanced engagement analysis"""
        engagement_score = 0
        factors = []
        
        total_text = ' '.join(tweets).lower()
        
        # Emojis (but not too many)
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', total_text))
        if emoji_count > 0:
            optimal_emojis = min(emoji_count, 8)  # Cap at 8 for optimal engagement
            engagement_score += optimal_emojis * 2
            factors.append(f"Emojis: +{optimal_emojis * 2}")
        
        # Questions encourage replies
        question_count = total_text.count('?')
        if question_count > 0:
            engagement_score += min(question_count * 4, 16)
            factors.append(f"Questions: +{min(question_count * 4, 16)}")
        
        # Strong opening hook
        first_tweet = tweets[0].lower()
        if any(hook in first_tweet for hook in ['thread:', 'breaking:', 'shocking:', 'nobody tells you']):
            engagement_score += 8
            factors.append("Strong hook: +8")
        
        # Call-to-action phrases
        cta_phrases = ['retweet', 'share', 'comment', 'thoughts', 'agree', 'disagree', 'experience', 'drop', 'what do you think']
        cta_count = sum(1 for phrase in cta_phrases if phrase in total_text)
        if cta_count > 0:
            engagement_score += cta_count * 3
            factors.append(f"CTAs: +{cta_count * 3}")
        
        # Thread structure
        if 3 <= len(tweets) <= 8:
            engagement_score += 6
            factors.append("Optimal thread length: +6")
        elif len(tweets) > 8:
            engagement_score += 2
            factors.append("Long thread: +2")
        
        # Hashtags (optimal range)
        hashtag_count = total_text.count('#')
        if 1 <= hashtag_count <= 5:
            engagement_score += hashtag_count * 2
            factors.append(f"Hashtags: +{hashtag_count * 2}")
        elif hashtag_count > 5:
            engagement_score += 5  # Diminishing returns
            factors.append("Hashtags (many): +5")
        
        # Personal touch
        personal_indicators = ['i', 'my', 'after years', 'in my experience', 'i learned', 'i discovered']
        if any(indicator in total_text for indicator in personal_indicators):
            engagement_score += 4
            factors.append("Personal touch: +4")
        
        # Data/numbers
        numbers = re.findall(r'\d+%|\$\d+|\d+x|\d+ years?', total_text)
        if numbers:
            engagement_score += min(len(numbers) * 2, 8)
            factors.append(f"Data points: +{min(len(numbers) * 2, 8)}")
        
        # Controversy/strong opinions
        strong_words = ['wrong', 'myth', 'mistake', 'shocking', 'surprising', 'nobody tells you']
        if any(word in total_text for word in strong_words):
            engagement_score += 5
            factors.append("Strong opinions: +5")
        
        return {
            'score': engagement_score,
            'max_score': 60,
            'percentage': min((engagement_score / 60) * 100, 100),
            'factors': factors,
            'recommendations': self._get_engagement_recommendations(tweets, engagement_score)
        }
    
    def _get_engagement_recommendations(self, tweets: List[str], current_score: int) -> List[str]:
        """Enhanced recommendations based on current score"""
        recommendations = []
        total_text = ' '.join(tweets).lower()
        
        if current_score < 20:
            recommendations.append("🚨 LOW ENGAGEMENT RISK - Consider major revisions")
        
        if '?' not in total_text:
            recommendations.append("Add questions to encourage replies")
        
        if not any(word in total_text for word in ['share', 'retweet', 'thoughts', 'drop', 'comment']):
            recommendations.append("Include call-to-action phrases")
        
        if '#' not in total_text:
            recommendations.append("Add relevant hashtags")
        
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', total_text))
        if emoji_count < 3:
            recommendations.append("Add more emojis for visual appeal")
        elif emoji_count > 10:
            recommendations.append("Consider reducing emojis to avoid spam appearance")
        
        if len(tweets) < 3:
            recommendations.append("Expand into longer thread for more engagement")
        elif len(tweets) > 10:
            recommendations.append("Consider condensing - very long threads lose engagement")
        
        # Content quality recommendations
        if not any(indicator in total_text for indicator in ['i', 'my', 'after', 'experience']):
            recommendations.append("Add personal experiences/stories for authenticity")
        
        if not re.findall(r'\d+%|\$\d+|\d+x|\d+ years?', total_text):
            recommendations.append("Include specific numbers/data for credibility")
        
        if current_score >= 40:
            recommendations.append("✅ High engagement potential - good to go!")
        elif current_score >= 25:
            recommendations.append("🟡 Moderate engagement - consider 1-2 improvements")
        
        return recommendations