# DroneAgent - AI Twitter Automation

A powerful, AI-driven tool for creating and scheduling drone-related content for Twitter.

## Features

- Generate engaging drone content ideas
- Write coherent Twitter threads
- Create and attach drone images
- Schedule posts for optimal engagement
- Track post performance and analytics

## Setup Instructions

### Environment Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your API keys:
```properties
# Twitter API Keys
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

# AI API Keys
PERPLEXITY_API_KEY=your_perplexity_api_key
GEMINI_API_KEY=your_gemini_api_key

# Image APIs (Optional)
UNSPLASH_ACCESS_KEY=your_unsplash_key
PEXELS_API_KEY=your_pexels_key
```

### Perplexity API Setup

The app currently uses local content generation due to Perplexity API issues. To enable AI-powered content:

1. Get a valid API key from [Perplexity API](https://www.perplexity.ai/api)
2. Update the `.env` file with your key
3. Test the API connection:
```bash
python test_perplexity_api.py
```
4. Modify `ideator.py` to re-enable API calls (instructions in code)

## Usage

Run the application with:
```bash
python ./DroneAgent/gui.py
```

### Content Creation Workflow

1. **Generate Ideas**: Click "Generate Ideas" to create content topics
2. **Select an Idea**: Click on an idea from the list
3. **Write Thread**: Generate a coherent Twitter thread
4. **Add Images**: Generate drone images for your tweets
5. **Preview**: Review how your thread will look
6. **Post**: Schedule or immediately post to Twitter

## Troubleshooting

If the application fails to connect to APIs:
1. Check your API keys in the `.env` file
2. Run the test script for the specific API (e.g., `test_perplexity_api.py`)
3. Look at the logs in the `logs/` directory
4. Ensure you have internet connectivity

## License

This project is licensed under the MIT License - see the LICENSE file for details.
