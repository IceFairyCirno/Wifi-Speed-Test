import requests
import time
import os
import tkinter as tk
from datetime import datetime
import sys

def test_download(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'
        }
        start_time = time.time()
        response = requests.get(url, stream=True, headers=headers, timeout=120)
        response.raise_for_status()
        filename = "100MB.bin"
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        end_time = time.time()  # Record end time
        duration = end_time - start_time
        result = round((800_000_000/duration)/1_000_000, 2)
        os.remove(filename)
        return result
    except Exception as e:
        print(f"Error downloading {url}: {type(e).__name__} - {str(e)}")
        return f"Error downloading {url}: {type(e).__name__} - {str(e)}"

def test_upload(url):
    try:
        upload_data = os.urandom(10 * 1024 * 1024)  # 10 MB
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }   
        start_time = time.time()
        response = requests.post(url, data=upload_data, headers=headers, timeout=120)
        response.raise_for_status()
        duration = time.time() - start_time
        result = round((len(upload_data)*8/duration)/1_000_000, 2)
        return result
    except Exception as e:
        print(f"Error uploading {url}: {type(e).__name__} - {str(e)}")
        return f"Error uploading {url}: {type(e).__name__} - {str(e)}"

class SpeedTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speed Test App")
        self.root.geometry("400x200")

        self.set_icon()
        
        self.status = False
        self.test_running = False

        self.status_label = tk.Label(root, text="Stopped", font=('Arial', 16))
        self.status_label.pack(pady=30)
        self.dots = 0

        self.button = tk.Button(root, text="Start Testing", font=('Arial', 12), command=self.switch)
        self.button.pack(pady=5)
    
    def set_icon(self):
        if getattr(sys, "frozen", False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, "Assets", "speed_test.ico")
        try:
            self.root.iconbitmap(icon_path)
        except tk.TclError as e:
            print(f"Failed to set icon: {e}. Ensure Assets/speed_test.ico exists.")

    def switch(self):
        if not self.status:
            self.status = True
            self.test_running = True
            self.status_label.config(text="Running...")
            self.button.config(text="Stop Testing")
            self.run_test()  # Start the first test
        else:
            self.status = False
            self.test_running = False
            self.status_label.config(text="Stopped")
            self.button.config(text="Start Testing")

            date = datetime.now().date()
            time = datetime.now().time()

            with open(f"{date}-WIFI-Speed.log", 'a') as file:
                file.write(f"{time}: Program Stopped by User\n")

    def run_test(self):
        if not self.test_running:
            return  # Exit if test was stopped

        try:
            url = "https://sin-speed.hetzner.com/100MB.bin"
            url2 = "https://httpbin.org/post"
            result = test_download(url)
            result2 = test_upload(url2)
            date = datetime.now().date()
            time = datetime.now().time()
            
            with open(f"{date}-WIFI-Speed.log", 'a') as file:
                file.write(f"{time}: Download: {result} Mbps, Upload: {result2} Mbps\n")

        except Exception as e:
            date = datetime.now().date()
            time = datetime.now().time()
            with open(f"{date}-WIFI-Speed.log", 'a') as file:
                file.write(f"{time}: Error: {type(e).__name__} - {str(e)}\n")
            self.status = False
            self.status_label.config(text="Retrying in 5 miniutes")
            if self.test_running:
                self.root.after(300000, self.run_test)  # Schedule retry after 5 minutes
            return

        # Schedule the next test after 300 seconds (5 minutes)
        if self.test_running:
            self.root.after(300000, self.run_test)  # 300,000 ms = 300 s

def main():
    root = tk.Tk()
    app = SpeedTestApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()