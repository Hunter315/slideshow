import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { randomUUID } from 'crypto';
import dotenv from 'dotenv';
import Anthropic from '@anthropic-ai/sdk';
import os from 'os';
import {
  insertPhoto,
  getActivePhotos,
  getPhotoById,
  softDeletePhoto,
  getAllPhotosForAdmin,
  updatePhotoProcessing,
  PhotoInsert,
  Photo,
  insertRecognitionEvent,
  getMostRecentRecognition,
  getRecentRecognitionsByPerson,
  RecognitionEvent,
  RecognitionEventInsert,
  insertReading,
  getReadingById,
  Reading,
  ReadingInsert
} from './database';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const ADMIN_API_KEY = process.env.ADMIN_API_KEY || 'change-me-please';

// Get local IP address
function getLocalIpAddress(): string {
  const interfaces = os.networkInterfaces();

  // Priority order: wlan0 (Pi WiFi), eth0 (Pi Ethernet), then any other
  const priorityInterfaces = ['wlan0', 'eth0'];

  // First try priority interfaces
  for (const ifaceName of priorityInterfaces) {
    const iface = interfaces[ifaceName];
    if (iface) {
      for (const addr of iface) {
        if (addr.family === 'IPv4' && !addr.internal) {
          return addr.address;
        }
      }
    }
  }

  // Fallback: find any non-internal IPv4 address
  for (const ifaceName in interfaces) {
    const iface = interfaces[ifaceName];
    if (iface) {
      for (const addr of iface) {
        if (addr.family === 'IPv4' && !addr.internal) {
          return addr.address;
        }
      }
    }
  }

  return 'localhost';
}

const LOCAL_IP = getLocalIpAddress();

// Initialize Anthropic client
const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || '',
});

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

    const photoData = photos.map(photo => {
      let recognizedFaces = [];
      try {
        if (photo.recognized_faces) {
          recognizedFaces = JSON.parse(photo.recognized_faces);
        }
      } catch (e) {
        // If parsing fails, leave as empty array
      }

      return {
        photoId: photo.photo_id,
        filename: photo.filename,
        url: `/uploads/${photo.filepath}`,
        uploadedAt: photo.uploaded_at,
        filesize: photo.filesize,
        guestName: photo.guest_name,
        caption: photo.caption,
        status: photo.status,
        processedAt: photo.processed_at,
        recognizedFaces: recognizedFaces
      };
    });

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

    // Store recognition event in database
    const eventData: RecognitionEventInsert = {
      person_name: name,
      timestamp: timestamp,
      created_at: Date.now()
    };
    insertRecognitionEvent.run(eventData);

    // TODO: Send WebSocket event to connected clients for real-time updates

    res.json({ success: true, message: `Recognized ${name}` });
  } catch (error) {
    console.error('Error processing recognition:', error);
    res.status(500).json({ error: 'Failed to process recognition' });
  }
});

// Get most recent recognized person with stare duration
app.get('/api/recognition/current', (req: Request, res: Response) => {
  try {
    const recentRecognition = getMostRecentRecognition.get() as RecognitionEvent | undefined;

    if (!recentRecognition) {
      return res.json({ recognized: false, stareDuration: 0 });
    }

    // Only return recognitions from the last 10 seconds (if no new events, person left)
    const tenSecondsAgo = Date.now() - 10000;
    if (recentRecognition.created_at < tenSecondsAgo) {
      return res.json({ recognized: false, stareDuration: 0 });
    }

    // Calculate continuous presence duration
    // Get all recognition events for this person in the last 10 seconds
    const recentEvents = getRecentRecognitionsByPerson.all(
      recentRecognition.person_name,
      tenSecondsAgo
    ) as RecognitionEvent[];

    if (recentEvents.length === 0) {
      return res.json({ recognized: false, stareDuration: 0 });
    }

    // Calculate duration: time from oldest recent event to now
    const oldestEvent = recentEvents[recentEvents.length - 1];
    const stareDurationMs = Date.now() - oldestEvent.created_at;

    res.json({
      recognized: true,
      personName: recentRecognition.person_name,
      timestamp: recentRecognition.timestamp,
      stareDuration: stareDurationMs, // in milliseconds
      eventCount: recentEvents.length
    });
  } catch (error) {
    console.error('Error fetching current recognition:', error);
    res.status(500).json({ error: 'Failed to fetch recognition' });
  }
});

// Request a psychic reading
app.post('/api/readings/request', async (req: Request, res: Response) => {
  try {
    const { personName } = req.body;

    if (!personName) {
      return res.status(400).json({ error: 'personName is required' });
    }

    console.log(`🔮 Generating psychic reading for ${personName}...`);

    // Generate reading using Claude
    const message = await anthropic.messages.create({
      model: 'claude-sonnet-4-5-20250929',
      max_tokens: 500,
      messages: [{
        role: 'user',
        content: `You are a mystical fortune teller at a Halloween party. Give ${personName} a creative, entertaining, and slightly spooky psychic reading. The reading should be personalized with their name, mysterious but fun, and appropriate for a party atmosphere. Keep it to 3-4 sentences. Make it feel authentic and engaging, with references to cosmic energies, fate, or mysterious forces. Do not use any formatting or special characters - just plain text.`
      }]
    });

    const readingText = message.content[0].type === 'text' ? message.content[0].text : '';

    // Store reading in database
    const readingId = randomUUID();
    const readingData: ReadingInsert = {
      reading_id: readingId,
      person_name: personName,
      reading_type: 'psychic',
      reading_text: readingText,
      created_at: Date.now()
    };
    insertReading.run(readingData);

    console.log(`✨ Generated reading for ${personName}`);

    res.json({
      readingId,
      personName,
      readingText,
      createdAt: readingData.created_at
    });
  } catch (error) {
    console.error('Error generating reading:', error);
    res.status(500).json({ error: 'Failed to generate reading' });
  }
});

// Get a specific reading by ID
app.get('/api/readings/:readingId', (req: Request, res: Response) => {
  try {
    const { readingId } = req.params;
    const reading = getReadingById.get(readingId) as Reading | undefined;

    if (!reading) {
      return res.status(404).json({ error: 'Reading not found' });
    }

    res.json({
      readingId: reading.reading_id,
      personName: reading.person_name,
      readingType: reading.reading_type,
      readingText: reading.reading_text,
      createdAt: reading.created_at
    });
  } catch (error) {
    console.error('Error fetching reading:', error);
    res.status(500).json({ error: 'Failed to fetch reading' });
  }
});

// Photo Processing: Receive processing results from Python service
app.post('/api/photo-processed', (req: Request, res: Response) => {
  try {
    const { photo_id, results } = req.body;

    if (!photo_id) {
      return res.status(400).json({ error: 'photo_id is required' });
    }

    // Store the results as JSON string in database
    const recognizedFacesJson = JSON.stringify(results.detected_faces || []);
    const processedAt = Date.now();

    updatePhotoProcessing.run(processedAt, recognizedFacesJson, photo_id);

    // Log recognized faces
    if (results.detected_faces && results.detected_faces.length > 0) {
      const recognizedNames = results.detected_faces
        .map((face: any) => face.name)
        .filter((name: string) => name !== 'Unknown');

      if (recognizedNames.length > 0) {
        console.log(`✅ Photo ${photo_id}: Recognized ${recognizedNames.join(', ')}`);
      } else {
        console.log(`📸 Photo ${photo_id}: Face(s) detected but not recognized`);
      }
    } else {
      console.log(`📸 Photo ${photo_id}: No faces detected`);
    }

    res.json({ success: true, message: 'Processing results stored' });
  } catch (error) {
    console.error('Error storing processing results:', error);
    res.status(500).json({ error: 'Failed to store processing results' });
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

app.get('/psychic', (req: Request, res: Response) => {
  res.sendFile(path.join(__dirname, '..', 'public', 'psychic.html'));
});

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error('Server error:', err);
  res.status(500).json({ error: err.message || 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  const baseUrl = LOCAL_IP === 'localhost' ? 'localhost' : LOCAL_IP;

  console.log(`
🎉 Party Photo Server is running!

📸 Guest Upload:    http://${baseUrl}:${PORT}
🔐 Admin Panel:     http://${baseUrl}:${PORT}/admin
🖼️  Slideshow:       http://${baseUrl}:${PORT}/slideshow
🔮 Psychic Reading: http://${baseUrl}:${PORT}/psychic

🔑 Admin API Key: ${ADMIN_API_KEY}
${LOCAL_IP !== 'localhost' ? `\n📡 Network IP detected: ${LOCAL_IP}` : '\n⚠️  No network IP detected - running on localhost only'}
  `);
});

export default app;
