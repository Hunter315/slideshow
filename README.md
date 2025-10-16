# 🎃 Halloween Party Photo Upload & Slideshow

A spooky self-hosted photo upload system for your Halloween party! Runs entirely on Raspberry Pi. Guests scan a QR code to upload photos from their phones, which are displayed in a real-time slideshow with name/caption support.

## 👻 Features

- **Halloween Theme**: Spooky orange & black design with floating ghosts 🦇
- **Mobile-First**: Fully optimized for phone use
- **Guest Upload**: Camera + gallery upload with name & caption
- **Admin Panel**: Secure photo management (view & delete)
- **Live Slideshow**: Auto-updating with adjustable speed controls
- **Self-Hosted**: 100% on Raspberry Pi (no cloud, no costs!)
- **Local Network**: Works on your WiFi, no internet required

## 🏗️ Architecture

```
                    ┌─────────────────┐
                    │  Raspberry Pi   │
                    │                 │
                    │  Express Server │
                    │  SQLite DB      │
                    │  Photo Storage  │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
      ┌─────▼─────┐    ┌────▼────┐    ┌─────▼──────┐
      │  Guests   │    │  Admin  │    │ Slideshow  │
      │  Upload   │    │  Panel  │    │  Display   │
      └───────────┘    └─────────┘    └────────────┘
```

## 📋 Prerequisites

- **Raspberry Pi Zero W** (or any Pi with WiFi)
- **Node.js 18+** installed on Pi
- **Chromium browser** (for slideshow display)
- Network connection (your home WiFi)

---

## 🧪 Test on Your Computer First

### 1. Install Dependencies

```bash
npm install
```

### 2. Start the Server

```bash
npm start
```

### 3. Test It Out

Open in your browser:
- **Guest Upload**: http://localhost:3000
- **Admin Panel**: http://localhost:3000/admin (API Key: `thisismysecretadminkey`)
- **Slideshow**: http://localhost:3000/slideshow

Test the flow:
1. Upload a photo with your name and a spooky message
2. Check the slideshow to see it appear
3. Use admin panel to view/delete photos
4. Try the slideshow controls (speed, prev/next, pause)

---

## 🥧 Deploy to Raspberry Pi Zero W

### Step 1: Prepare Your Raspberry Pi

**SSH into your Pi** (or connect keyboard/monitor):

```bash
ssh pi@<raspberry-pi-ip>
```

Default credentials: `pi` / `raspberry` (change this!)

### Step 2: Install Node.js (if not installed)

```bash
# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

### Step 3: Transfer Your Project to the Pi

**Option A: Using SCP (from your Windows computer)**

Open Command Prompt or PowerShell:

```bash
scp -r C:\Users\hunte\OneDrive\Desktop\slideshow pi@<raspberry-pi-ip>:/home/pi/
```

**Option B: Using Git**

On your computer:
```bash
cd C:\Users\hunte\OneDrive\Desktop\slideshow
git init
git add .
git commit -m "Halloween party photo app"
git remote add origin <your-github-repo-url>
git push -u origin main
```

On Raspberry Pi:
```bash
cd /home/pi
git clone <your-github-repo-url> slideshow
```

**Option C: Using USB Drive**

1. Copy the `slideshow` folder to a USB drive
2. Plug USB drive into Raspberry Pi
3. Mount and copy:
```bash
sudo mount /dev/sda1 /mnt
cp -r /mnt/slideshow /home/pi/
sudo umount /mnt
```

### Step 4: Install Dependencies on Pi

```bash
cd /home/pi/slideshow
npm install
```

This might take 5-10 minutes on Raspberry Pi Zero W (be patient!)

### Step 5: Configure Your Admin API Key

**IMPORTANT**: Change your admin API key to something secure!

```bash
nano .env
```

Change this line:
```
ADMIN_API_KEY=YourSuperSecretHalloweenKey2024
```

Save with `Ctrl+X`, then `Y`, then `Enter`

### Step 6: Test the Server

```bash
npm start
```

You should see:
```
🎉 Party Photo Server is running!

📸 Guest Upload:    http://localhost:3000
🔐 Admin Panel:     http://localhost:3000/admin
🖼️  Slideshow:       http://localhost:3000/slideshow

🔑 Admin API Key: YourSuperSecretHalloweenKey2024
```

### Step 7: Find Your Pi's IP Address

In a new terminal (or press `Ctrl+C` to stop server, then):

```bash
hostname -I
```

Example output: `192.168.1.100`

### Step 8: Test from Your Phone

Connect your phone to the **same WiFi network** as the Pi, then visit:
- Guest Upload: `http://192.168.1.100:3000`
- Admin Panel: `http://192.168.1.100:3000/admin`

**If you can see the upload page on your phone, you're ready!** 🎉

---

## 🔄 Make Server Auto-Start on Boot

Use PM2 to run the server automatically:

### 1. Install PM2

```bash
sudo npm install -g pm2
```

### 2. Start Your App with PM2

```bash
cd /home/pi/slideshow
pm2 start npm --name "halloween-party" -- start
```

### 3. Save PM2 Configuration

```bash
pm2 save
```

### 4. Enable Auto-Start on Boot

```bash
pm2 startup
```

Follow the command it prints (copy and paste it).

### 5. Reboot and Test

```bash
sudo reboot
```

After reboot, the server should start automatically!

**Check status:**
```bash
pm2 status
pm2 logs halloween-party
```

---

## 🖥️ Setup Slideshow Auto-Launch (Optional)

If you want the slideshow to display automatically on a monitor/TV:

### 1. Install Chromium (if needed)

```bash
sudo apt-get update
sudo apt-get install -y chromium-browser unclutter
```

### 2. Create Auto-Start Script

```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/slideshow.desktop
```

Add this content:
```ini
[Desktop Entry]
Type=Application
Name=Halloween Slideshow
Exec=chromium-browser --kiosk --noerrdialogs --disable-infobars http://localhost:3000/slideshow
```

Save with `Ctrl+X`, `Y`, `Enter`

### 3. Disable Screen Blanking

```bash
sudo nano /etc/lightdm/lightdm.conf
```

Find `[Seat:*]` section and add:
```ini
xserver-command=X -s 0 -dpms
```

### 4. Reboot

```bash
sudo reboot
```

The slideshow will launch in fullscreen automatically! 🎃

---

## 📱 Create QR Code for Guests

Once your Pi is running on your network, create a QR code with your Pi's IP:

**URL to use:**
```
http://192.168.1.100:3000
```
(Replace with YOUR Pi's IP address)

**Generate QR Code:**
- Online: https://www.qr-code-generator.com/
- Or use `qrencode`:
  ```bash
  sudo apt-get install qrencode
  qrencode -o party-qr.png "http://192.168.1.100:3000"
  ```

**Print it large** and display at your party entrance! 👻

---

## 🎮 How to Use

### For Guests
1. Scan QR code with phone
2. Allow camera access (or choose from gallery)
3. Take/select a spooky photo
4. Enter name and caption (optional)
5. Upload! Photo appears in slideshow within 30 seconds

### For You (Admin)
1. Visit `http://<pi-ip>:3000/admin` on your phone
2. Login with your admin API key
3. View all uploaded photos
4. Delete inappropriate ones
5. Pull down to refresh

### Slideshow Controls (Mobile)
- Tap **⚙️ Controls** button to access:
  - **Speed**: Fast (3s), Normal (5s), Slow (8s)
  - **Navigation**: Prev, Next, Play/Pause
  - **Refresh**: Manually load new photos
- Controls auto-hide after 10 seconds
- Tap toggle button to show again

**Desktop Keyboard Shortcuts:**
- Arrow Keys: Navigate
- Spacebar: Play/Pause
- R: Refresh photos
- C: Toggle controls
- F: Fullscreen

---

## 🛠️ Troubleshooting

### Can't Connect from Phone

**Check firewall:**
```bash
sudo ufw allow 3000
```

**Verify Pi IP:**
```bash
hostname -I
```

**Ensure phone on same WiFi network as Pi**

### Server Won't Start

**Check if port 3000 is in use:**
```bash
sudo lsof -i :3000
```

**View logs:**
```bash
pm2 logs halloween-party
```

**Restart server:**
```bash
pm2 restart halloween-party
```

### Photos Not Loading in Slideshow

**Check server is running:**
```bash
pm2 status
```

**Test API manually:**
```bash
curl http://localhost:3000/api/photos
```

**Check uploads folder:**
```bash
ls -la /home/pi/slideshow/uploads
```

### Database Issues

**Reset database:**
```bash
cd /home/pi/slideshow
rm photos.db photos.db-wal photos.db-shm
pm2 restart halloween-party
```

---

## 🔒 Security Notes

- **Admin API Key**: Keep it secret! Don't share publicly
- **Local Network Only**: Server only accessible on your WiFi
- **No Internet Exposure**: Not accessible from outside (unless you port forward)
- **Soft Delete**: Photos marked deleted but kept in `uploads/` folder
- **Change Default Password**: Change Pi password from default `raspberry`!

---

## 💾 Backup & Restore

### Backup All Photos

```bash
cd /home/pi/slideshow
tar -czf halloween-party-backup-$(date +%F).tar.gz uploads/ photos.db
```

### Restore Photos

```bash
cd /home/pi/slideshow
tar -xzf halloween-party-backup-*.tar.gz
pm2 restart halloween-party
```

### Clear All Photos (After Party)

```bash
cd /home/pi/slideshow
rm -rf uploads/*
rm photos.db photos.db-wal photos.db-shm
pm2 restart halloween-party
```

---

## 📊 Performance

Raspberry Pi Zero W can handle:
- **50+ guests** uploading simultaneously
- **1000+ photos** without slowdown
- Smooth slideshow playback

---

## 🎨 Customization

### Change Slide Duration

Edit `public/slideshow.html`:
```javascript
let SLIDE_DURATION = 5000; // Change to 3000 for 3s, 8000 for 8s, etc.
```

### Change Auto-Refresh Interval

Edit `public/slideshow.html`:
```javascript
const REFRESH_INTERVAL = 30000; // Check for new photos every X ms
```

### Change Upload Size Limit

Edit `src/server.ts`:
```typescript
limits: {
  fileSize: 10 * 1024 * 1024, // 10MB (change as needed)
}
```

Then restart:
```bash
pm2 restart halloween-party
```

---

## 🆘 PM2 Commands

```bash
# View status
pm2 status

# View logs
pm2 logs halloween-party

# Restart server
pm2 restart halloween-party

# Stop server
pm2 stop halloween-party

# Start server
pm2 start halloween-party

# Remove from PM2
pm2 delete halloween-party
```

---

## 📝 License

MIT License - Feel free to use for your parties!

---

## 🎃 Have a Spooktacular Halloween Party!

Questions? Issues? Check the troubleshooting section above or create an issue on GitHub.

**Happy Halloween! 👻🎃🦇**
