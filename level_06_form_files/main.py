"""
Level 6: Form Data & File Uploads
=================================
Concepts Covered:
    - Form fields with Form()
    - Single file upload with File() and UploadFile
    - Multiple file uploads
    - Combining form data with files
    - File validation (type, size)
    - Optional file uploads
    - Saving uploaded files

Installation:
    pip install python-multipart

Run Command:
    uvicorn main:app --reload

Important:
    Form data and JSON body CANNOT be mixed in same request!
    Use either Form() OR Body(), not both.
"""

from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from typing import Optional, List
from pydantic import BaseModel
import os
import shutil
from datetime import datetime

app = FastAPI(
    title="Task Manager API - Level 6",
    description="Learning Form Data & File Uploads",
    version="6.0.0"
)

# ============================================================
# Setup: Create uploads directory
# ============================================================

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# CONCEPT 1: Basic Form Fields
# ============================================================
# Form() is used instead of Body() for form data
# Requires: pip install python-multipart

@app.post("/tasks/form")
def create_task_form(
    title: str = Form(...),                    # Required
    description: str = Form(default=""),       # Optional with default
    priority: int = Form(default=1)            # Optional with default
):
    """
    Create task using form data (not JSON)
    
    Content-Type: application/x-www-form-urlencoded
    
    Form fields:
    - title: Required
    - description: Optional (default: "")
    - priority: Optional (default: 1)
    
    Use HTML form or Swagger UI to test
    """
    return {
        "message": "Task created from form",
        "task": {
            "title": title,
            "description": description,
            "priority": priority
        }
    }


# ============================================================
# CONCEPT 2: Form with Validation
# ============================================================

@app.post("/login")
def login(
    username: str = Form(..., min_length=3, max_length=50),
    password: str = Form(..., min_length=8)
):
    """
    Login form with validation
    
    - username: 3-50 characters required
    - password: minimum 8 characters required
    
    Note: In production, NEVER log passwords!
    """
    # Simulate authentication
    if username == "admin" and password == "password123":
        return {
            "message": "Login successful",
            "username": username,
            "token": "fake-jwt-token-12345"
        }
    
    return {"error": "Invalid credentials"}


# ============================================================
# CONCEPT 3: Single File Upload (bytes)
# ============================================================
# File as bytes - loads entire file into memory
# Good for small files only

@app.post("/upload/bytes")
def upload_file_bytes(
    file: bytes = File(..., description="File content as bytes")
):
    """
    Upload file as bytes (simple but memory intensive)
    
    - Entire file loaded into memory
    - Good for small files only (<1MB)
    - No filename or content-type info available
    """
    return {
        "file_size_bytes": len(file),
        "file_size_kb": round(len(file) / 1024, 2),
        "message": "File received as bytes"
    }


# ============================================================
# CONCEPT 4: Single File Upload (UploadFile) - Recommended
# ============================================================
# UploadFile is more efficient and provides metadata

@app.post("/upload")
async def upload_file(file: UploadFile):
    """
    Upload file using UploadFile (recommended)
    
    Benefits over bytes:
    - Spooled file (memory efficient)
    - Access to filename, content_type
    - Async read methods
    - File-like interface
    
    UploadFile attributes:
    - filename: Original filename
    - content_type: MIME type (image/jpeg, etc.)
    - file: SpooledTemporaryFile
    """
    # Read file content
    content = await file.read()
    
    # Save to disk
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(content),
        "size_kb": round(len(content) / 1024, 2),
        "saved_to": file_path
    }


# ============================================================
# CONCEPT 5: Multiple File Uploads
# ============================================================

@app.post("/upload/multiple")
async def upload_multiple_files(files: List[UploadFile]):
    """
    Upload multiple files at once
    
    HTML: <input type="file" name="files" multiple>
    
    Returns info about each uploaded file
    """
    results = []
    total_size = 0
    
    for file in files:
        content = await file.read()
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        size = len(content)
        total_size += size
        
        results.append({
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": size
        })
    
    return {
        "total_files": len(files),
        "total_size_bytes": total_size,
        "total_size_kb": round(total_size / 1024, 2),
        "files": results
    }


# ============================================================
# CONCEPT 6: Optional File Upload
# ============================================================

@app.post("/tasks/with-attachment")
async def create_task_with_optional_file(
    title: str = Form(...),
    description: str = Form(default=""),
    attachment: Optional[UploadFile] = File(default=None)
):
    """
    Create task with optional file attachment
    
    - title: Required
    - description: Optional
    - attachment: Optional file
    
    File is saved only if provided
    """
    result = {
        "title": title,
        "description": description,
        "has_attachment": False,
        "attachment": None
    }
    
    if attachment and attachment.filename:
        content = await attachment.read()
        file_path = os.path.join(UPLOAD_DIR, attachment.filename)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        result["has_attachment"] = True
        result["attachment"] = {
            "filename": attachment.filename,
            "content_type": attachment.content_type,
            "size_bytes": len(content),
            "saved_to": file_path
        }
    
    return result


# ============================================================
# CONCEPT 7: Form + File Combined
# ============================================================

@app.post("/profile/create")
async def create_profile(
    username: str = Form(..., min_length=3),
    email: str = Form(...),
    bio: str = Form(default=""),
    avatar: UploadFile = File(...)
):
    """
    Create profile with form data and file
    
    Form fields:
    - username: Required (min 3 chars)
    - email: Required
    - bio: Optional
    
    File:
    - avatar: Required image file
    """
    # Save avatar
    avatar_content = await avatar.read()
    avatar_filename = f"{username}_{avatar.filename}"
    avatar_path = os.path.join(UPLOAD_DIR, avatar_filename)
    
    with open(avatar_path, "wb") as f:
        f.write(avatar_content)
    
    return {
        "message": "Profile created",
        "profile": {
            "username": username,
            "email": email,
            "bio": bio,
            "avatar": {
                "filename": avatar_filename,
                "content_type": avatar.content_type,
                "size_bytes": len(avatar_content),
                "path": avatar_path
            }
        }
    }


# ============================================================
# CONCEPT 8: File Validation (Type)
# ============================================================

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]

@app.post("/upload/image")
async def upload_image(
    file: UploadFile = File(..., description="Image file only")
):
    """
    Upload image with type validation
    
    Allowed types: JPEG, PNG, GIF, WebP
    
    Returns error if file type not allowed
    """
    # Validate content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid file type",
                "allowed_types": ALLOWED_IMAGE_TYPES,
                "received_type": file.content_type
            }
        )
    
    content = await file.read()
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {
        "message": "Image uploaded successfully",
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(content)
    }


# ============================================================
# CONCEPT 9: File Validation (Size)
# ============================================================

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

@app.post("/upload/limited")
async def upload_limited_size(
    file: UploadFile = File(..., description="Max 5MB")
):
    """
    Upload file with size limit
    
    Maximum file size: 5 MB
    
    Returns error if file exceeds limit
    """
    content = await file.read()
    file_size = len(content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "File too large",
                "max_size_mb": MAX_FILE_SIZE / (1024 * 1024),
                "received_size_mb": round(file_size / (1024 * 1024), 2)
            }
        )
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "size_mb": round(file_size / (1024 * 1024), 2)
    }


# ============================================================
# CONCEPT 10: Combined Type + Size Validation
# ============================================================

ALLOWED_DOC_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
]
MAX_DOC_SIZE = 10 * 1024 * 1024  # 10 MB

@app.post("/upload/document")
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(default="general")
):
    """
    Upload document with full validation
    
    Allowed types: PDF, DOC, DOCX, TXT
    Max size: 10 MB
    
    Also accepts category as form field
    """
    # Validate type
    if file.content_type not in ALLOWED_DOC_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid document type",
                "allowed_types": ["PDF", "DOC", "DOCX", "TXT"],
                "received_type": file.content_type
            }
        )
    
    # Read and validate size
    content = await file.read()
    if len(content) > MAX_DOC_SIZE:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Document too large",
                "max_size_mb": 10,
                "received_size_mb": round(len(content) / (1024 * 1024), 2)
            }
        )
    
    # Save with category prefix
    filename = f"{category}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {
        "message": "Document uploaded",
        "category": category,
        "filename": filename,
        "content_type": file.content_type,
        "size_kb": round(len(content) / 1024, 2)
    }


# ============================================================
# CONCEPT 11: Streaming Large Files (Chunked)
# ============================================================

@app.post("/upload/large")
async def upload_large_file(file: UploadFile):
    """
    Upload large file using chunked reading
    
    Reads file in chunks to avoid memory issues
    Suitable for files of any size
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    total_size = 0
    chunk_size = 1024 * 1024  # 1 MB chunks
    
    with open(file_path, "wb") as f:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            total_size += len(chunk)
    
    return {
        "message": "Large file uploaded",
        "filename": file.filename,
        "size_mb": round(total_size / (1024 * 1024), 2),
        "method": "chunked_streaming"
    }


# ============================================================
# HTML Test Forms (for easy testing)
# ============================================================

@app.get("/", response_class=HTMLResponse)
def test_forms():
    """HTML forms for testing uploads"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Level 6 - Form & File Upload Tests</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        .form-section { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 8px; }
        h3 { margin-top: 0; color: #333; }
        input, button { margin: 5px 0; padding: 8px; }
        button { background: #007bff; color: white; border: none; cursor: pointer; border-radius: 4px; }
        button:hover { background: #0056b3; }
        label { display: block; margin-top: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>📁 Level 6: Form Data & File Uploads</h1>
    
    <div class="form-section">
        <h3>1. Basic Form (No File)</h3>
        <form action="/tasks/form" method="post">
            <label>Title (required):</label>
            <input type="text" name="title" required>
            <label>Description:</label>
            <input type="text" name="description">
            <label>Priority:</label>
            <input type="number" name="priority" value="1" min="1" max="5">
            <br><button type="submit">Create Task</button>
        </form>
    </div>
    
    <div class="form-section">
        <h3>2. Login Form (Validation)</h3>
        <form action="/login" method="post">
            <label>Username (3-50 chars):</label>
            <input type="text" name="username" required minlength="3">
            <label>Password (min 8 chars):</label>
            <input type="password" name="password" required minlength="8">
            <br><button type="submit">Login</button>
        </form>
    </div>
    
    <div class="form-section">
        <h3>3. Single File Upload</h3>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <label>Select file:</label>
            <input type="file" name="file" required>
            <br><button type="submit">Upload</button>
        </form>
    </div>
    
    <div class="form-section">
        <h3>4. Multiple Files Upload</h3>
        <form action="/upload/multiple" method="post" enctype="multipart/form-data">
            <label>Select files:</label>
            <input type="file" name="files" multiple required>
            <br><button type="submit">Upload All</button>
        </form>
    </div>
    
    <div class="form-section">
        <h3>5. Task with Optional Attachment</h3>
        <form action="/tasks/with-attachment" method="post" enctype="multipart/form-data">
            <label>Title:</label>
            <input type="text" name="title" required>
            <label>Description:</label>
            <input type="text" name="description">
            <label>Attachment (optional):</label>
            <input type="file" name="attachment">
            <br><button type="submit">Create Task</button>
        </form>
    </div>
    
    <div class="form-section">
        <h3>6. Profile with Avatar</h3>
        <form action="/profile/create" method="post" enctype="multipart/form-data">
            <label>Username:</label>
            <input type="text" name="username" required minlength="3">
            <label>Email:</label>
            <input type="email" name="email" required>
            <label>Bio:</label>
            <input type="text" name="bio">
            <label>Avatar (required):</label>
            <input type="file" name="avatar" accept="image/*" required>
            <br><button type="submit">Create Profile</button>
        </form>
    </div>
    
    <div class="form-section">
        <h3>7. Image Upload (Type Validated)</h3>
        <form action="/upload/image" method="post" enctype="multipart/form-data">
            <label>Image (JPEG, PNG, GIF, WebP):</label>
            <input type="file" name="file" accept="image/*" required>
            <br><button type="submit">Upload Image</button>
        </form>
    </div>
    
    <div class="form-section">
        <h3>8. Document Upload (Type + Size)</h3>
        <form action="/upload/document" method="post" enctype="multipart/form-data">
            <label>Category:</label>
            <input type="text" name="category" value="general">
            <label>Document (PDF, DOC, DOCX, TXT - Max 10MB):</label>
            <input type="file" name="file" accept=".pdf,.doc,.docx,.txt" required>
            <br><button type="submit">Upload Document</button>
        </form>
    </div>
    
    <p style="margin-top: 30px; color: #666;">
        💡 Also try <a href="/docs">Swagger UI</a> for API testing
    </p>
</body>
</html>
    """
