import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/v1/workspace", tags=["Workspace"])

# Security / Ignore patterns
IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
IGNORE_EXTS = {".exe", ".bin", ".pyc", ".pyo", ".pyd", ".db", ".sqlite"}

def get_project_root() -> Path:
    # Assuming we are in beta_pyramid_functional/B5_AgentTools
    return Path(__file__).resolve().parents[2]

class FileNode(BaseModel):
    name: str
    path: str
    type: str  # "file" or "directory"
    size: int = 0
    children: Optional[List["FileNode"]] = None

FileNode.update_forward_refs()

@router.get("/tree")
async def get_tree(root: Optional[str] = None):
    """Returns a recursive tree of the project directory."""
    try:
        base_path = Path(root) if root else get_project_root()
        if not base_path.exists():
            raise HTTPException(404, detail="Path not found")
            
        def build_tree(current_path: Path) -> FileNode:
            is_dir = current_path.is_dir()
            node = FileNode(
                name=current_path.name or str(current_path),
                path=str(current_path.relative_to(get_project_root())),
                type="directory" if is_dir else "file",
                size=current_path.stat().st_size if not is_dir else 0
            )
            
            if is_dir:
                node.children = []
                # Sort: Directories first, then files
                entries = sorted(list(current_path.iterdir()), key=lambda x: (not x.is_dir(), x.name.lower()))
                for entry in entries:
                    if entry.name in IGNORE_DIRS or entry.suffix in IGNORE_EXTS:
                        continue
                    node.children.append(build_tree(entry))
            return node

        return build_tree(base_path)
    except Exception as e:
        logging.error(f"[Workspace] Tree error: {e}")
        raise HTTPException(500, detail=str(e))

class FileReadResponse(BaseModel):
    content: str
    path: str
    size: int

@router.get("/file")
async def read_file(path: str = Query(..., description="Relative path from project root")):
    """Reads a text file from the workspace."""
    try:
        full_path = get_project_root() / path
        if not full_path.exists() or not full_path.is_file():
            raise HTTPException(404, detail="File not found")
        
        # Security check: ensure path is within project root
        if not str(full_path.resolve()).startswith(str(get_project_root().resolve())):
             raise HTTPException(403, detail="Access denied: outside of workspace")

        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        return FileReadResponse(
            content=content,
            path=path,
            size=len(content)
        )
    except Exception as e:
        logging.error(f"[Workspace] Read error: {e}")
        raise HTTPException(500, detail=str(e))

class FileWriteRequest(BaseModel):
    path: str
    content: str
    overwrite: bool = False

@router.post("/file")
async def write_file(req: FileWriteRequest):
    """
    Pre-checks a file write. 
    In Stage 4, this should NOT write directly but return a success status 
    indicating that the change is STAGED for UI approval.
    """
    try:
        full_path = get_project_root() / req.path
        
        # Security check: ensure path is within project root
        if not str(full_path.resolve()).startswith(str(get_project_root().resolve())):
             raise HTTPException(403, detail="Access denied: outside of workspace")

        # For MVP/Phase 4.1, we return 'staged' successfully.
        # The frontend will then call a specialized 'commit' endpoint once user approves.
        return {
            "status": "staged",
            "path": req.path,
            "can_write": True,
            "message": "Change staged. User approval required in the Workspace Tab."
        }
    except Exception as e:
        logging.error(f"[Workspace] Write stage error: {e}")
        raise HTTPException(500, detail=str(e))

@router.post("/commit")
async def commit_change(req: FileWriteRequest):
    """Actually writes the staged change to disk after user approval."""
    try:
        full_path = get_project_root() / req.path
        
        # Security check: ensure path is within project root
        if not str(full_path.resolve()).startswith(str(get_project_root().resolve())):
             raise HTTPException(403, detail="Access denied: outside of workspace")

        # Create directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(req.content)

        logging.info(f"[Workspace] Committed change to {req.path}")
        return {
            "status": "success",
            "path": req.path,
            "message": f"Successfully committed changes to {req.path}"
        }
    except Exception as e:
        logging.error(f"[Workspace] Commit error: {e}")
        raise HTTPException(500, detail=str(e))
