# Zoom Meeting Taker (with Pre-Recorded Video)

This project allows you to automatically join Zoom meetings with OBS Studio and a pre-recorded video, giving the impression of a live presence.  

---

## 📋 Prerequisites
Before setting up, make sure you have the following installed:
1. **OBS Studio** (latest version) → [Download here](https://obsproject.com/download)  
2. **Zoom Meeting App** → [Download here](https://zoom.us/download)  
3. **Google Chrome** → [Download here](https://www.google.com/chrome/)  

---

## ⚙️ Setup Steps

### 1. Configure OBS Studio
1. Open **OBS Studio**.  
2. On the **top-left menu**, click **Tools → WebSocket Server Settings**.  
3. Enable **WebSocket server**.  
4. Set the following values:  
   - **Server Port**: `4455`  
   - **Password**: `ashanb`  
5. Click **Apply → OK**, then close the settings window.  

---

### 2. Configure the App
1. Open the **Zoom Meeting Taker app**.  
2. Enter your **Zoom meeting link**.  
3. Set options:  
   - **Microphone**: On/Off  
   - **Camera**: On/Off  
   - **Schedule**:  
     - Choose `Now` (immediate join), or  
     - Set a scheduled time using **24-hour format** (`HH:MM`).  

4. Click **Start** and watch the magic happen 🎉  

---

## ⚠️ Important Notes
- **Do not open Zoom or OBS Studio manually before starting the app.**  
- The app will launch and control both automatically.  

---

## 🚀 Example Usage
- **Join immediately:**  
  Enter Zoom link → Camera On → Mic Off → Start.  

- **Schedule meeting at 14:30 (2:30 PM):**  
  Enter Zoom link → Set `14:30` → Camera Off → Mic On → Start.  

---

## 🙌 Credits
Developed by **Ashan Baig **  
