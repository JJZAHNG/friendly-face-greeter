# Friendly-Face-Greeter

A Python application that uses your webcam to detect and recognize faces from a pre‑loaded library, then greets known individuals with randomized friendly phrases via text‑to‑speech.

## 🚀 Features

- **Real‑time face detection & recognition**
   Uses `face_recognition` on live webcam feed.
- **Customizable greetings**
   Randomly selects from a list of small‑talk phrases each time.
- **Non‑blocking TTS**
   Offloads speech synthesis to a background thread, keeping the video smooth.
- **macOS `say` integration**
   Uses the built‑in `say` command with the “Kathy” voice for warm, natural speech.
- **Simple setup**
   Just drop your labeled JPG/PNG files into `known_faces/`, install dependencies, and run.

## 📁 Repository Structure

```bash
friendly-face-greeter/
├── known_faces/            # Place your known face images here (e.g. Alice.jpg)
├── requirements.txt        # Python dependencies
├── face_greeting.py        # Main application script
└── README.md               # This documentation
```

## 💻 Requirements

- Python 3.7 or newer
- macOS (for the `say` TTS integration)
- Or Windows/Linux with a compatible TTS fallback (see **Alternatives** below)

### Python packages

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:

```bash
opencv-python
face_recognition
numpy
```

## ⚙️ Installation & Usage

1. **Clone the repo**

   ```bash
   git clone https://github.com/your‑username/friendly-face-greeter.git
   cd friendly-face-greeter
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Add your known faces**

   - Put `Name.jpg` or `Name.png` into the `known_faces/` folder.
   - The filename (without extension) will be used as the person’s name.

4. **Run the application**

   ```bash
   python face_greeting.py
   ```

5. **Controls**

   - Press **q** in the video window to quit.

## 🛠 Configuration

- **Greeting interval**
   By default, each person is re‑greeted every 60 seconds. To change, edit:

  ```python
  GREET_INTERVAL = 60  # seconds
  ```

- **Small‑talk phrases**
   Customize the list in `face_greeting.py`:

  ```python
  small_talk_phrases = [
      "How are you today?",
      "Nice to see you!",
      ...
  ]
  ```

- **Voice & speed**
   Currently uses macOS’s `say -v Kathy`. To adjust speed or voice, modify the `subprocess.run` call in the TTS worker.

## ⚙️ Alternatives for Non‑macOS

If you’re on Windows or Linux and don’t have the `say` command, you can switch back to `pyttsx3`:

1. Install:

   ```bash
   pip install pyttsx3
   ```

2. Replace the TTS section in `face_greeting.py` with:

   ```Python
   import pyttsx3
   engine = pyttsx3.init()
   engine.setProperty('rate', 120)
   engine.setProperty('voice', '<your‑preferred‑voice‑id>')
   engine.say(msg); engine.runAndWait()
   ```

## 🤝 Contributing

1. Fork this repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request — all contributions are welcome!

## 📝 License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.