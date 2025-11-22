# Voice Tester Guide - Developer Playground

**Last Updated:** November 2025  
**Location:** Developer Playground → Voice Tester Tab

---

## Overview

The Voice Tester allows you to test the Text-to-Speech (TTS) functionality in isolation. This tool is useful for:
- Testing different emotional tones
- Verifying TTS engine functionality
- Debugging voice synthesis issues
- Experimenting with different text inputs

---

## Prerequisites

### 1. Backend Dependencies

Ensure TTS libraries are installed:

```bash
pip install TTS pyttsx3
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

**Note:** Coqui TTS will download ~1GB model files on first use (this happens automatically).

### 2. Backend Server

Ensure the backend API is running:

```bash
# Check if backend is running on port 8005
curl http://localhost:8005/health
```

If not running, start it:
```bash
python main.py
# or
uvicorn tradingagents.api.main:app --port 8005
```

### 3. Frontend Access

Open the Developer Playground:
- Navigate to: `http://localhost:3005` (or your frontend URL)
- Click on the **"Voice Tester"** tab

---

## How to Use the Voice Tester

### Step-by-Step Testing Process

#### 1. **Enter Text to Synthesize**

- The textarea is pre-filled with: `"Hello, I am Eddie. How can I help you today?"`
- You can:
  - Keep the default text
  - Type your own text
  - Paste longer text for testing

**Example Test Texts:**
```
Short: "Hello, I am Eddie."
Medium: "Apple Inc. is currently trading at $175.50, up 2.3% today."
Long: "Based on my analysis, Apple Inc. shows strong fundamentals with a P/E ratio of 28.5 and revenue growth of 8% year-over-year. The technical indicators suggest a bullish trend, but I recommend monitoring the support level at $170."
```

#### 2. **Select Emotional Tone**

Choose from 5 available tones:

- **Professional** (default)
  - Standard analytical tone
  - Clear and precise
  - Best for: General market analysis, technical explanations

- **Calm**
  - Reassuring, slow, gentle
  - Best for: Stressed users, market crashes, negative news

- **Energetic**
  - Enthusiastic but cautionary
  - Best for: All-time highs, exciting news, positive momentum

- **Technical**
  - Precise, methodical
  - Best for: System diagnostics, technical deep-dives

- **Reassuring**
  - Supportive, empathetic
  - Best for: User concerns, uncertainty, guidance

#### 3. **Synthesize Speech**

- Click the **"Synthesize Speech"** button
- The button will show a loading spinner while processing
- Processing time:
  - **First synthesis**: 5-10 seconds (model loading)
  - **Subsequent synthesis**: 1-3 seconds

#### 4. **Listen to Audio**

- Once synthesis completes, an audio player appears below
- The audio will **auto-play** when ready
- Use the audio controls to:
  - Play/Pause
  - Adjust volume
  - Seek through the audio
  - Download the audio (browser-dependent)

---

## Testing Scenarios

### Scenario 1: Basic Functionality Test

**Purpose:** Verify TTS engine is working

1. Use default text: `"Hello, I am Eddie. How can I help you today?"`
2. Select tone: **Professional**
3. Click **Synthesize Speech**
4. **Expected:** Audio plays successfully with clear speech

---

### Scenario 2: Tone Comparison Test

**Purpose:** Compare different emotional tones

1. Use the same text for all tests: `"The market is showing strong momentum today."`
2. Test each tone sequentially:
   - Professional
   - Calm
   - Energetic
   - Technical
   - Reassuring
3. **Expected:** Noticeable differences in:
   - Speech pace (Calm = slower, Energetic = faster)
   - Voice inflection
   - Overall delivery style

---

### Scenario 3: Long Text Test

**Purpose:** Test synthesis with longer content

1. Enter a long paragraph (200+ words)
2. Select tone: **Professional**
3. Click **Synthesize Speech**
4. **Expected:** 
   - Synthesis completes successfully
   - Audio duration matches text length
   - No truncation or errors

---

### Scenario 4: Special Characters & Numbers

**Purpose:** Test handling of special content

1. Enter text with:
   - Numbers: `"Apple is trading at $175.50, up 2.3%"`
   - Symbols: `"The P/E ratio is 28.5x"`
   - Abbreviations: `"AAPL, MSFT, and NVDA are tech stocks"`
2. **Expected:** All content is synthesized correctly

---

### Scenario 5: Empty Text Handling

**Purpose:** Test error handling

1. Clear the text field (leave empty)
2. Click **Synthesize Speech**
3. **Expected:** Button is disabled or shows error (current implementation may allow this)

---

### Scenario 6: API Connection Test

**Purpose:** Verify backend connectivity

1. Check browser console (F12 → Console tab)
2. Click **Synthesize Speech**
3. **Expected:** 
   - No network errors
   - Successful API call to `/voice/synthesize`
   - Response status: 200 OK

---

## Troubleshooting

### Issue: "Failed to synthesize speech" Error

**Possible Causes:**
1. TTS libraries not installed
2. Backend not running
3. Model files not downloaded

**Solutions:**
```bash
# 1. Install TTS libraries
pip install TTS pyttsx3

# 2. Verify backend is running
curl http://localhost:8005/health

# 3. Check backend logs for TTS initialization errors
# Look for: "TTS engine initialized successfully"
```

---

### Issue: "Error connecting to TTS service"

**Possible Causes:**
1. Backend API not accessible
2. Wrong port number
3. CORS issues
4. API key authentication required

**Solutions:**
1. Verify backend URL in browser console
2. Check if API key is set in localStorage:
   ```javascript
   localStorage.getItem("api_key")
   ```
3. Check backend logs for connection errors

---

### Issue: No Audio Playback

**Possible Causes:**
1. Browser audio permissions
2. Audio format not supported
3. Base64 encoding issue

**Solutions:**
1. Check browser console for audio errors
2. Verify audio element is created:
   ```javascript
   // In browser console
   document.querySelector('audio')
   ```
3. Check if `audioUrl` state is set correctly

---

### Issue: Slow Synthesis

**Expected Behavior:**
- **First synthesis**: 5-10 seconds (normal - model loading)
- **Subsequent synthesis**: 1-3 seconds

**If consistently slow:**
- Check CPU usage (TTS uses CPU by default)
- Consider GPU acceleration (requires CUDA setup)
- Check backend logs for performance warnings

---

### Issue: Audio Quality Issues

**Possible Causes:**
1. Using fallback TTS (pyttsx3) instead of Coqui
2. Model not fully loaded
3. Audio format issues

**Solutions:**
1. Check backend logs for which TTS engine is used:
   - `"Initializing TTS model: tts_models/multilingual/multi-dataset/xtts_v2"` (Coqui)
   - `"Using fallback TTS engine"` (pyttsx3)
2. Verify Coqui TTS is installed: `pip show TTS`
3. Check model download status in logs

---

## API Testing (Alternative Method)

You can also test the TTS endpoint directly via API:

### Using cURL

```bash
# Basic test
curl -X POST "http://localhost:8005/voice/synthesize?text=Hello%20World&tone=professional&return_base64=true" \
  -H "Content-Type: application/json" \
  --output response.json

# Extract and play audio (macOS)
cat response.json | jq -r '.audio_base64' | base64 -d > audio.wav
afplay audio.wav
```

### Using Python

```python
import requests
import base64

response = requests.post(
    "http://localhost:8005/voice/synthesize",
    params={
        "text": "Hello, I am Eddie",
        "tone": "professional",
        "return_base64": True
    }
)

data = response.json()
audio_b64 = data["audio_base64"]
audio_bytes = base64.b64decode(audio_b64)

with open("test.wav", "wb") as f:
    f.write(audio_bytes)
```

---

## Expected Behavior Checklist

When testing, verify:

- [ ] Text input accepts and displays text correctly
- [ ] Tone dropdown shows all 5 options
- [ ] Button shows loading state during synthesis
- [ ] Success toast appears: "Speech synthesized"
- [ ] Audio player appears below the button
- [ ] Audio auto-plays when ready
- [ ] Audio controls work (play, pause, volume)
- [ ] Different tones produce different audio characteristics
- [ ] Long text synthesizes without errors
- [ ] Error messages appear for connection issues
- [ ] Browser console shows no errors

---

## Technical Details

### Frontend Implementation

**File:** `web-app/components/DevToolsView.tsx`

**Key Functions:**
- `synthesizeSpeech()` (line 104): Handles API call and audio creation
- State management: `ttsText`, `ttsTone`, `ttsLoading`, `audioUrl`

**API Call:**
```typescript
POST /voice/synthesize?text={text}&tone={tone}&return_base64=true
```

**Response Format:**
```json
{
  "audio_base64": "UklGRiQAAABXQVZFZm10...",
  "format": "wav"
}
```

### Backend Implementation

**Endpoint:** `POST /voice/synthesize`  
**Location:** `tradingagents/api/main.py` (line 448)

**Parameters:**
- `text` (required): Text to synthesize
- `tone` (optional): Emotional tone (default: "professional")
- `return_base64` (optional): Return base64 string (default: false)

**TTS Engine:** `tradingagents/voice/tts_engine.py`
- Primary: Coqui XTTS v2
- Fallback: pyttsx3 (system TTS)

---

## Best Practices

1. **Start Simple**: Begin with short text and default tone
2. **Test Incrementally**: Test one tone at a time
3. **Check Logs**: Monitor backend logs for errors
4. **Verify Audio**: Always listen to the output
5. **Test Edge Cases**: Empty text, special characters, long text
6. **Compare Tones**: Use the same text to compare tones effectively

---

## Related Documentation

- [EDDIE_V2_VOICE_INTEGRATION_COMPLETE.md](./EDDIE_V2_VOICE_INTEGRATION_COMPLETE.md) - Full voice integration details
- [EDDIE_V2_VOICE_TTS_SUMMARY.md](./EDDIE_V2_VOICE_TTS_SUMMARY.md) - TTS implementation summary
- [EDDIE_V2_TESTING_GUIDE.md](./EDDIE_V2_TESTING_GUIDE.md) - General testing guide

---

## Support

If you encounter issues not covered here:

1. Check backend logs: `logs/backend.log`
2. Check browser console: F12 → Console
3. Verify dependencies: `pip list | grep -i tts`
4. Test API directly: Use cURL or Python examples above

---

**Happy Testing! 🎙️**

