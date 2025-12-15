# Level 6: Form Data & File Uploads

## Learning Objectives
- Handle form data with `Form()`
- Upload single files with `File()` and `UploadFile`
- Upload multiple files
- Combine form fields with file uploads
- Validate file type and size
- Save uploaded files to disk
- Handle optional file uploads

---

## Setup Instructions

```bash
cd level_06_form_files
pip install -r requirements.txt
uvicorn main:app --reload
```

**Testing:** Open http://127.0.0.1:8000 for HTML test forms, or use Swagger UI at `/docs`.

---

## Important: Form vs JSON

⚠️ **Form data and JSON body CANNOT be mixed in same request!**

| Use Case | Parameter Type |
|----------|---------------|
| JSON API | `Body()` or Pydantic model |
| HTML Form | `Form()` |
| File Upload | `File()` or `UploadFile` |
| Form + File | `Form()` + `File()` together ✅ |
| JSON + File | ❌ Not allowed |

---

## Key Concepts

### 1. Basic Form Fields
```python
from fastapi import Form

@app.post("/tasks/form")
def create_task(
    title: str = Form(...),              # Required
    description: str = Form(default=""), # Optional
    priority: int = Form(default=1)      # Optional with default
):
    return {"title": title}
```

**Content-Type:** `application/x-www-form-urlencoded`

### 2. Form with Validation
```python
@app.post("/login")
def login(
    username: str = Form(..., min_length=3, max_length=50),
    password: str = Form(..., min_length=8)
):
    return {"username": username}
```

### 3. File Upload (bytes) - Simple but Limited
```python
from fastapi import File

@app.post("/upload/bytes")
def upload_bytes(file: bytes = File(...)):
    return {"size": len(file)}
```

⚠️ Loads entire file into memory - use only for small files!

### 4. File Upload (UploadFile) - Recommended
```python
from fastapi import UploadFile

@app.post("/upload")
async def upload(file: UploadFile):
    content = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content)
    }
```

**UploadFile Attributes:**
| Attribute | Description |
|-----------|-------------|
| `filename` | Original filename |
| `content_type` | MIME type (e.g., `image/jpeg`) |
| `file` | SpooledTemporaryFile object |

**UploadFile Methods:**
| Method | Description |
|--------|-------------|
| `await read(size)` | Read bytes (all or chunk) |
| `await write(data)` | Write data |
| `await seek(offset)` | Move to position |
| `await close()` | Close file |

### 5. Multiple File Uploads
```python
from typing import List

@app.post("/upload/multiple")
async def upload_many(files: List[UploadFile]):
    for file in files:
        content = await file.read()
        # Process each file
    return {"count": len(files)}
```

**HTML:** `<input type="file" name="files" multiple>`

### 6. Optional File Upload
```python
from typing import Optional

@app.post("/tasks/with-attachment")
async def create_task(
    title: str = Form(...),
    attachment: Optional[UploadFile] = File(default=None)
):
    if attachment and attachment.filename:
        # Process file
        pass
    return {"title": title}
```

### 7. Form + File Combined
```python
@app.post("/profile/create")
async def create_profile(
    username: str = Form(...),
    email: str = Form(...),
    avatar: UploadFile = File(...)
):
    content = await avatar.read()
    # Save avatar
    return {"username": username}
```

### 8. File Type Validation
```python
ALLOWED_TYPES = ["image/jpeg", "image/png"]

@app.post("/upload/image")
async def upload_image(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type"
        )
    return {"filename": file.filename}
```

### 9. File Size Validation
```python
MAX_SIZE = 5 * 1024 * 1024  # 5 MB

@app.post("/upload/limited")
async def upload_limited(file: UploadFile):
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large"
        )
    return {"size": len(content)}
```

### 10. Saving Files to Disk
```python
import os

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload(file: UploadFile):
    content = await file.read()
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {"saved_to": file_path}
```

### 11. Chunked Reading (Large Files)
```python
@app.post("/upload/large")
async def upload_large(file: UploadFile):
    file_path = f"uploads/{file.filename}"
    
    with open(file_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            f.write(chunk)
    
    return {"filename": file.filename}
```

---

## Common MIME Types

| Extension | MIME Type |
|-----------|-----------|
| `.jpg`, `.jpeg` | `image/jpeg` |
| `.png` | `image/png` |
| `.gif` | `image/gif` |
| `.pdf` | `application/pdf` |
| `.doc` | `application/msword` |
| `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| `.txt` | `text/plain` |
| `.json` | `application/json` |
| `.zip` | `application/zip` |

---

## HTML Form Requirements

For file uploads, HTML form must have:
```html
<form action="/upload" method="post" enctype="multipart/form-data">
    <input type="file" name="file">
    <button type="submit">Upload</button>
</form>
```

**Important:** `enctype="multipart/form-data"` is required for file uploads!

---

## Test Endpoints

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000 | HTML test forms |
| http://127.0.0.1:8000/docs | Swagger UI |

### Test Scenarios

1. **Basic Form:** `/tasks/form`
2. **Login (validation):** `/login`
3. **Single File:** `/upload`
4. **Multiple Files:** `/upload/multiple`
5. **Optional File:** `/tasks/with-attachment`
6. **Form + File:** `/profile/create`
7. **Image Only:** `/upload/image`
8. **Size Limited:** `/upload/limited`
9. **Document:** `/upload/document`

---

## Exercises

### Exercise 1: Product Image Upload
Create `POST /products` with:
- `name`: Form field (required)
- `price`: Form field (required, float)
- `image`: File upload (required, images only)

### Exercise 2: Resume Upload
Create `POST /applications` with:
- `name`: Form field
- `email`: Form field
- `position`: Form field
- `resume`: File (PDF only, max 2MB)
- `cover_letter`: Optional file

### Exercise 3: Gallery Upload
Create `POST /gallery` with:
- `album_name`: Form field
- `images`: Multiple files (images only, max 10 files)

### Exercise 4: File Rename
Create endpoint that:
- Accepts file upload
- Accepts new filename as form field
- Saves file with new name

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `422 - value is not a valid file` | Missing file | Ensure file is attached |
| `400 - Invalid file type` | Wrong MIME type | Use correct file type |
| No `python-multipart` | Missing dependency | `pip install python-multipart` |
| Form data empty | Missing enctype | Add `enctype="multipart/form-data"` |
| File not saving | Permission issue | Check write permissions |

---

## Best Practices

1. **Always validate** file type and size
2. **Use UploadFile** over bytes for efficiency
3. **Generate unique filenames** to prevent overwrites
4. **Set size limits** to prevent abuse
5. **Scan files** for malware in production
6. **Use cloud storage** (S3, GCS) for production

---

## What's Next?
**Level 7: Advanced Validation** - Learn `Path()`, `Query()`, `Field()` validators with constraints, patterns, and custom validation.
