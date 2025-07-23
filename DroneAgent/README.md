# 🚁 DroneAgent - AI-Powered Twitter Automation

**DroneAgent** is an intelligent AI agent that builds an audience and brand on Twitter by automatically posting engaging drone-related content twice daily. It combines content ideation, writing, visualization, and scheduling to create a comprehensive Twitter automation solution.

## 🛠 Features

- **🧠 AI-Powered Content Creation** - Uses multiple AI models (Perplexity, Gemini, GPT-4, Claude) for ideation
- **✍️ Smart Thread Writing** - Automatically formats content into engaging Twitter threads
- **🖼️ Image Integration** - Fetches relevant drone images from Unsplash/Pexels with proper attribution
- **⏰ Intelligent Scheduling** - Posts at optimal times (10am & 7pm IST) for global engagement
- **🖥️ GUI + CLI Interface** - PyQt5 desktop app with command-line fallback
- **📊 Analytics & Backtesting** - Track performance and posting history
- **🔄 Automated Posting** - Background scheduling with smart content rotation

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd DroneAgent

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

1. **Copy `.env.example` to `.env`** and add your API keys:
```env
# Twitter API Keys
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here

# AI API Keys (at least one required)
PERPLEXITY_API_KEY=your_perplexity_key_here
GEMINI_API_KEY=your_gemini_key_here

# Image APIs (optional)
UNSPLASH_ACCESS_KEY=your_unsplash_key_here
PEXELS_API_KEY=your_pexels_key_here
```

2. **Update `config.yaml`** with your preferences:
```yaml
app:
  debug: false

scheduling:
  timezone: "Asia/Kolkata"
  post_times: ["10:00", "19:00"]

ai_models:
  preferred: "perplexity"
  fallback: "gemini"

posting:
  auto_post: false  # Set to true for automated posting
  dry_run: true     # Set to false for actual posting
```

### 3. Usage

#### GUI Mode (Recommended)
```bash
python main.py --gui
```

#### CLI Mode
```bash
# Generate content ideas
python main.py --ideate

# Write a thread about a specific topic
python main.py --write "FPV drone racing"

# Post immediately
python main.py --post-now

# Setup scheduled posting
python main.py --schedule

# View analytics
python main.py --backtest
```

## 📁 Project Structure

```
DroneAgent/
├── main.py                 # CLI entry point
├── gui.py                  # PyQt5 GUI interface
├── config.yaml             # Configuration settings
├── .env                    # API keys and secrets
│
├── agent/
│   ├── ideator.py          # AI-powered content ideation
│   ├── writer.py           # Thread writing and formatting
│   ├── visualizer.py       # Image fetching and processing
│   └── scheduler.py        # Post scheduling logic
│
├── utils/
│   ├── logger.py           # Centralized logging
│   ├── poster.py           # Twitter API integration
│   └── thread_builder.py   # Thread formatting utilities
│
├── data/
│   ├── history.json        # Posting history and analytics
│   └── images/             # Downloaded/cached images
│
├── logs/                   # Application logs
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔑 API Keys Required

### Twitter API v2 (Required)
1. Apply for Twitter Developer Account: https://developer.twitter.com
2. Create a new app and generate API keys
3. Ensure you have v2 API access

### AI APIs (At least one required)
- **Perplexity Pro** (Recommended): https://www.perplexity.ai/pro
- **Google Gemini**: https://ai.google.dev
- **OpenAI**: https://openai.com/api
- **Anthropic Claude**: https://www.anthropic.com

### Image APIs (Optional)
- **Unsplash**: https://unsplash.com/developers
- **Pexels**: https://www.pexels.com/api

## 🎯 Content Strategy

DroneAgent creates diverse content including:

- **Tutorial Threads** - DIY builds, setup guides, troubleshooting
- **Technology Deep-Dives** - Latest innovations, comparisons, reviews
- **Industry Analysis** - Commercial applications, market trends
- **Historical Content** - Drone evolution, milestones, pioneers
- **Promotional Posts** - Personal brand building (customizable)

### Sample Content Types

1. **"Building Your First Racing Drone"** - 7-tweet tutorial thread
2. **"Drone Tech Evolution 2015-2025"** - Historical timeline with images
3. **"Commercial Drone ROI Analysis"** - Business-focused insights
4. **"FPV Racing: Pro Tips"** - Expert techniques and advice

## ⏰ Scheduling Strategy

**Optimal Posting Times (IST):**
- **10:00 AM IST** → Targets US evening (6:30 PM EST) + EU night
- **07:00 PM IST** → Targets US morning (9:30 AM EST) + EU afternoon

This schedule maximizes global reach across major English-speaking markets.

## 🖥️ GUI Features

The PyQt5 interface provides:

- **Content Creation Tab**
  - AI model selection
  - One-click idea generation
  - Thread writing and preview
  - Image integration
  - Instant posting

- **Analytics Tab**
  - Posting history
  - Performance metrics
  - Engagement trends

- **Settings Tab**
  - Scheduling configuration
  - API status monitoring
  - Auto-posting controls

## 📊 Analytics & Backtesting

Track your content performance:

```bash
python main.py --backtest
```

Provides:
- Total posts and engagement
- Posting frequency analysis
- Character count statistics
- Best performing content types
- Visual charts and graphs

## 🛡️ Safety Features

- **Dry Run Mode** - Test without posting
- **Rate Limiting** - Respects Twitter API limits
- **Error Handling** - Graceful failure recovery
- **Content Validation** - Character limits and format checks
- **Manual Override** - GUI approval for all posts

## 🔧 Customization

### Adding New Content Types
Edit `agent/writer.py` to add new content templates:

```python
def _generate_custom_content(self, topic: str, max_tweets: int) -> Dict:
    # Your custom content logic here
    pass
```

### Custom Posting Schedule
Modify `config.yaml`:

```yaml
scheduling:
  post_times: ["08:00", "14:00", "20:00"]  # Custom times
```

### Personal Branding
Update promotional content in `agent/writer.py`:

```python
def create_promotional_thread(self) -> Dict:
    # Customize your promotional content
    pass
```

## 🐛 Troubleshooting

### Common Issues

1. **Twitter API Errors**
   - Verify all API keys are correct
   - Check API permissions and access levels
   - Ensure rate limits aren't exceeded

2. **AI API Failures**
   - Check API key validity
   - Verify account credits/quota
   - Try fallback models

3. **Image Download Issues**
   - Check Unsplash/Pexels API keys
   - Verify internet connection
   - Review image URL accessibility

### Debug Mode
Enable debug logging in `config.yaml`:

```yaml
app:
  debug: true

logging:
  level: "DEBUG"
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Support

- **Issues**: GitHub Issues page
- **Documentation**: This README + code comments
- **Community**: Twitter @droneagent_ai

## 🚀 Roadmap

- [ ] **v1.1** - Advanced analytics dashboard
- [ ] **v1.2** - Multi-platform support (LinkedIn, Instagram)
- [ ] **v1.3** - AI-generated images with DALL-E/Midjourney
- [ ] **v1.4** - Engagement automation (replies, likes)
- [ ] **v1.5** - Team collaboration features

---

**Ready to dominate the drone Twitter space? 🚁**

Start with `python main.py --gui` and watch your audience grow!

*Built with ❤️ for the drone community*
