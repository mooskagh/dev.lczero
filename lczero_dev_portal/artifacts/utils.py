from pathlib import Path

from django.conf import settings


def generate_file_path(revision_id, target_id, filename):
    """
    Generate file path for storing artifacts.
    Format: {revision_id}/{target_id}/{filename}
    """
    return f"{revision_id}/{target_id}/{filename}"


def get_full_file_path(file_path):
    """
    Get full filesystem path for a file_path.
    """
    storage_path = Path(settings.ARTIFACTS_STORAGE_PATH)
    return storage_path / file_path


def ensure_directory_exists(file_path):
    """
    Ensure the directory structure exists for a file path.
    """
    full_path = get_full_file_path(file_path)
    full_path.parent.mkdir(parents=True, exist_ok=True)
    return full_path


def delete_file_if_exists(file_path):
    """
    Delete a file if it exists.
    """
    try:
        full_path = get_full_file_path(file_path)
        if full_path.exists():
            full_path.unlink()
            return True
    except OSError:
        pass
    return False


def cleanup_empty_directories(file_path):
    """
    Remove empty parent directories after file deletion.
    """
    try:
        full_path = get_full_file_path(file_path)
        parent = full_path.parent
        while parent != Path(settings.ARTIFACTS_STORAGE_PATH):
            if parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent
            else:
                break
    except OSError:
        pass
