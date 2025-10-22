# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a self-hosted photo upload and slideshow system designed for parties, running on Raspberry Pi. Guests scan a QR code to upload photos from their phones, which display in a real-time slideshow. The system includes optional face recognition capabilities using a Pi Camera.

**Key Technologies:**
- Backend: Express.js (TypeScript) with better-sqlite3
- Frontend: Vanilla HTML/CSS/JS (Halloween-themed)
- Database: SQLite with WAL mode
- Optional: Python face recognition service
- Target: Raspberry Pi Zero W / Pi 4

## Development Commands

### Local Development
```bash
npm install          # Install dependencies
npm run dev          # Start server with hot-reload (tsx watch)
npm start            # Start server (production mode)
npm run build        # Compile TypeScript to dist/
```

### Building for Raspberry Pi
```bash
npm run build:pi     # Build standalone ARM executable for Pi Zero W
                     # Uses pkg to create build/slideshow-pi
                     # Target: node18-linuxstatic-armv7
```

**Note:** Building for Pi from Windows requires Linux/WSL or GitHub Actions. The recommended approach is to push to GitHub and download the built artifact from Actions.

### Testing
Access locally at:
- Guest Upload: `http://localhost:3000`
- Admin Panel: `http://localhost:3000/admin` (requires `X-API-Key` header)
- Slideshow: `http://localhost:3000/slideshow`

## Architecture

### Core Components

**Backend (`src/server.ts`)**
- Express server on port 3000 (configurable via `PORT` env var)
- Multer middleware handles photo uploads (10MB max, images only)
- Soft-delete architecture (photos marked `deleted` but files remain)
- Admin routes protected by `requireAdmin` middleware (checks `X-API-Key` header)
- Face recognition endpoint at `/api/recognition` (receives events from Python service)

**Database (`src/database.ts`)**
- SQLite database at `photos.db` with WAL mode enabled
- Single `photos` table with columns: id, photo_id (UUID), filename, filepath, filesize, mimetype, guest_name, caption, status, uploaded_at, deleted_at
- Prepared statements for all queries (security + performance)
- Indexes on `status` and `uploaded_at` columns

**Frontend (`public/`)**
- `index.html`: Guest upload page
- `admin.html`: Admin panel for viewing/deleting photos
- `slideshow.html`: Auto-advancing slideshow with speed controls

**Face Recognition (Optional)**
- `face_recognition_service.py`: Standalone Python service that captures video, detects faces, and POSTs recognition events to `/api/recognition`
- Uses dlib/face_recognition library
- Configured via constants: `CAMERA_INDEX`, `RECOGNITION_THRESHOLD`, `FRAME_SKIP`, `SCALE_FACTOR`
- Enrolls known faces from `faces/` directory or via API

### Data Flow

```
Guest Phone → [POST /api/photos] → Multer → Database + uploads/ → [GET /api/photos] → Slideshow
Admin Panel → [DELETE /api/admin/photos/:id] → Soft-delete in DB
Camera → Python Service → [POST /api/recognition] → Node.js Server (TODO: trigger personalized slideshow)
```

### File Upload Strategy
- Photos stored in `uploads/` directory with UUID-based filenames
- Original filename, size, mimetype stored in database
- Soft-delete: `status` set to 'deleted', file remains on disk
- Database tracks all metadata; filesystem only stores blobs

### Configuration
Environment variables (`.env`):
- `PORT`: Server port (default: 3000)
- `ADMIN_API_KEY`: Required header value for admin routes (default: 'change-me-please')

## Deployment Context

### Raspberry Pi Zero W
- Limited resources: use standalone executable from `npm run build:pi`
- No Node.js installation required on device
- Executable includes all dependencies except better-sqlite3 native binary
- Recommended: systemd service for auto-start on boot

### Raspberry Pi 4
- Can run both Node.js server AND Python face recognition simultaneously
- 4GB RAM handles 10-20 simultaneous uploads, ~10-15 FPS recognition
- 8GB RAM handles 50+ uploads, ~15-20 FPS recognition
- See `PI4_COMPLETE_SETUP.md` for unified setup guide

### Common Deployment Patterns
- PM2 for process management (Node.js server)
- systemd services for auto-start on boot
- Chromium kiosk mode for slideshow display
- USB deployment workflow (no SSH/git required)

## Important Implementation Notes

### Security
- Admin routes MUST check `X-API-Key` header via `requireAdmin` middleware
- File uploads validated by mimetype (images only) and size (10MB max)
- Soft-delete prevents data loss but doesn't remove files from disk
- No authentication for guest uploads (by design - party context)

### Database Patterns
- All queries use prepared statements (exported from `database.ts`)
- WAL mode enables concurrent reads during writes
- Photo IDs are UUIDs generated via crypto.randomUUID()
- Timestamps stored as Unix epoch milliseconds (Date.now())

### Cross-Platform Considerations
- TypeScript compiled to CommonJS (target: ES2022)
- Use path.join() for all file paths (Windows/Linux compatibility)
- Better-sqlite3 requires native compilation per platform
- Face recognition Python service only runs on Pi (camera dependency)

## Build Artifacts

- `dist/`: TypeScript compilation output (gitignored)
- `build/slideshow-pi`: Standalone executable for Pi Zero W (gitignored)
- `uploads/`: User-uploaded photos (gitignored)
- `photos.db`: SQLite database (gitignored)
- `known_faces.pkl`: Face recognition encodings (gitignored)

## Future Enhancements (TODOs in code)

See `src/server.ts:188-190`:
- Store recognition events in database
- Trigger personalized slideshow based on recognized face
- Send WebSocket events to connected clients for real-time updates

Additional ideas documented in `PI4_COMPLETE_SETUP.md:321-327`:
- Admin panel for managing enrolled faces
- Auto-tag uploaded photos with recognized faces
- Generate party attendance reports
- Add photo filters/effects
