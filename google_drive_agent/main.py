from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

app = FastAPI(
    title="Google Drive Agent",
    description="An agent that interacts with Google Drive to retrieve and read documents.",
    version="1.0.0",
)

# --- Global variable to store the Google Drive service object ---
global_drive_service = None

# --- Pydantic Models ---
class CredentialsRequest(BaseModel):
    credentials_json: str

class CreateTextFileRequest(BaseModel):
    file_name: str
    content: str
    mime_type: str = 'application/vnd.google-apps.document' # Default to Google Doc
    folder_id: str | None = None

class CreateFolderRequest(BaseModel):
    folder_name: str
    parent_folder_id: str | None = None

# --- Helper Functions ---
def initialize_drive_service(creds_json: str):
    global global_drive_service
    try:
        creds_info = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(
            creds_info,
            scopes=['https://www.googleapis.com/auth/drive'] # Full access for creating/writing
        )
        global_drive_service = build('drive', 'v3', credentials=creds)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Google Drive service: {e}")

# --- API Endpoints ---
@app.post("/set_credentials", summary="Set Google Drive API credentials")
async def set_credentials(request: CredentialsRequest):
    initialize_drive_service(request.credentials_json)
    return {"status": "Google Drive credentials set successfully."}

@app.get("/list_files", summary="List files in Google Drive")
async def list_files(folder_id: str | None = None, search_query: str | None = None):
    if global_drive_service is None:
        raise HTTPException(status_code=400, detail="Google Drive credentials not set. Please call /set_credentials first.")
    try:
        query_parts = []
        if folder_id:
            query_parts.append(f"'{folder_id}' in parents")
        else:
            query_parts.append("'root' in parents") # Default to root if no folder_id

        if search_query:
            query_parts.append(f"name contains '{search_query}' or fullText contains '{search_query}'")

        query = " and ".join(query_parts)

        results = global_drive_service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name, mimeType)", q=query).execute()
        items = results.get('files', [])

        if not items:
            return {"message": "No files found.", "files": []}
        else:
            file_list = []
            for item in items:
                file_list.append({"id": item['id'], "name": item['name'], "mimeType": item['mimeType']})
            return {"message": "Files listed successfully.", "files": file_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {e}")

@app.get("/read_file/{file_id}", summary="Read content of a Google Drive file")
async def read_file(file_id: str):
    if global_drive_service is None:
        raise HTTPException(status_code=400, detail="Google Drive credentials not set. Please call /set_credentials first.")
    try:
        # Get file metadata to check mimeType
        file_metadata = global_drive_service.files().get(fileId=file_id, fields="mimeType,name").execute()
        mime_type = file_metadata.get('mimeType')
        file_name = file_metadata.get('name')

        # Only export text-based files for now
        if mime_type == 'application/vnd.google-apps.document':
            # Google Docs need to be exported as plain text or other format
            content = global_drive_service.files().export(fileId=file_id, mimeType='text/plain').execute()
            return {"file_id": file_id, "file_name": file_name, "mime_type": mime_type, "content": content.decode('utf-8')}
        elif mime_type.startswith('text/') or mime_type == 'application/json':
            # Directly download text files
            content = global_drive_service.files().get_media(fileId=file_id).execute()
            return {"file_id": file_id, "file_name": file_name, "mime_type": mime_type, "content": content.decode('utf-8')}
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type for reading: {mime_type}. Only text-based files and Google Docs are supported.")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file {file_id}: {e}")

@app.post("/create_text_file", summary="Create a new text-based file (e.g., Google Doc)")
async def create_text_file(request: CreateTextFileRequest):
    if global_drive_service is None:
        raise HTTPException(status_code=400, detail="Google Drive credentials not set. Please call /set_credentials first.")
    try:
        file_metadata = {
            'name': request.file_name,
            'mimeType': request.mime_type
        }
        if request.folder_id:
            file_metadata['parents'] = [request.folder_id]

        # Create the file
        file = global_drive_service.files().create(body=file_metadata, fields='id').execute()
        file_id = file.get('id')

        # Update the content of the file
        media_body = MediaIoBaseUpload(io.BytesIO(request.content.encode('utf-8')),
                                       mimetype='text/plain',
                                       resumable=True)
        
        global_drive_service.files().update(
            fileId=file_id,
            media_body=media_body,
            fields='id').execute()

        return {"status": "File created and content set successfully.", "file_id": file_id, "file_name": request.file_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create file: {e}")

@app.delete("/delete_file/{file_id}", summary="Delete a file from Google Drive")
async def delete_file(file_id: str):
    if global_drive_service is None:
        raise HTTPException(status_code=400, detail="Google Drive credentials not set. Please call /set_credentials first.")
    try:
        global_drive_service.files().delete(fileId=file_id).execute()
        return {"status": f"File {file_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file {file_id}: {e}")

@app.post("/create_folder", summary="Create a new folder in Google Drive")
async def create_folder(request: CreateFolderRequest):
    if global_drive_service is None:
        raise HTTPException(status_code=400, detail="Google Drive credentials not set. Please call /set_credentials first.")
    try:
        file_metadata = {
            'name': request.folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if request.parent_folder_id:
            file_metadata['parents'] = [request.parent_folder_id]

        folder = global_drive_service.files().create(body=file_metadata, fields='id, name').execute()
        return {"status": "Folder created successfully.", "folder_id": folder.get('id'), "folder_name": folder.get('name')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create folder: {e}")

@app.get("/health", summary="Health check endpoint")
async def health_check() -> dict:
    """Returns a success message to indicate that the agent is running."""
    return {"status": "ok"}