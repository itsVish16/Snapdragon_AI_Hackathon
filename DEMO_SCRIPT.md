# SnapFlow AI: 2-Minute Video Demonstration Script
**Qualcomm® AI Lab Build & Present Challenge 2026**

---

### Video Specs:
* **Duration:** 2 Minutes (120 Seconds)
* **Resolution:** 1080p / 60fps or 4K
* **Screen Layout:** Split screen showing SnapFlow Dashboard on the left and active target application (VS Code / Word / Email) on the right.

---

### Scene-by-Scene Walkthrough:

#### Scene 1: Introduction & Hardware Foundation (0:00 – 0:20)
* **Visual:** Close-up of SnapFlow Dashboard at `http://localhost:8000`. Highlight the telemetry badge showing `⚡ Compute Engine: Qualcomm Hexagon NPU (45 TOPS)`.
* **Voiceover:**  
  *"Hello! This is SnapFlow AI, an ambient ultra-low latency voice copilot engineered specifically for Snapdragon-powered HP PCs like the HP OmniBook Ultra. Cloud dictation tools leak private data and add severe latency, while running speech models on a laptop CPU drains the battery in under three hours. SnapFlow offloads speech processing entirely to Qualcomm's 45 TOPS Hexagon NPU, delivering real-time dictation at just 1.6 Watts of power."*

#### Scene 2: Live Low-Latency Flow Dictation (0:20 – 0:45)
* **Visual:** Click the glowing red/orange microphone button. The HTML5 waveform canvas pulses with audio waves. Speak naturally into the mic.
* **Spoken Phrase:**  
  *"SnapFlow delivers ambient intelligence directly to your cursor at sub-seventy millisecond latency."*
* **Visual Action:** The text appears instantly on screen. Point mouse cursor to the telemetry box: `Latency: 64.8 ms`, `RTF: 0.065x`, `Energy Saved: 1.25 J`.
* **Voiceover:**  
  *"As you speak, our circular audio buffer and adaptive VAD process audio in real-time. Text appears at your cursor faster than human reaction time—under 70 milliseconds."*

#### Scene 3: Toggleable Edge SLM Smart Polish (0:45 – 1:15)
* **Visual:** Toggle the `[ Smart Refine (Edge SLM) ]` switch to **ON**. Select the `Executive Email` pill.
* **Spoken Phrase:**  
  *"Umm hey team, so basically I think we should finalize the Snapdragon AI submission by tomorrow noon, like definitely."*
* **Visual Action:** In under 300ms, the text transforms into:
  ```text
  Subject: Update: We Should Finalize The Snapdragon AI
  Hi Team,
  I think we should finalize the Snapdragon AI submission by tomorrow noon, definitely.
  Please let me know if you have any questions.
  Best regards,
  Sent via SnapFlow AI on Snapdragon HP OmniBook
  ```
* **Voiceover:**  
  *"Notice our toggleable Edge SLM Copilot. Powered by an on-device quantized Llama model, it strips 'umms' and rambling phrases, instantaneously transforming verbal thoughts into a ready-to-send executive email or structured action items."*

#### Scene 4: OS Active Window Injection & Offline Utility (1:15 – 1:40)
* **Visual:** Open a blank VS Code editor or Notepad side-by-side. Click `Type Into Active App` (or trigger the hotkey).
* **Visual Action:** The polished text is instantly pasted directly into the cursor location in the target application.
* **Voiceover:**  
  *"With system-wide text injection, SnapFlow works anywhere you work—Notepad, Word, VS Code, or Slack. And because it runs 100% locally on the Hexagon NPU, it requires zero internet connection and guarantees complete privacy for enterprise and healthcare data."*

#### Scene 5: Conclusion & Benchmark Impact (1:40 – 2:00)
* **Visual:** Show terminal benchmark summary table from `python benchmark.py`.
* **Visual Table Highlight:** `1.6W NPU Power vs 18.5W CPU Power -> 14.5+ Hours Battery Life`.
* **Voiceover:**  
  *"In our automated benchmarks, SnapFlow achieves an incredible 12x power reduction compared to running Whisper on a standard CPU, enabling all-day ambient dictation on HP OmniBook PCs. SnapFlow AI: truly private, ultra-fast, and powered by Qualcomm Snapdragon. Thank you!"*
