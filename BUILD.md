# Building for Raspberry Pi Zero W

This project creates a standalone executable for Raspberry Pi that requires NO Node.js installation.

## Easy Method: Download from GitHub Actions (Recommended)

1. Push your code to GitHub (on the `no-node` or `main` branch)
2. Go to your repository's **Actions** tab
3. Find the latest "Build for Raspberry Pi" workflow run
4. Download the `slideshow-pi-executable` artifact
5. Extract and copy `slideshow-pi` to your Pi via USB

## Alternative: Build Locally (Requires Linux/WSL/Docker)

Building from Windows directly doesn't work due to cross-compilation limitations. You need Linux to build for Pi.

## Deploying to Raspberry Pi (USB Method - No SSH/Git needed)

1. Download `slideshow-pi` executable from GitHub Actions (see above)

2. Copy `slideshow-pi` to a USB drive

3. On Raspberry Pi terminal:
```bash
# Copy from USB to home directory
cd ~
cp /media/pi/*/slideshow-pi .
chmod +x slideshow-pi

# Create uploads folder
mkdir uploads

# Run it! (No Node.js needed)
./slideshow-pi
```

That's it! The executable includes everything needed.

## Running on Boot (Optional)

Create a systemd service:

```bash
sudo nano /etc/systemd/system/slideshow.service
```

Add:
```ini
[Unit]
Description=Photo Slideshow Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/slideshow
ExecStart=/usr/bin/node /home/pi/slideshow/server-bundle.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable slideshow.service
sudo systemctl start slideshow.service
sudo systemctl status slideshow.service
```

## Notes

- You only need to install Node.js ONCE on the Pi (lightweight, ~40MB)
- The bundled file is small (~2-3MB)
- Much better than pkg for Pi Zero W - faster and more reliable
- better-sqlite3 needs its native ARM binary from node_modules
