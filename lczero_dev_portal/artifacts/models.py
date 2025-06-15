from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class RevisionManager(models.Manager):
    pass


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

    objects = RevisionManager()

    def __str__(self) -> str:
        return f"{self.commit_hash[:8]} ({self.datetime})"

    def days_until_cleanup(self):
        if self.is_scheduled_for_deletion or self.is_pinned:
            return None if self.is_pinned else 0

        age = timezone.now() - self.datetime
        retention_days = getattr(settings, "ARTIFACTS_RETENTION_DAYS", 30)
        pr_retention_days = getattr(settings, "ARTIFACTS_PR_RETENTION_DAYS", 7)

        # Latest PR revision gets PR retention period
        if (
            self.pr_number
            and self
            == Revision.objects.filter(pr_number=self.pr_number)
            .order_by("-datetime")
            .first()
        ):
            cutoff = timedelta(days=pr_retention_days)
        else:
            cutoff = timedelta(days=retention_days)

        return max(0, (cutoff - age).days)

    def cleanup_status_display(self):
        if self.is_pinned:
            return "(pinned)"

        days = self.days_until_cleanup()
        return "today" if days == 0 else f"in {days} days"

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
