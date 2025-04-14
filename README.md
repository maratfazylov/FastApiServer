# FastAPI File Upload Server

A FastAPI-based web server that handles file uploads with content validation and preview generation.

## Features

- File upload with content-based validation (not just extension)
- Support for images and videos
- File retrieval by UUID
- Optional thumbnail generation for images

## Requirements

- Python 3.8+
- Dependencies listed in requirements.txt

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the server:

```bash
python server.py
```

The server will be available at http://localhost:8000

## Testing the API

You can test the API using the provided Python script:

```bash
python test_api.py
```

You'll need to provide test files:
- `cat_video.mp4` - a sample video file
- `cat_image.jpg` - a sample image file

## API Endpoints

### Upload a File

**Endpoint:** `PUT /api/upload`

**Parameters:**
- `file`: The file to upload (multipart form data)
- `file_type`: Type of file, either 'image' or 'video'

**Example request:**
```bash
curl -X PUT "http://localhost:8000/api/upload?file_type=image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg"
```

**Response:**
```json
{
  "uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "filename": "image.jpg",
  "file_type": "image",
  "content_type": "image/jpeg",
  "size": 12345
}
```

### Get a File

**Endpoint:** `GET /api/{file_uuid}`

**Parameters:**
- `file_uuid`: UUID of the file to retrieve
- `width` (optional): Width for the thumbnail
- `height` (optional): Height for the thumbnail

**Example requests:**

Get original file:
```bash
curl -X GET "http://localhost:8000/api/f47ac10b-58cc-4372-a567-0e02b2c3d479"
```

Get thumbnail:
```bash
curl -X GET "http://localhost:8000/api/f47ac10b-58cc-4372-a567-0e02b2c3d479?width=300&height=200"
```

The response will be the file content with appropriate content type headers.

## Supported File Types

### Images
- JPEG (image/jpeg)
- PNG (image/png)
- GIF (image/gif)
- WebP (image/webp)

### Videos
- MP4 (video/mp4)
- QuickTime (video/quicktime)
- AVI (video/x-msvideo)
- WebM (video/webm)

## Notes

- Thumbnail generation is currently supported only for images.
- File validation is done based on file content, not just extension.
- Files are stored with their UUIDs as filenames. 