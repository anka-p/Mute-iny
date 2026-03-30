# Mute-iny
**The Ad-Assassin for LG WebOS TVs.**

Mute-iny is a Python-based "listener" designed to run on an old MacBook. It monitors ambient audio via the microphone; when it detects a sudden spike in volume (typical of loud TV commercials), it sends a network command to silence your LG TV.

## Prerequisites
* **LG Smart TV** (WebOS) connected to the same Wi-Fi as your Mac.
* **Python 3.9+** installed on your MacBook.
* **Network IP Control** enabled on your TV (Settings > Connection).

## SetUp

1. **Clone & Install**
   ```bash
   pip install -r requirements.txt 
   ```
2. Find your TV's IP Address 
- Press Settings > All Settings.
- Go to General.
- Select Network.
- Select your current connection (Wi-Fi or Wired).
- Look for Other Network Settings or Advanced Settings to see the IP.