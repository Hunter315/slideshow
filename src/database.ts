import Database from 'better-sqlite3';
import path from 'path';

const DB_PATH = path.join(__dirname, '..', 'photos.db');
const db = new Database(DB_PATH);

// Enable WAL mode for better concurrency
db.pragma('journal_mode = WAL');

// Create photos table
db.exec(`
  CREATE TABLE IF NOT EXISTS photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    photo_id TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    filesize INTEGER NOT NULL,
    mimetype TEXT NOT NULL,
    guest_name TEXT,
    caption TEXT,
    status TEXT DEFAULT 'active',
    uploaded_at INTEGER NOT NULL,
    deleted_at INTEGER,
    processed_at INTEGER,
    recognized_faces TEXT
  );

  CREATE INDEX IF NOT EXISTS idx_status ON photos(status);
  CREATE INDEX IF NOT EXISTS idx_uploaded_at ON photos(uploaded_at);

  CREATE TABLE IF NOT EXISTS recognition_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_name TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    created_at INTEGER NOT NULL
  );

  CREATE INDEX IF NOT EXISTS idx_person_name ON recognition_events(person_name);
  CREATE INDEX IF NOT EXISTS idx_timestamp ON recognition_events(timestamp);

  CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reading_id TEXT UNIQUE NOT NULL,
    person_name TEXT NOT NULL,
    reading_type TEXT DEFAULT 'psychic',
    reading_text TEXT NOT NULL,
    created_at INTEGER NOT NULL
  );

  CREATE INDEX IF NOT EXISTS idx_reading_id ON readings(reading_id);
  CREATE INDEX IF NOT EXISTS idx_reading_person ON readings(person_name);
`);

export interface Photo {
  id: number;
  photo_id: string;
  filename: string;
  filepath: string;
  filesize: number;
  mimetype: string;
  guest_name?: string;
  caption?: string;
  status: 'active' | 'deleted';
  uploaded_at: number;
  deleted_at?: number;
  processed_at?: number;
  recognized_faces?: string;
}

export interface PhotoInsert {
  photo_id: string;
  filename: string;
  filepath: string;
  filesize: number;
  mimetype: string;
  guest_name?: string;
  caption?: string;
  uploaded_at: number;
}

export const insertPhoto = db.prepare(`
  INSERT INTO photos (photo_id, filename, filepath, filesize, mimetype, guest_name, caption, uploaded_at)
  VALUES (@photo_id, @filename, @filepath, @filesize, @mimetype, @guest_name, @caption, @uploaded_at)
`);

export const getActivePhotos = db.prepare(`
  SELECT * FROM photos
  WHERE status = 'active'
  ORDER BY uploaded_at DESC
`);

export const getPhotoById = db.prepare(`
  SELECT * FROM photos
  WHERE photo_id = ? AND status = 'active'
`);

export const softDeletePhoto = db.prepare(`
  UPDATE photos
  SET status = 'deleted', deleted_at = ?
  WHERE photo_id = ? AND status = 'active'
`);

export const getAllPhotosForAdmin = db.prepare(`
  SELECT * FROM photos
  WHERE status = 'active'
  ORDER BY uploaded_at DESC
`);

export const updatePhotoProcessing = db.prepare(`
  UPDATE photos
  SET processed_at = ?, recognized_faces = ?
  WHERE photo_id = ?
`);

// Recognition events interfaces and queries
export interface RecognitionEvent {
  id: number;
  person_name: string;
  timestamp: number;
  created_at: number;
}

export interface RecognitionEventInsert {
  person_name: string;
  timestamp: number;
  created_at: number;
}

export const insertRecognitionEvent = db.prepare(`
  INSERT INTO recognition_events (person_name, timestamp, created_at)
  VALUES (@person_name, @timestamp, @created_at)
`);

export const getMostRecentRecognition = db.prepare(`
  SELECT * FROM recognition_events
  ORDER BY created_at DESC
  LIMIT 1
`);

export const getRecentRecognitionsByPerson = db.prepare(`
  SELECT * FROM recognition_events
  WHERE person_name = ? AND created_at > ?
  ORDER BY created_at DESC
`);

export const getRecognitionsByPerson = db.prepare(`
  SELECT * FROM recognition_events
  WHERE person_name = ?
  ORDER BY created_at DESC
`);

// Readings interfaces and queries
export interface Reading {
  id: number;
  reading_id: string;
  person_name: string;
  reading_type: string;
  reading_text: string;
  created_at: number;
}

export interface ReadingInsert {
  reading_id: string;
  person_name: string;
  reading_type: string;
  reading_text: string;
  created_at: number;
}

export const insertReading = db.prepare(`
  INSERT INTO readings (reading_id, person_name, reading_type, reading_text, created_at)
  VALUES (@reading_id, @person_name, @reading_type, @reading_text, @created_at)
`);

export const getReadingById = db.prepare(`
  SELECT * FROM readings
  WHERE reading_id = ?
`);

export const getReadingsByPerson = db.prepare(`
  SELECT * FROM readings
  WHERE person_name = ?
  ORDER BY created_at DESC
`);

export default db;
