import json
import sys
import time
import numpy as np
import sounddevice as sd
from pywebostv.connection import WebOSClient
from pywebostv.controls import MediaControl

class MuteIny:
    def __init__(self, config_path='config.json'):
        self.config = self._load_config(config_path)
        self.client = WebOSClient(self.config['TV_IP'])
        self.__THRESHOLD__ = self.config.get("THRESHOLD", .5)
        self.__MUTE_DURATION__ = self.config.get("AD_DURATION", 3)
        self.media = None
        self.is_muted = False
        self.mute_end_time = 0
        self.vol_history = []

    def _load_config(self, path):
        """Private method to handle configuration."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config missing! Copy config.json.example to {path}")
            sys.exit(1)

    def connect(self):
        """Handles the 'Always-Register' logic you requested."""
        self.client.connect()
        # Passing an empty dict forces the 'Allow' popup every time
        for status in self.client.register(self.config["client_key"]):
            if status == WebOSClient.PROMPTED:
                print("\n[!] Check TV: Click 'Allow' or 'Yes' now!")
            elif status == WebOSClient.REGISTERED:
                print("\n[+] Mute-iny Authenticated.")
        self.media = MediaControl(self.client)

    def draw_graph(self, current_vol, avg_vol):
        """Prints a reactive, non-flickering volume meter."""
        width = 40
        # Scale current volume to bar width
        bar_len = int(min(current_vol, 1.5) * (width / 1.5))
        thresh_pos = int(self.__THRESHOLD__ * (width / 1.5))
        
        # Construct the bar string
        bar_chars = []
        for i in range(width):
            if i == thresh_pos:
                bar_chars.append("|") # The Tripwire
            elif i < bar_len:
                bar_chars.append("█") # Active Volume
            else:
                bar_chars.append("░") # Background
                
        bar = "".join(bar_chars)
        status = "[MUTED]" if self.is_muted else "[LIVE ]"
        
        # \r returns cursor to start
        # \033[K clears the rest of the line to prevent 'ghosting'
        output = f"\r{status} {bar} Vol: {current_vol:.2f} (Avg: {avg_vol:.2f}) \033[K"
        
        sys.stdout.write(output)

    def process_pulse(self):
        """The 1-second decision engine."""
        if not self.vol_history:
            return

        avg_vol = sum(self.vol_history) / len(self.vol_history)
        self.draw_graph(self.vol_history[-1], avg_vol)

        now = time.time()
        if self.is_muted:
            if now > self.mute_end_time:
                self.media.mute(False)
                self.is_muted = False
                print("\n[+] Ad over. Unmuting.")
        elif avg_vol > self.__THRESHOLD__:
            self.media.mute(True)
            self.is_muted = True
            self.mute_end_time = now + self.__MUTE_DURATION__
            print(f"\n Muting (Avg: {avg_vol:.2f})")

        self.vol_history = [] # Reset for next 1-sec pulse

    def audio_callback(self, indata, *args):
        """Rapidly collects data in the background."""
        volume = np.linalg.norm(indata) * 10
        self.vol_history.append(volume)

    def run(self):
        """The main execution loop."""
        self.connect()
        with sd.InputStream(callback=self.audio_callback):
            while True:
                self.process_pulse()
                time.sleep(1.0) # The 1-second pulse you wanted

if __name__ == "__main__":
    # This ensures the code only runs if the script is executed directly
    bot = MuteIny()
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\nAborted.")