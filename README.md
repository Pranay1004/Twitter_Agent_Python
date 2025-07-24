<<<<<<< HEAD

# DroneAgent Twitter Automation

A robust, AI-powered agent for generating, visualizing, and posting Twitter/X threads using Gemini, Perplexity, Unsplash, Pexels, Bitly, and Stability AI APIs. Includes secure API key management and extensibility for new APIs.

## Features
- Generate unique Twitter threads and images
- Schedule and post threads automatically
- Manage API keys securely via GUI
- OAuth 2.0 authentication for X.com (Twitter)
- Easily add new APIs with comments for documentation

## Setup

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Configure API Keys
- All API keys and secrets are stored in the `.env` file (excluded from git).
- Use the API Key Manager GUI to add or update credentials:
  ```powershell
  python DroneAgent\gui_api_manager.py
  ```
- For each API, use the standardized key name suggested by the GUI (e.g., `GEMINI_API_KEY`, `UNSPLASH_ACCESS_KEY`).
- To add a new API (not core), use the GUI and add an optional comment describing its purpose. Example:
  ```properties
  # Weather API for drone flight planning
  WEATHER_API_KEY=your_weather_api_key
  ```

### 3. Run the Agent
- To launch the main application:
  ```powershell
  python DroneAgent\gui.py
  ```
- For CLI usage or testing, use the provided test scripts (e.g., `python test_image_generation.py`).

## Usage Workflow
1. **Generate Ideas:** Use the GUI to create content topics.
2. **Write Thread:** Generate a coherent Twitter thread using AI.
3. **Add Images:** Generate and attach images to your tweets.
4. **Preview:** Review your thread before posting.
5. **Post/Schedule:** Post immediately or schedule for later.
6. **API Key Management:** Add/update API keys via the GUI, with comments for documentation.

## Extending with New APIs
- Open the API Key Manager GUI.
- Enter the API key name (use uppercase and underscores, e.g., `NEWAPI_API_KEY`).
- Enter the API key value.
- Optionally, add a comment describing the API's purpose.
- The key and comment will be added to `.env` and available for use in code.

## Troubleshooting
- If the application fails to connect to APIs:
  1. Check your API keys in `.env`.
  2. Use the API Key Manager GUI to update keys.
  3. Run the relevant test script (e.g., `python test_gemini_api_fixed.py`).
  4. Check logs in the `logs/` directory.
  5. Ensure internet connectivity.

## Security
- `.env` and sensitive files are excluded from git by `.gitignore`.
- No credentials are hardcoded in code.
- Use the API Key Manager GUI for all credential management.

## License
MIT License. See LICENSE file for details.


## Usage Workflow
1. **Generate Ideas:** Use the GUI to create content topics.
2. **Write Thread:** Generate a coherent Twitter thread using AI.
3. **Add Images:** Generate and attach images to your tweets.
4. **Preview:** Review your thread before posting.
5. **Post/Schedule:** Post immediately or schedule for later.
6. **API Key Management:** Add/update API keys via the GUI, with comments for documentation.

## Troubleshooting
- If the application fails to connect to APIs:
  1. Check your API keys in `.env`.
  2. Use the API Key Manager GUI to update keys.
  3. Run the relevant test script (e.g., `python test_gemini_api_fixed.py`).
  4. Check logs in the `logs/` directory.
  5. Ensure internet connectivity.

## License
MIT License. See LICENSE file for details.
=======
# Twitter_Agent_Python
Twitter_Agent_Python
>>>>>>> 1c9685cf270f3b51b2714afbe388c69574dfdccc
