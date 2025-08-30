import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import time
import threading
import schedule
from obswebsocket import obsws, requests, exceptions
import pyautogui
import psutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse, parse_qs
from pywinauto import Application, Desktop
import os
class MeetingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Meeting + OBS + Zoom Launcher")
        self.root.geometry("600x750")
        self.ws = None
        self.video_path = None
        self.zoom_driver = None
        self.zoom_joined = False
        self.mic_muted = False
        self.video_off = False
        
        self.zoom_app = None
        self.zoom_window = None

        # ===== Zoom Link & Options =====
        tk.Label(root, text="Zoom Meeting URL:").pack(pady=5)
        self.zoom_entry = tk.Entry(root, width=50)
        self.zoom_entry.pack(pady=5)

        tk.Label(root, text="Initial Audio/Video Settings:").pack(pady=(10, 5))
        
        audio_frame = tk.Frame(root)
        audio_frame.pack(pady=2)
        self.mic_var = tk.BooleanVar(value=True)
        tk.Checkbutton(audio_frame, text="Start with Mic ON", variable=self.mic_var).pack(side=tk.LEFT)
        
        video_frame = tk.Frame(root)
        video_frame.pack(pady=2)
        self.camera_var = tk.BooleanVar(value=True)
        tk.Checkbutton(video_frame, text="Start with Camera ON", variable=self.camera_var, command=self.toggle_obs_options).pack(side=tk.LEFT)

        # ===== OBS Options =====
        tk.Label(root, text="Select Video File:").pack(pady=5)
        self.video_button = tk.Button(root, text="Select Video", command=self.select_video)
        self.video_button.pack(pady=5)

        tk.Label(root, text="Join Meeting: Now or Scheduled?").pack(pady=5)
        self.schedule_var = tk.StringVar(value="now")
        tk.Radiobutton(root, text="Now", variable=self.schedule_var, value="now", command=self.toggle_time_entry).pack()
        tk.Radiobutton(root, text="Scheduled", variable=self.schedule_var, value="scheduled", command=self.toggle_time_entry).pack()

        tk.Label(root, text="Scheduled Time (HH:MM):").pack(pady=5)
        self.time_entry = tk.Entry(root, width=10)
        self.time_entry.pack(pady=5)

        self.start_btn = tk.Button(root, text="Start Meeting Flow", command=self.start_workflow, 
                                  bg="#0078d4", fg="white", font=("Arial", 12, "bold"))
        self.start_btn.pack(pady=20)

        tk.Label(root, text="Status:").pack(pady=(10, 2))
        self.status_label = tk.Label(root, text="Ready", bg="lightgray", fg="black", 
                                   font=("Arial", 10, "bold"), relief="sunken", 
                                   width=60, height=2)
        self.status_label.pack(pady=5, padx=10, fill="x")

        # Initialize OBS options state
        self.toggle_obs_options()
        self.toggle_time_entry()

    def update_status(self, message, status_type="info"):
        """Update status display with color coding
        status_type: 'success' (green), 'error' (red), 'info' (gray), 'working' (yellow)
        """
        colors = {
            'success': {'bg': '#90EE90', 'fg': '#006400'},
            'error': {'bg': '#FFB6C1', 'fg': '#8B0000'},
            'info': {'bg': 'lightgray', 'fg': 'black'},
            'working': {'bg': '#FFFFE0', 'fg': '#FF8C00'}
        }
        
        color_config = colors.get(status_type, colors['info'])
        self.status_label.config(text=message, bg=color_config['bg'], fg=color_config['fg'])
        self.root.update()

    def toggle_obs_options(self):
        self.video_button.config(state="normal" if self.camera_var.get() else "disabled")

    def toggle_time_entry(self):
        if self.schedule_var.get() == "scheduled":
            self.time_entry.config(state="normal")
        else:
            self.time_entry.delete(0, tk.END)
            self.time_entry.config(state="disabled")

    def select_video(self):
        file = filedialog.askopenfilename(title="Select Video File",
                                          filetypes=[("Video files", "*.mp4 *.mov *.mkv *.avi")])
        if file:
            self.video_path = file
            self.update_status(f"Video selected: {file.split('/')[-1]}", "success")
            print(f"Video selected: {file}")
        else:
            self.update_status("No video selected", "info")

    def launch_obs(self):
        try:
            self.update_status("Launching OBS Studio...", "working")
            subprocess.Popen(["obs64.exe"], cwd=r"C:\Program Files\obs-studio\bin\64bit", shell=True)
            print("Launching OBS...")
            time.sleep(10)
            self.connect_obs()
        except Exception as e:
            self.update_status(f"Failed to launch OBS: {str(e)}", "error")
            print(f"Failed to launch OBS: {e}")

    def connect_obs(self):
        self.update_status("Connecting to OBS WebSocket...", "working")
        for _ in range(10):
            try:
                self.ws = obsws("localhost", 4455, "ashanb")
                self.ws.connect()
                self.update_status("Connected to OBS WebSocket successfully!", "success")
                print("Connected to OBS WebSocket!")
                return
            except exceptions.ConnectionFailure:
                print("Waiting for OBS WebSocket...")
                time.sleep(3)
        self.update_status("Cannot connect to OBS WebSocket", "error")
        messagebox.showerror("Error", "Cannot connect to OBS WebSocket. Make sure WebSocket is enabled.")

    def setup_obs_scene(self):
        if not self.video_path or not self.ws:
            self.update_status("No video selected or OBS not connected", "error")
            print("❌ No video selected or OBS not connected.")
            return

        self.update_status("Setting up OBS scene...", "working")
        scene_name = "AutoScene"
        media_name = "AutoMedia"

        scenes_response = self.ws.call(requests.GetSceneList())
        scenes = [s['sceneName'] for s in scenes_response.getScenes()]

        if scene_name in scenes:
            print(f"Scene '{scene_name}' already exists.")
        else:
            self.ws.call(requests.CreateScene(sceneName=scene_name))
            print(f"Created scene: {scene_name}")
            time.sleep(0.5)

        items = self.ws.call(requests.GetSceneItemList(sceneName=scene_name)).getSceneItems()
        media_item = next((item for item in items if item['sourceName'] == media_name), None)

        if media_item:
            self.ws.call(requests.SetInputSettings(
                inputName=media_name,
                inputSettings={
                    "local_file": self.video_path,
                    "looping": True,
                    "restart_on_activate": True
                }
            ))
            print(f"Updated media input '{media_name}' with new video.")
            media_item_id = media_item['sceneItemId']
        else:
            self.ws.call(requests.CreateInput(
                sceneName=scene_name,
                inputName=media_name,
                inputKind="ffmpeg_source",
                inputSettings={
                    "local_file": self.video_path,
                    "looping": True,
                    "restart_on_activate": True
                }
            ))
            print(f"Added media input: {media_name}")
            time.sleep(0.5)
            items = self.ws.call(requests.GetSceneItemList(sceneName=scene_name)).getSceneItems()
            media_item_id = next((item['sceneItemId'] for item in items if item['sourceName'] == media_name), None)

        if media_item_id is None:
            self.update_status("Could not find media scene item!", "error")
            print("❌ Could not find media scene item!")
            return

        try:
            canvas_settings = self.ws.call(requests.GetVideoSettings())
            canvas_width = canvas_settings.getSettings().get('baseWidth', 1920)
            canvas_height = canvas_settings.getSettings().get('baseHeight', 1080)
        except:
            canvas_width, canvas_height = 1920, 1080
        print(f"Canvas: {canvas_width}x{canvas_height}")

        import subprocess, json
        try:
            ffprobe_cmd = [
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height", "-of", "json", self.video_path
            ]
            result = subprocess.run(ffprobe_cmd, capture_output=True, text=True)
            video_info = json.loads(result.stdout)
            video_width = video_info['streams'][0]['width']
            video_height = video_info['streams'][0]['height']
        except:
            print("❌ Could not get video size, using fallback 1280x720")
            video_width, video_height = 1280, 720
        print(f"Video: {video_width}x{video_height}")

        scale_w = canvas_width / video_width
        scale_h = canvas_height / video_height
        scale = min(scale_w, scale_h)

        new_width = int(video_width * scale)
        new_height = int(video_height * scale)

        pos_x = canvas_width / 2 - new_width / 2
        pos_y = canvas_height / 2 - new_height / 2

        self.ws.call(requests.SetSceneItemProperties(
            sceneItemId=media_item_id,
            visible=True,
            boundsWidth=new_width,
            boundsHeight=new_height,
            boundsType="OBS_BOUNDS_SCALE_INNER",
            positionX=pos_x,
            positionY=pos_y,
            alignment=5
        ))

        self.ws.call(requests.SetCurrentScene(sceneName=scene_name))
        self.ws.call(requests.SetPreviewScene(sceneName=scene_name))
        try:
            self.ws.call(requests.TransitionToProgram(transitionName="Cut", duration=0))
        except:
            pass

        self.update_status(f"OBS scene setup complete - Video scaled and centered", "success")
        print(f"✅ Video scaled ({new_width}x{new_height}) and perfectly centered on {canvas_width}x{canvas_height} canvas.")

    def start_virtual_cam(self):
        try:
            self.update_status("Starting virtual camera...", "working")
            if not self.ws:
                self.launch_obs()
            else:
                try:
                    self.ws.disconnect()
                except:
                    pass
                self.connect_obs()

            self.setup_obs_scene()
            self.select_auto_scene() 
            self.ws.call(requests.StartVirtualCam())
            self.update_status("Virtual Camera started successfully!", "success")
            print("✅ Virtual Camera Started with new video scene!")

        except Exception as e:
            self.update_status(f"Failed to start virtual cam: {str(e)}", "error")
            print(f"Failed to start virtual cam: {e}")
    
    def select_auto_scene(self):
        if not self.ws:
            self.update_status("OBS not connected", "error")
            print("❌ OBS not connected")
            return

        scene_name = "AutoScene"

        try:
            self.ws.call(requests.SetCurrentProgramScene(sceneName=scene_name))
            self.ws.call(requests.SetCurrentPreviewScene(sceneName=scene_name))
            self.update_status(f"Scene '{scene_name}' selected successfully", "success")
            print(f"✅ Scene '{scene_name}' is now selected for preview and live")
        except Exception as e:
            self.update_status(f"Failed to switch scene: {str(e)}", "error")
            print(f"❌ Failed to switch scene: {e}")

    def get_zoom_window(self, timeout=10):
        """Find and connect to Zoom meeting window using pywinauto"""
        try:
            self.update_status("Connecting to Zoom window...", "working")
            
            # Find Zoom.exe process IDs
            zoom_pids = [p.info['pid'] for p in psutil.process_iter(['name', 'pid']) if "Zoom.exe" in p.info['name']]
            if not zoom_pids:
                raise RuntimeError("❌ Zoom.exe not running!")

            # Look through all top-level windows and match process ID
            windows = Desktop(backend="uia").windows()
            for w in windows:
                try:
                    if w.process_id() in zoom_pids:
                        title = w.window_text()
                        if title and not any(x in title for x in ["Chrome", "Visual Studio Code", "WhatsApp"]):
                            app = Application(backend="uia").connect(process=w.process_id())
                            print(f"✅ Found Zoom window: {title}")
                            return app.window(handle=w.handle)
                except Exception:
                    continue

            raise TimeoutError("❌ Could not find Zoom meeting window")
            
        except Exception as e:
            self.update_status(f"Failed to connect to Zoom window: {str(e)}", "error")
            raise e

    def setup_zoom_camera_and_join(self):
        """Setup OBS camera in Zoom and click join"""
        try:
            self.update_status("Setting up Zoom camera and joining...", "working")
            time.sleep(5)

            dlg = self.get_zoom_window()
            time.sleep(2)

            # Select OBS Camera if camera is enabled
            if self.camera_var.get():
                try:
                    camera_dropdowns = dlg.descendants(control_type="ComboBox")
                    if len(camera_dropdowns) >= 2:
                        camera_dropdown = camera_dropdowns[1]  # 2nd combo box = camera
                        camera_dropdown.click_input()
                        time.sleep(1)

                        # Look for OBS in dropdown menu
                        menu_items = dlg.descendants(control_type="MenuItem")
                        selected = False
                        for item in menu_items:
                            text = item.window_text()
                            if "OBS Virtual Camera" in text:
                                item.click_input()
                                self.update_status("OBS Virtual Camera selected ✅", "success")
                                print("📷 OBS Virtual Camera selected ✅")
                                selected = True
                                break
                        if not selected:
                            print("❌ OBS Virtual Camera not found in menu")
                    else:
                        print("❌ Camera dropdown not found")
                except Exception as e:
                    print(f"⚠ Camera selection failed: {e}")

            time.sleep(1)

            # Click Join button
            try:
                join_button = dlg.child_window(title="Join", control_type="Button")
                join_button.click_input()
                self.update_status("Join button clicked ✅", "success")
                print("🚀 Join button clicked ✅")
            except Exception as e:
                print(f"❌ Join button not found: {e}")

            time.sleep(5)
            return dlg

        except Exception as e:
            self.update_status(f"Zoom setup failed: {str(e)}", "error")
            print("Error in setup_zoom_camera_and_join:" , )
            self.setup_zoom_camera_and_join()

    def wait_for_host_admission(self, dlg):
        """Wait for host to admit from waiting room"""
        try:
            self.update_status("Checking for waiting room...", "working")
            print("🔍 Checking for waiting room message...")
            
            WAITING_ROOM_MESSAGES = [
                "waiting for the host",
                "host has not joined", 
                "we've let them know you're here",
                "waiting room"
            ]

            while True:
                try:
                    all_texts = [ctrl.window_text() for ctrl in dlg.descendants(control_type="Text")]
                except Exception:
                    all_texts = []

                found_msg = None
                for txt in all_texts:
                    for msg in WAITING_ROOM_MESSAGES:
                        if msg.lower() in txt.lower():
                            found_msg = txt
                            break

                if found_msg:
                    self.update_status(f"⚠ Waiting room detected: {found_msg}", "working")
                    print(f"⚠ Waiting room detected: {found_msg}")
                    time.sleep(5)

                elif all_texts:  
                    self.update_status("✅ Host admitted you", "success")
                    print("✅ Host admitted you")
                    break

                else:
                    print("🔄 Window changed, re-attaching to Zoom...")
                    try:
                        dlg = self.get_zoom_window()
                        time.sleep(2)
                    except Exception:
                        print("⚠ Could not re-attach, retrying...")
                        time.sleep(3)

            time.sleep(2)
            return dlg

        except Exception as e:
            self.update_status(f"Waiting room handling failed: {str(e)}", "error")
            raise e

    def toggle_zoom_camera_and_mic(self, dlg):
        """Toggle camera and mic based on user settings"""
        try:
            self.update_status("Configuring camera and mic settings...", "working")
            for i in range(3):
                
                time.sleep(2)
                dlg = self.get_zoom_window()
                dlg.set_focus()
                dlg.restore()
                dlg.maximize()
                print(dlg,"*************************************")
                # Toggle Camera
                try:
                    cam_button = dlg.child_window(title_re=".*video*", control_type="Button")
                    cam_text = cam_button.window_text().strip().lower()
                    print(f"🔎 Camera button text: {cam_text}")

                    if self.camera_var.get() and ("start video" in cam_text or "start my video" in cam_text):
                        cam_button.click_input()
                        print("📷 Camera turned ON ✅")
                    elif not self.camera_var.get() and ("stop video" in cam_text or "stop my video" in cam_text):
                        cam_button.click_input()
                        print("📷 Camera turned OFF ✅")
                    else:
                        print("📷 Camera already in desired state")
                        print("Camera", self.camera_var.get(), cam_text)
                except Exception as e:
                    print(f"⚠ Could not toggle camera: {e}")


                # Toggle Mic
                try:
                    mic_button = dlg.child_window(title_re=".*mute*", control_type="Button")
                    mic_text = mic_button.window_text().strip().lower()
                    print(f"🔎 Mic button text: {mic_text}")

                    if self.mic_var.get() and "currently muted" in mic_text:
                        mic_button.click_input()
                        print("🎤 Mic turned ON ✅")
                    elif not self.mic_var.get() and "currently unmute" in mic_text:
                        mic_button.click_input()
                        print("🎤 Mic turned OFF ✅")
                    else:
                        print("🎤 Mic already in desired state")
                except Exception as e:
                    print(f"⚠ Could not toggle mic: {e}")

            self.update_status("🎉 Zoom setup complete!", "success")
            print("🎉 Setup complete!")

        except Exception as e:
            self.update_status(f"Camera/Mic toggle failed: {str(e)}", "error")
            print(f"Camera/Mic toggle failed: {e}")

    def find_and_click_zoom_popup(self):
        time.sleep(3)
        """Pure Windows automation for browser-level Open Zoom Meetings popup - NO webpage detection"""
        try:
            button = None       
            
            images = ["open_zoom.png", "open_zoom_white2.png","open_zoom_white.png"]

            for img in images:
                if os.path.exists(img):  # check file exists
                    try:
                        found = pyautogui.locateOnScreen(img, confidence=0.8)
                        if found:
                            button = found
                            break  # stop if found
                    except Exception as e:
                        print(f"Error locating {img}: {e}")
                else:
                    print(f"Image file not found: {img}")

            if button:
                pyautogui.click(pyautogui.center(button))
                # self.update_status("Open/Join Button Clicked", "success")
            else:
                print("No matching button found -> using fallback keys")
                pyautogui.press('tab', presses=2, interval=0.2)
                pyautogui.press('enter')

            #       
            # self.update_status("Completed browser popup tab navigation", "info")
            return True

        except Exception as e:
            print(f"Error: {e}")
            pass

    def join_zoom_via_browser(self, zoom_link):
        """Browser method for joining Zoom with full automation"""
        try:
            self.update_status("Opening new browser window for Zoom...", "working")
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Set preferences to automatically allow protocol handlers
            prefs = {
                "profile.default_content_setting_values.protocol_handlers": 1,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.popups": 0,
                "profile.default_content_setting_values.notifications": 2,
                "profile.protocol_handler_per_host_allowed_protocols": {
                    "us04web.zoom.us": {
                        "zoommtg": True,
                        "zoomus": True
                    }
                }
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Initialize WebDriver
            self.zoom_driver = webdriver.Chrome(options=chrome_options)
            self.zoom_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigate to Zoom URL
            self.update_status("Navigating to Zoom meeting...", "working")
            self.zoom_driver.get(zoom_link)
            
            # Handle cookie popups first
            # self.handle_cookie_popups()
            
            # popup_handled = self.find_and_click_zoom_popup_quick()
            
            # if not popup_handled:
            #     self.update_status("No popup detected - proceeding with meeting flow", "info")
            
            # # Handle Zoom meeting join flow
            # self.handle_zoom_meeting_flow()
            
        except Exception as e:
            self.update_status(f"Browser automation failed: {str(e)}", "error")
            print(f"Browser automation error: {e}")
            if self.zoom_driver:
                self.zoom_driver.quit()

    def join_zoom_meeting(self):
        """Enhanced Zoom meeting join with pywinauto automation"""
        zoom_link = self.zoom_entry.get().strip()
        if not zoom_link:
            self.update_status("Please enter Zoom meeting URL", "error")
            messagebox.showerror("Error", "Please enter Zoom meeting URL")
            return

        try:
            # Step 1: Open Zoom link in browser to trigger Zoom app
            self.update_status("Opening Zoom meeting link...", "working")
            # webbrowser.open(zoom_link)  # yaha pr brooweser wla kaam krna hy 
            self.join_zoom_via_browser(zoom_link)
            
            time.sleep(8)  # Wait for Zoom app to launch
            if not self.find_and_click_zoom_popup():
                self.find_and_click_zoom_popup()
            # Step 2: Setup camera and join meeting
            dlg = self.setup_zoom_camera_and_join()
            
            # Step 3: Wait for host admission if in waiting room
            dlg = self.wait_for_host_admission(dlg)
            # Step 4: Configure camera and mic settings
            time.sleep(3)
            self.toggle_zoom_camera_and_mic(dlg)
            
            self.update_status("Successfully joined Zoom meeting!", "success")
            self.start_btn.config(state="normal", text="Start Meeting Flow")
            
        except Exception as e:
            self.update_status(f"Failed to join Zoom: {str(e)}", "error")
            self.start_btn.config(state="normal", text="Start Meeting Flow")
            print(f"Error joining Zoom: {e}")

    def start_workflow(self):
        zoom_link = self.zoom_entry.get().strip()
        if not zoom_link:
            self.update_status("Please enter Zoom link", "error")
            messagebox.showerror("Error", "Please enter Zoom link")
            return

        self.start_btn.config(state="disabled", text="Running...")
        self.update_status("Starting meeting workflow...", "working")
        schedule.clear()

        def complete_workflow():
            try:
                if self.camera_var.get():
                    self.update_status("Step 1/2: Setting up OBS and Virtual Camera...", "working")
                    self.start_virtual_cam()
                    time.sleep(3)
                    self.update_status("OBS setup complete. Starting Zoom...", "success")
                else:
                    self.update_status("Skipping OBS (camera disabled). Starting Zoom...", "info")
                
                time.sleep(1)
                self.update_status("Step 2/2: Joining Zoom meeting...", "working")
                self.join_zoom_meeting()
                
            except Exception as e:
                self.update_status(f"Workflow failed: {str(e)}", "error")
                self.start_btn.config(state="normal", text="Start Meeting Flow")

        # Schedule handling
        if self.schedule_var.get() == "scheduled":
            time_str = self.time_entry.get().strip()
            if not time_str:
                self.update_status("Please enter scheduled time", "error")
                messagebox.showerror("Error", "Please enter scheduled time")
                self.start_btn.config(state="normal", text="Start Meeting Flow")
                return
            
            schedule.every().day.at(time_str).do(complete_workflow)
            threading.Thread(target=self.run_scheduler, daemon=True).start()
            self.update_status(f"Meeting scheduled for {time_str}", "success")
            print(f"Meeting scheduled at {time_str}")
        else:
            threading.Thread(target=complete_workflow, daemon=True).start()

        print(f"Zoom Link: {zoom_link}, Mic: {'ON' if self.mic_var.get() else 'OFF'}, Camera: {'ON' if self.camera_var.get() else 'OFF'}")

    def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def extract_meeting_id(self, zoom_link):
        """Extract meeting ID and passcode from Zoom URL"""
        import re
        
        parsed_url = urlparse(zoom_link)
        query_params = parse_qs(parsed_url.query)
        
        passcode = None
        if 'pwd' in query_params:
            passcode = query_params['pwd'][0]
        elif 'password' in query_params:
            passcode = query_params['password'][0]
        
        self.extracted_passcode = passcode
        
        patterns = [
            r'/j/(\d+)',
            r'confno=(\d+)',
            r'meeting_id=(\d+)',
            r'/(\d{9,11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, zoom_link)
            if match:
                meeting_id = match.group(1)
                if passcode:
                    self.update_status(f"Extracted Meeting ID: {meeting_id} with passcode", "success")
                else:
                    self.update_status(f"Extracted Meeting ID: {meeting_id} (no passcode needed)", "success")
                return meeting_id
            
        return None

# ===== MAIN =====
if __name__ == "__main__":
    root = tk.Tk()
    app = MeetingApp(root)
    root.mainloop()
