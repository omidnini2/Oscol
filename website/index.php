<?php
// index.php - Simple Voice Cloning Frontend
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Voice Cloning Demo</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <header>
    <h1>Voice Cloning Demo</h1>
    <button id="theme-toggle" aria-label="Toggle Dark/Light">
      <span id="theme-icon">🌙</span>
    </button>
  </header>

  <main>
    <section>
      <h2>1. Select or Record Your Voice</h2>
      <input type="file" id="audio-upload" accept="audio/*" />
      <button id="record-btn">🎤 Record</button>
      <audio id="recording-playback" controls hidden></audio>
      <p id="record-status"></p>
      <button id="clone-btn" disabled>Clone Voice</button>
    </section>

    <section>
      <h2>2. Type Text to Read</h2>
      <textarea id="tts-text" rows="4" placeholder="متن را اینجا بنویسید…"></textarea>
      <button id="speak-btn" disabled>Speak</button>
      <audio id="tts-output" controls hidden></audio>
    </section>
  </main>

  <script src="script.js"></script>
</body>
</html>