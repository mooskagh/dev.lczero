from django.urls import path

from .views import (
    UploadView,
    artifacts_table_view,
    bulk_manage_view,
    run_janitor_view,
)

app_name = "artifacts"

urlpatterns = [
    path("", artifacts_table_view, name="table"),
    path("manage/", bulk_manage_view, name="bulk_manage"),
    path("janitor/", run_janitor_view, name="run_janitor"),
    path("upload/", UploadView.as_view(), name="upload"),
]
