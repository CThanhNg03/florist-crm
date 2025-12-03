from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable
from uuid import uuid4

import aiofiles
from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings

ALLOWED_CONTENT_TYPES: Iterable[str] = ("image/jpeg", "image/png", "image/webp")


class LocalStorage:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_path: Path = settings.media_root
        self.base_url: str = settings.media_url.rstrip("/")
        self.completions_dir: Path = self.base_path / "completions"
        self.completions_dir.mkdir(parents=True, exist_ok=True)

    async def save_completion_image(self, task_id: int, upload: UploadFile) -> str:
        if upload.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported image type",
            )
        extension = self._extension_from_content_type(upload.content_type)
        filename = f"task-{task_id}-{uuid4().hex}{extension}"
        destination = self.completions_dir / filename

        async with aiofiles.open(destination, "wb") as outfile:
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                await outfile.write(chunk)

        return f"{self.base_url}/completions/{filename}"

    @staticmethod
    def _extension_from_content_type(content_type: str) -> str:
        mapping = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
        return mapping.get(content_type, os.path.splitext(content_type)[1] or ".jpg")
