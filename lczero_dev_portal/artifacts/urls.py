from django.urls import path

from .views import DownloadView, UploadView, artifacts_table_view

app_name = "artifacts"

urlpatterns = [
    path("", artifacts_table_view, name="table"),
    path("upload/", UploadView.as_view(), name="upload"),
    path(
        "download/<int:artifact_id>/", DownloadView.as_view(), name="download"
    ),
]
