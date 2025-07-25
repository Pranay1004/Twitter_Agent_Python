# Twitter Automation Suite - Installation & Build Guide

## 🚀 Quick Start (For End Users)

If you received the pre-built executables:

1. Extract the `TwitterAutomationSuite` folder to your desired location
2. Double-click `TwitterAgent-Launcher.exe` to start the main launcher
3. Use the launcher to open individual applications as needed
4. Configure your API keys using the API Manager first
5. Start creating content!

## 🔧 Building from Source

### Prerequisites

1. **Python 3.8+** installed on your system
2. **Git** (to clone the repository)
3. **Windows** (these scripts are designed for Windows)

### Step-by-Step Build Process

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Pranay1004/Twitter_Agent_Python
   cd "Twitter Auto\DroneAgent"
   ```

2. **Choose your build method:**

   **Option A: Simple Build (Recommended)**
   ```bash
   build_simple.bat
   ```

   **Option B: Advanced Build (All features)**
   ```bash
   build_exe.bat
   ```

   **Option C: PowerShell Build (Alternative)**
   ```powershell
   .\build_exe.ps1
   ```

3. **Wait for the build to complete** (5-10 minutes depending on your system)

4. **Find your executables** in the `dist` folder

### 📁 What Gets Built

The build process creates these executable files:

- **TwitterAgent-Launcher.exe** - Main suite launcher (START HERE)
- **TwitterAgent-Main.exe** - Complete Twitter automation interface
- **TwitterAgent-Ideator.exe** - Content ideation tool
- **TwitterAgent-APIManager.exe** - API key configuration manager

### 🎯 Applications Overview

#### 1. Main Launcher (TwitterAgent-Launcher.exe)
- Central hub for all applications
- Launch any tool with one click
- Monitor running applications
- Activity logging
- **This is the recommended starting point**

#### 2. Main Twitter Agent (TwitterAgent-Main.exe)
- Complete content generation and posting
- AI-powered thread creation
- Image generation and management
- Scheduling and automation
- Full-featured Twitter integration

#### 3. Content Ideator (TwitterAgent-Ideator.exe)
- Specialized tool for generating content ideas
- Multiple AI backend support
- Content deduplication
- Category-based idea organization

#### 4. API Manager (TwitterAgent-APIManager.exe)
- Secure API key management
- Configuration validation
- Environment setup
- **Configure this first before using other tools**

### 🔑 Configuration

1. **Set up your API keys** (Required):
   - Open API Manager
   - Enter your keys for:
     - Twitter API (Consumer Key, Consumer Secret, Access Token, Access Token Secret)  
     - OpenAI API Key (optional)
     - Gemini API Key (optional)
     - Perplexity API Key (optional)
     - OpenRouter API Key (optional)

2. **Create a `.env` file** in the same directory as the executables:
   ```
   TWITTER_CONSUMER_KEY=your_key_here
   TWITTER_CONSUMER_SECRET=your_secret_here
   TWITTER_ACCESS_TOKEN=your_token_here
   TWITTER_ACCESS_TOKEN_SECRET=your_token_secret_here
   GEMINI_API_KEY=your_gemini_key_here
   PERPLEXITY_API_KEY=your_perplexity_key_here
   OPENROUTER_API_KEY=your_openrouter_key_here
   ```

### 📦 Distribution

The built applications are completely portable:

1. **Copy the entire `dist` folder** to any Windows machine
2. **No Python installation required** on target machines
3. **All dependencies included** in the executables
4. **Run from any location** - no installation needed

### 🛠️ Troubleshooting

**Build Issues:**
- Ensure Python 3.8+ is installed and in PATH
- Install missing packages: `pip install -r requirements.txt`
- Clear build cache: Delete `build` and `dist` folders before rebuilding

**Runtime Issues:**
- Ensure all API keys are properly configured
- Check that `.env` file is in the same directory as executables
- Run from Command Prompt to see error messages: `TwitterAgent-Main.exe`

**Performance:**
- First launch may be slower as Windows scans the executable
- Subsequent launches will be faster
- Large executables are normal (includes all dependencies)

### 🔒 Security Notes

- API keys are stored locally in the `.env` file
- No data is transmitted except to configured API services
- All processing happens locally on your machine
- Built executables include only necessary dependencies

### 📱 System Requirements

- **OS:** Windows 10/11 (64-bit recommended)
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 200MB for executables + space for generated content
- **Internet:** Required for API calls and content generation

### 📞 Support

- **GitHub Issues:** https://github.com/Pranay1004/Twitter_Agent_Python/issues
- **Documentation:** Check README files in the repository
- **Updates:** Watch the repository for new releases

### 🎉 Quick Test

After building:

1. Run `TwitterAgent-Launcher.exe`
2. Click "API Manager" and configure at least Twitter API keys
3. Click "Main Twitter Agent" 
4. Generate some test content
5. Check that everything works before distributing

---

**Enjoy your automated Twitter content creation! 🚁✨**
