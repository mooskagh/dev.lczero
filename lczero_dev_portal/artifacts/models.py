from django.conf import settings
from django.db import models


class Target(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"


class Revision(models.Model):
    commit_hash = models.CharField(max_length=40, unique=True)
    datetime = models.DateTimeField()
    pr_number = models.IntegerField(null=True, blank=True)
    tag_description = models.TextField(blank=True)
    is_pinned = models.BooleanField(default=False)
    is_scheduled_for_deletion = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.commit_hash[:8]} ({self.datetime})"

    class Meta:
        ordering = ["-datetime"]


class Artifact(models.Model):
    revision = models.ForeignKey(Revision, on_delete=models.CASCADE)
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    file_path = models.TextField()
    size = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["revision", "target", "filename"]

    def __str__(self) -> str:
        return (
            f"{self.filename} "
            f"({self.revision.commit_hash[:8]} - {self.target.id})"
        )

    @property
    def download_url(self) -> str:
        download_prefix = getattr(
            settings, "ARTIFACTS_DOWNLOAD_URL_PREFIX", "/static/artifacts"
        )
        return f"{download_prefix}/{self.file_path}"
