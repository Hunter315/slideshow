# Building for Raspberry Pi Zero W

This project can be compiled into a standalone executable that runs on Raspberry Pi Zero W without needing to install Node.js.

## Prerequisites (on your Windows machine)

1. Install dependencies:
```bash
npm install
```

## Building the Executable

Run this command on your Windows machine:

```bash
npm run build:pi
```

This will create a file called `slideshow-pi` in the `build/` directory. This is a standalone executable for ARM64 Linux (Raspberry Pi).

## Deploying to Raspberry Pi

1. Copy the executable to your Pi:
```bash
scp build/slideshow-pi pi@raspberrypi.local:~/
```

2. SSH into your Pi:
```bash
ssh pi@raspberrypi.local
```

3. Make it executable:
```bash
chmod +x slideshow-pi
```

4. Create necessary directories:
```bash
mkdir -p uploads
```

5. Create a .env file (optional):
```bash
nano .env
```
Add:
```
PORT=3000
```

6. Run the application:
```bash
./slideshow-pi
```

## Running on Boot (Optional)

To make it start automatically when the Pi boots:

1. Create a systemd service file:
```bash
sudo nano /etc/systemd/system/slideshow.service
```

2. Add this content:
```ini
[Unit]
Description=Photo Slideshow Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/home/pi/slideshow-pi
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl enable slideshow.service
sudo systemctl start slideshow.service
```

4. Check status:
```bash
sudo systemctl status slideshow.service
```

## Notes

- The executable is ~50-80MB (includes Node.js runtime and all dependencies)
- No Node.js installation needed on the Pi
- The Pi Zero W only needs standard Linux libraries (glibc)
- All dependencies are bundled into the single executable
