from django.urls import path

from .views import DownloadView, UploadView

app_name = "artifacts"

urlpatterns = [
    path("upload/", UploadView.as_view(), name="upload"),
    path(
        "download/<int:artifact_id>/", DownloadView.as_view(), name="download"
    ),
]
