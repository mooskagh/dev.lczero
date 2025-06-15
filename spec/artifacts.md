 # Requirements

"artifacts" is a Django app that is responsible for hosting GitHub CI build artifacts.
After a build is completed, the artifacts are uploaded to the server.
Every revision is built for several targets (e.g. different operating systems and different Lc0 backends).
The page should display the artifacts as a table (revisions are rows, targets are columns).

The revision contains the following information:
- Commit hash
- Datetime
- optionally the PR number
- optionally, tag/description
- Whether the revision is pinned
- Whether the revision is scheduled for deletion
- Whether the revision is hidden

The target contains the following information:
- target id
- target name

The artifacts contain the following information:
- Filename
- Size
- Download link

Periodically (daily), we run janitor task, which:
- Deletes all revisions that are scheduled for deletion
- Deletes all revisions that are older than 30 days (configurable), which are not pinned
- Deletes all revisions that are older than 7 days (configurable) and not the latest revision for a given PR, which are not pinned

You'll need to create a Django permission that would allow users to pin/hide/schedule revisions for deletion (one permission for all three actions)
All other users should be able to view/download artifacts.

Artifacts will be uploaded one by one through HTTP POST requests.
The artifacts will be large (hundreds of MBs), so you should use streaming uploads, the location should be configurable (i.e. not the standard MEDIA_ROOT, and the files should be located in a file system, not in a database).

# Implementation Plan

## Phase 1: Django App Setup and Models
1. **Create Django app structure**
   - Create `artifacts` Django app
   - Add to `INSTALLED_APPS` in settings
   - Create app directory structure

2. **Database Models**
   - `Target` model: id, name
   - `Revision` model: commit_hash, datetime, pr_number (optional), tag/description (optional), is_pinned, is_scheduled_for_deletion, is_hidden
   - `Artifact` model: revision (FK), target (FK), filename, file_path, size, created_at
   - Create and run migrations

3. **Settings Configuration**
   - Add `ARTIFACTS_STORAGE_PATH` setting for configurable file storage location
   - Add `ARTIFACTS_UPLOAD_TOKEN` for authentication
   - Add `ARTIFACTS_DOWNLOAD_URL_PREFIX` for nginx-served files
   - Add retention period settings (30 days, 7 days) as configurable options

## Phase 2: File Storage and Upload System
1. **Storage Backend**
   - Store files directly to filesystem at `ARTIFACTS_STORAGE_PATH`
   - Generate file paths: `{target_id}/{revision_hash}/{uuid4()}-{filename}`
   - Handle file cleanup when artifacts are deleted

2. **Upload API Endpoint**
   - Create streaming upload view for large files
   - Token-based authentication using `ARTIFACTS_UPLOAD_TOKEN`
   - Accept POST requests with multipart/form-data
   - Store file with generated path and save metadata
   - Add proper error handling and logging

3. **File Serving**
   - Create download redirect view (302 redirect to nginx-served location)
   - Generate download URLs: `{ARTIFACTS_DOWNLOAD_URL_PREFIX}/{file_path}`
   - Add security checks (file exists, not hidden, etc.)

## Phase 3: Main Table Interface
1. **Single Table View**
   - Create main artifacts table view (revisions × targets matrix)
   - Show revision metadata and artifact download links
   - Add "Cleanup Status" column showing when revision will be janitored ("in 3 days", "pinned", "scheduled for deletion")
   - For regular users: show pin icons for pinnable revisions
   - For admins: show checkboxes for pin/hide/schedule-for-deletion
   - Add "Save" button for admin bulk actions
   - Add "Run Janitor Now" button for admins

2. **Frontend Components**
   - Responsive table with revisions as rows, targets as columns
   - AJAX forms for admin actions (no page refresh)
   - Visual indicators for revision status (pinned/hidden/scheduled)
   - File size and download count display
   - Cleanup status with color coding (red for imminent deletion, green for pinned)

3. **Admin Interface**
   - Register models with Django admin for basic CRUD
   - Keep main functionality in the table view

## Phase 4: Permissions and User Management
1. **Permission System**
   - Create custom permission: `artifacts.manage_revisions`
   - Apply permission checks to management actions
   - Integrate with existing Discord authentication
   - Show different UI based on user permissions

## Phase 5: Janitor Task System
1. **Management Command**
   - Create Django management command for cleanup
   - Implement deletion logic:
     - Delete revisions scheduled for deletion
     - Delete unpinned revisions > 30 days old
     - Delete unpinned PR revisions > 7 days old (except latest per PR)
   - Delete both database records and actual files
   - Add dry-run mode and logging

2. **Manual Janitor Trigger**
   - Add view for "Run Janitor Now" button
   - Execute janitor task immediately with progress feedback
   - Show cleanup results to admin

## Phase 6: Testing and Documentation
1. **Unit Tests**
   - Model tests for business logic
   - View tests for upload/download/management
   - Permission tests
   - File operation tests

2. **Integration Tests**
   - Full upload/download flow
   - Janitor task execution
   - Admin interface interactions

## Database Schema

### Target Model
```python
class Target(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Revision Model
```python
class Revision(models.Model):
    commit_hash = models.CharField(max_length=40, unique=True)
    datetime = models.DateTimeField()
    pr_number = models.IntegerField(null=True, blank=True)
    tag_description = models.CharField(max_length=200, blank=True)
    is_pinned = models.BooleanField(default=False)
    is_scheduled_for_deletion = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def days_until_cleanup(self):
        from django.utils import timezone
        from django.conf import settings
        
        if self.is_scheduled_for_deletion:
            return 0
        if self.is_pinned:
            return None
        
        now = timezone.now()
        age = now - self.datetime
        
        # Check if it's the latest for a PR
        if self.pr_number:
            latest_for_pr = Revision.objects.filter(
                pr_number=self.pr_number
            ).order_by('-datetime').first()
            if self == latest_for_pr:
                pr_cutoff = timezone.timedelta(days=settings.ARTIFACTS_PR_RETENTION_DAYS)
                if age < pr_cutoff:
                    return (pr_cutoff - age).days
        
        # General retention
        general_cutoff = timezone.timedelta(days=settings.ARTIFACTS_RETENTION_DAYS)
        if age < general_cutoff:
            return (general_cutoff - age).days
        
        return 0
```

### Artifact Model
```python
class Artifact(models.Model):
    revision = models.ForeignKey(Revision, on_delete=models.CASCADE)
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)  # User-visible filename
    file_path = models.CharField(max_length=500)  # Server storage path
    size = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['revision', 'target', 'filename']
    
    @property
    def download_url(self):
        return f"{settings.ARTIFACTS_DOWNLOAD_URL_PREFIX}/{self.file_path}"
```

## URL Structure
- `/artifacts/` - Main table view
- `/artifacts/download/<int:artifact_id>/` - Download redirect
- `/artifacts/upload/` - Upload endpoint (POST)
- `/artifacts/manage/` - AJAX endpoints for admin actions
- `/artifacts/janitor/` - Manual janitor trigger

## Configuration Settings
```python
# Artifacts configuration
ARTIFACTS_STORAGE_PATH = env.str('ARTIFACTS_STORAGE_PATH', '/var/artifacts/')
ARTIFACTS_UPLOAD_TOKEN = env.str('ARTIFACTS_UPLOAD_TOKEN')
ARTIFACTS_DOWNLOAD_URL_PREFIX = env.str('ARTIFACTS_DOWNLOAD_URL_PREFIX', '/static/artifacts')
ARTIFACTS_RETENTION_DAYS = env.int('ARTIFACTS_RETENTION_DAYS', 30)
ARTIFACTS_PR_RETENTION_DAYS = env.int('ARTIFACTS_PR_RETENTION_DAYS', 7)
ARTIFACTS_MAX_FILE_SIZE = env.int('ARTIFACTS_MAX_FILE_SIZE', 1024*1024*1024)  # 1GB
```

## Upload Example
```bash
curl -X POST \
  -H "Authorization: Bearer ${ARTIFACTS_UPLOAD_TOKEN}" \
  -F "file=@/path/to/lc0-windows.exe" \
  -F "filename=lc0-windows.exe" \
  -F "target_id=windows-cpu" \
  -F "commit_hash=abc123..." \
  -F "datetime=2024-01-01T12:00:00Z" \
  -F "pr_number=1234" \
  -F "tag_description=Release v1.0" \
  https://dev.lczero.org/artifacts/upload/
```

## Nginx Configuration
```nginx
location /static/artifacts/ {
    alias /var/artifacts/;
    expires 1d;
    add_header Cache-Control "public, immutable";
}
```