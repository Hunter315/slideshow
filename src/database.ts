import Database from 'better-sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

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
    deleted_at INTEGER
  );

  CREATE INDEX IF NOT EXISTS idx_status ON photos(status);
  CREATE INDEX IF NOT EXISTS idx_uploaded_at ON photos(uploaded_at);
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

export default db;
