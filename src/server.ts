import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { randomUUID } from 'crypto';
import dotenv from 'dotenv';
import {
  insertPhoto,
  getActivePhotos,
  getPhotoById,
  softDeletePhoto,
  getAllPhotosForAdmin,
  PhotoInsert,
  Photo
} from './database';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const ADMIN_API_KEY = process.env.ADMIN_API_KEY || 'change-me-please';

// Create uploads directory
const UPLOADS_DIR = path.join(__dirname, '..', 'uploads');
if (!fs.existsSync(UPLOADS_DIR)) {
  fs.mkdirSync(UPLOADS_DIR, { recursive: true });
}

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '..', 'public')));
app.use('/uploads', express.static(UPLOADS_DIR));

// Multer configuration for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, UPLOADS_DIR);
  },
  filename: (req, file, cb) => {
    const photoId = randomUUID();
    const ext = path.extname(file.originalname);
    cb(null, `${photoId}${ext}`);
  }
});

const upload = multer({
  storage,
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB max
  },
  fileFilter: (req, file, cb) => {
    const allowedMimes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (allowedMimes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only images are allowed.'));
    }
  }
});

// Admin authentication middleware
const requireAdmin = (req: Request, res: Response, next: NextFunction) => {
  const apiKey = req.headers['x-api-key'];

  if (!apiKey || apiKey !== ADMIN_API_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  next();
};

// Routes

// Health check
app.get('/api/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', timestamp: Date.now() });
});

// Upload photo
app.post('/api/photos', upload.single('photo'), (req: Request, res: Response) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const { guestName, caption } = req.body;
    const photoId = path.parse(req.file.filename).name;
    const photoData: PhotoInsert = {
      photo_id: photoId,
      filename: req.file.originalname,
      filepath: req.file.filename,
      filesize: req.file.size,
      mimetype: req.file.mimetype,
      guest_name: guestName || null,
      caption: caption || null,
      uploaded_at: Date.now()
    };

    insertPhoto.run(photoData);

    res.json({
      message: 'Photo uploaded successfully',
      photoId,
      filename: req.file.originalname
    });
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'Failed to upload photo' });
  }
});

// Get all active photos (for slideshow)
app.get('/api/photos', (req: Request, res: Response) => {
  try {
    const photos = getActivePhotos.all() as Photo[];

    const photoData = photos.map(photo => ({
      photoId: photo.photo_id,
      filename: photo.filename,
      url: `/uploads/${photo.filepath}`,
      uploadedAt: photo.uploaded_at,
      filesize: photo.filesize,
      guestName: photo.guest_name,
      caption: photo.caption
    }));

    res.json({ photos: photoData });
  } catch (error) {
    console.error('Error fetching photos:', error);
    res.status(500).json({ error: 'Failed to fetch photos' });
  }
});

// Admin: Get all photos with metadata
app.get('/api/admin/photos', requireAdmin, (req: Request, res: Response) => {
  try {
    const photos = getAllPhotosForAdmin.all() as Photo[];

    const photoData = photos.map(photo => ({
      photoId: photo.photo_id,
      filename: photo.filename,
      url: `/uploads/${photo.filepath}`,
      uploadedAt: photo.uploaded_at,
      filesize: photo.filesize,
      guestName: photo.guest_name,
      caption: photo.caption,
      status: photo.status
    }));

    res.json({ photos: photoData });
  } catch (error) {
    console.error('Error fetching admin photos:', error);
    res.status(500).json({ error: 'Failed to fetch photos' });
  }
});

// Admin: Delete photo
app.delete('/api/admin/photos/:photoId', requireAdmin, (req: Request, res: Response) => {
  try {
    const { photoId } = req.params;

    const result = softDeletePhoto.run(Date.now(), photoId);

    if (result.changes === 0) {
      return res.status(404).json({ error: 'Photo not found' });
    }

    res.json({ message: 'Photo deleted successfully' });
  } catch (error) {
    console.error('Error deleting photo:', error);
    res.status(500).json({ error: 'Failed to delete photo' });
  }
});

// Face Recognition: Receive recognition events from Python service
app.post('/api/recognition', (req: Request, res: Response) => {
  try {
    const { name, timestamp } = req.body;

    if (!name) {
      return res.status(400).json({ error: 'Name is required' });
    }

    console.log(`🎯 Face recognized: ${name} at ${new Date(timestamp * 1000).toLocaleTimeString()}`);

    // TODO: Store recognition events in database
    // TODO: Trigger personalized slideshow
    // TODO: Send WebSocket event to connected clients

    res.json({ success: true, message: `Recognized ${name}` });
  } catch (error) {
    console.error('Error processing recognition:', error);
    res.status(500).json({ error: 'Failed to process recognition' });
  }
});

// Serve frontend routes
app.get('/', (req: Request, res: Response) => {
  res.sendFile(path.join(__dirname, '..', 'public', 'index.html'));
});

app.get('/admin', (req: Request, res: Response) => {
  res.sendFile(path.join(__dirname, '..', 'public', 'admin.html'));
});

app.get('/slideshow', (req: Request, res: Response) => {
  res.sendFile(path.join(__dirname, '..', 'public', 'slideshow.html'));
});

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error('Server error:', err);
  res.status(500).json({ error: err.message || 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  console.log(`
🎉 Party Photo Server is running!

📸 Guest Upload:    http://localhost:${PORT}
🔐 Admin Panel:     http://localhost:${PORT}/admin
🖼️  Slideshow:       http://localhost:${PORT}/slideshow

🔑 Admin API Key: ${ADMIN_API_KEY}

Replace 'localhost' with your Raspberry Pi's IP address for network access.
  `);
});

export default app;
