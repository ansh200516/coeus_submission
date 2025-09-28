# 🎯 AI Interview Nudge System

A sophisticated AI-powered interviewer that monitors coding activity in real-time and provides intelligent assistance during technical interviews.

## 🌟 Features

- **Real-time Code Monitoring**: Tracks changes in the Next.js code editor every 5 seconds
- **Intelligent Nudging**: Uses AI to detect when candidates need help and provides contextual assistance
- **Voice Interaction**: Integrates speech-to-text (RSTT) and text-to-speech (RTTS) for natural conversation
- **Sophisticated AI**: Powered by Cerebras for high-quality interviewer responses
- **Configurable Parameters**: Easily adjustable timeouts and thresholds
- **Professional Interview Experience**: Maintains appropriate interview pressure while being supportive

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Code Editor   │────│   Browser        │────│   Nudge System  │
│   (Next.js)     │    │   Monitor        │    │   (Python)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────────────────────┼─────────────────────────────────┐
                       │                                 │                                 │
                ┌──────▼──────┐              ┌───────────▼──────────┐              ┌──────▼──────┐
                │   Deepgram  │              │      Cerebras        │              │   Deepgram  │
                │     STT     │              │    AI Interviewer    │              │     TTS     │
                │   (RSTT)    │              │   (Decision Making)  │              │   (RTTS)    │
                └─────────────┘              └──────────────────────┘              └─────────────┘
```

## ⚙️ Configuration Parameters

All key parameters are configurable at the top of `nudge.py`:

### Timing Configuration
- `INACTIVITY_THRESHOLD = 25` - Seconds before triggering a nudge (default: 25s)
- `POLLING_INTERVAL = 5` - How often to check editor content (default: 5s)
- `MAX_INTERVIEW_DURATION = 120` - Maximum interview time (default: 2 minutes)

### Browser Configuration
- `BROWSER_HEADLESS = False` - Run browser in background (set to True for production)
- `REACT_APP_URL = "http://localhost:3000/coding-engine"` - Your Next.js app URL

### Audio Configuration
- `STT_MODEL = "nova-3"` - Deepgram speech-to-text model
- `TTS_MODEL = "aura-2-thalia-en"` - Deepgram text-to-speech model
- `SAMPLE_RATE = 24000` - Audio sample rate

## 🚀 Installation & Setup

### 1. Install Dependencies

```bash
cd Brain/
pip install -r requirements.txt
```

### 2. Install Chrome WebDriver

The system uses Selenium with Chrome. Install ChromeDriver:

```bash
# Option 1: Using webdriver-manager (automatic)
# Already included in requirements.txt

# Option 2: Manual installation
# Download from https://chromedriver.chromium.org/
# Add to PATH
```

### 3. Environment Setup

Create a `.env` file in the Brain directory:

```env
# Deepgram API Key (for STT and TTS)
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# Cerebras API Key (for AI interviewer)
CEREBRAS_API_KEY=your_cerebras_api_key_here
```

### 4. Start Your Next.js Code Editor

Ensure your Next.js code editor is running:

```bash
cd ../../coeus-frontend/
npm run dev
```

The default URL is `http://localhost:3000/coding-engine`. Update `REACT_APP_URL` in config.py if different.

## 🎮 Usage

### Basic Usage

```bash
cd "Brain/code interview agent/"
python main.py
```

### Advanced Usage

You can modify the configuration parameters directly in the code:

```python
# Modify in config.py
INACTIVITY_THRESHOLD = 30  # Trigger nudge after 30 seconds
MAX_INTERVIEW_DURATION = 300  # 5-minute interview
POLLING_INTERVAL = 3  # Check every 3 seconds
```

## 🤖 How It Works

### 1. Monitoring Phase
- Browser automation tracks the Monaco code editor
- Polls every 5 seconds for code changes
- Detects inactivity periods

### 2. Decision Phase
- When inactivity threshold is reached (25s default)
- Current code and context sent to Cerebras AI
- AI analyzes situation and generates appropriate response

### 3. Interaction Phase
- AI response converted to speech via Deepgram TTS
- System listens for candidate response via Deepgram STT
- Follow-up questions generated based on candidate input

### 4. Loop Continuation
- Process repeats until:
  - All test cases pass, OR
  - Maximum time limit reached (2 minutes default)

## 🎭 Interviewer Personality

The AI interviewer is designed to be:

- **Professional**: Maintains appropriate interview standards
- **Encouraging**: Supportive while maintaining challenge
- **Strategic**: Provides hints without giving away solutions
- **Insightful**: Asks probing questions about approach and thinking
- **Adaptive**: Adjusts based on candidate's progress and responses

### Sample Interactions

**Inactivity Nudge:**
> "I notice you haven't made changes for about 30 seconds. Could you walk me through your current thinking on this problem?"

**Code Analysis:**
> "I see you're using a nested loop approach. Have you considered the time complexity? Are there any edge cases you're thinking about?"

**Debugging Help:**
> "Your logic looks interesting, but I notice the tests aren't passing. Would you like to trace through your algorithm with a simple example?"

## 🔧 Customization

### Modifying Prompts

Edit the `NUDGE_PROMPTS` dictionary in `nudge.py` to customize AI responses:

```python
NUDGE_PROMPTS = {
    "initial_inactivity": "Your custom prompt here...",
    "code_analysis": "Your analysis prompt...",
    # ... more prompts
}
```

### Adding New Nudge Types

1. Add new prompt template to `NUDGE_PROMPTS`
2. Add detection logic in `_monitoring_cycle()`
3. Update context generation

### Changing Models

```python
# Use different Deepgram models
STT_MODEL = "nova-2"  # Faster STT
TTS_MODEL = "aura-2-luna-en"  # Different voice

# The system uses the same models as your tested RSTT/RTTS implementations
```

## 🐛 Troubleshooting

### Common Issues

1. **Browser Not Found**
   ```
   selenium.common.exceptions.WebDriverException
   ```
   Solution: Install ChromeDriver or update PATH

2. **Code Editor Not Detected**
   ```
   Error getting code: ...
   ```
   Solution: Verify React app is running and URL is correct

3. **Audio Issues**
   ```
   PyAudio error
   ```
   Solution: Check microphone permissions and audio devices

4. **API Errors**
   ```
   Deepgram/Cerebras API Error
   ```
   Solution: Verify API keys in `.env` file

### Debug Mode

Enable debug logging:

```python
LOG_LEVEL = logging.DEBUG
```

### Test Components Individually

```python
# Test STT only
stt = DeepgramSTT()
await stt.start_listening()

# Test TTS only  
tts = DeepgramTTS()
await tts.connect()
await tts.speak("Test message")

# Test code monitoring only
monitor = CodeEditorMonitor()
monitor.setup_browser()
print(monitor.get_current_code())
```

## 📊 System Requirements

- **Python**: 3.8+
- **Chrome Browser**: Latest version
- **Microphone**: For speech input
- **Speakers/Headphones**: For audio output
- **RAM**: 4GB+ recommended
- **Network**: Stable internet for API calls

## 🔐 Security & Privacy

- All voice data is processed by Deepgram (secure API)
- Code content is sent to Cerebras for analysis
- No data is stored locally beyond conversation history
- Browser automation is local-only

## 📈 Performance Optimization

- Adjust `POLLING_INTERVAL` based on system performance
- Use `BROWSER_HEADLESS = True` for production
- Consider running on dedicated machine for interviews
- Monitor API rate limits for high-volume usage

## 🤝 Contributing

The system is modular and extensible:

1. **Add new AI models**: Modify the AI integration classes
2. **Support other editors**: Update the monitoring logic
3. **Enhance prompts**: Improve the interviewer personality
4. **Add metrics**: Track candidate performance

## 📝 License

This system integrates with your existing RSTT/RTTS implementations and uses the same battle-tested configurations for optimal performance.

---

**Built for sophisticated technical interviews with AI-powered insights.** 🚀
