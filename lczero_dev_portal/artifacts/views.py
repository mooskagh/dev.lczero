import logging
from datetime import datetime
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .helpers import get_artifacts_table_data
from .models import Artifact, Revision, Target
from .utils import (
    delete_file_if_exists,
    ensure_directory_exists,
    generate_file_path,
)

logger = logging.getLogger(__name__)


def authenticate_upload_token(request: HttpRequest) -> bool:
    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth_header.startswith("Bearer "):
        return False

    token = auth_header.removeprefix("Bearer ")
    return token == settings.ARTIFACTS_UPLOAD_TOKEN


def parse_upload_parameters(request: HttpRequest) -> dict[str, Any]:
    file_data = request.FILES["file"]
    if isinstance(file_data, list):
        raise ValueError("Multiple files not supported")
    uploaded_file: UploadedFile = file_data

    return {
        "file": uploaded_file,
        "filename": request.POST.get("filename", uploaded_file.name),
        "target_id": request.POST["target_id"],
        "commit_hash": request.POST["commit_hash"],
        "revision_datetime": (
            datetime.fromisoformat(request.POST["datetime"])
            if request.POST.get("datetime")
            else timezone.now()
        ),
        "pr_number": (
            int(request.POST["pr_number"])
            if request.POST.get("pr_number")
            else None
        ),
        "tag_description": request.POST.get("tag_description") or None,
    }


def create_revision_and_target(
    params: dict[str, Any],
) -> tuple[Revision, Target]:
    target, _ = Target.objects.get_or_create(
        id=params["target_id"], defaults={"name": params["target_id"]}
    )

    revision, _ = Revision.objects.get_or_create(
        commit_hash=params["commit_hash"],
        defaults={
            "datetime": params["revision_datetime"],
            "pr_number": params["pr_number"],
            "tag_description": params["tag_description"],
        },
    )

    return revision, target


def delete_existing_artifact(
    revision: Revision, target: Target, filename: str
) -> None:
    try:
        existing_artifact = Artifact.objects.get(
            revision=revision, target=target, filename=filename
        )
    except Artifact.DoesNotExist:
        return

    delete_file_if_exists(existing_artifact.file_path)
    existing_artifact.delete()


def save_uploaded_file(uploaded_file: Any, file_path: str) -> None:
    full_path = ensure_directory_exists(file_path)

    with open(full_path, "wb") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)


@method_decorator(csrf_exempt, name="dispatch")
class UploadView(View):
    def post(self, request: HttpRequest) -> JsonResponse:
        if not authenticate_upload_token(request):
            return JsonResponse(
                {"error": "Invalid or missing authorization token"}, status=401
            )

        if "file" not in request.FILES:
            return JsonResponse({"error": "No file provided"}, status=400)

        file_data = request.FILES["file"]
        if isinstance(file_data, list):
            return JsonResponse(
                {"error": "Multiple files not supported"}, status=400
            )
        uploaded_file: UploadedFile = file_data
        if uploaded_file.size > settings.ARTIFACTS_MAX_FILE_SIZE:
            return JsonResponse(
                {
                    "error": (
                        "File too large. Maximum size:"
                        f" {settings.ARTIFACTS_MAX_FILE_SIZE} bytes"
                    )
                },
                status=413,
            )

        try:
            params = parse_upload_parameters(request)
            revision, target = create_revision_and_target(params)
            file_path = generate_file_path(
                revision.pk, target.pk, params["filename"]
            )

            delete_existing_artifact(revision, target, params["filename"])
            save_uploaded_file(params["file"], file_path)

            artifact = Artifact.objects.create(
                revision=revision,
                target=target,
                filename=params["filename"],
                file_path=file_path,
                size=params["file"].size,
            )

            logger.info(
                f"Uploaded artifact: {params['filename']} for"
                f" {params['commit_hash']} ({params['target_id']})"
            )

            return JsonResponse({
                "success": True,
                "artifact_id": artifact.pk,
                "file_path": file_path,
                "size": params["file"].size,
            })

        except (KeyError, ValueError) as e:
            return JsonResponse(
                {"error": f"Missing or invalid parameters: {str(e)}"},
                status=400,
            )
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            return JsonResponse(
                {"error": f"Upload failed: {str(e)}"}, status=500
            )


def artifacts_table_view(request: HttpRequest):
    targets, matrix = get_artifacts_table_data()

    context = {
        "targets": targets,
        "matrix": matrix,
        "can_manage": (
            request.user.is_authenticated
            and hasattr(request.user, "has_perm")
            and request.user.has_perm("artifacts.manage_revisions")
        ),
    }

    return render(request, "artifacts/table.html", context)


@permission_required("artifacts.manage_revisions")
def bulk_manage_view(request: HttpRequest):
    if request.method != "POST":
        return redirect("artifacts:table")

    # Get all revision updates from form
    revision_updates: dict[int, dict[str, bool]] = {}
    for key, value in request.POST.items():
        if key.startswith("revision_"):
            parts = key.split("_")
            if len(parts) == 3:  # revision_{id}_{field}
                revision_id = int(parts[1])
                field = parts[2]
                if revision_id not in revision_updates:
                    revision_updates[revision_id] = {}
                revision_updates[revision_id][field] = value == "on"

    # Update revisions
    count = 0
    for revision_id, updates in revision_updates.items():
        fields = {
            "is_hidden": updates.get("hidden", False),
            "is_scheduled_for_deletion": updates.get("deletion", False),
            "is_pinned": updates.get("pinned", False),
        }
        Revision.objects.filter(id=revision_id).update(**fields)
        count += 1

    messages.success(request, f"Updated {count} revision(s).")
    return redirect("artifacts:table")


@permission_required("artifacts.manage_revisions")
def run_janitor_view(request: HttpRequest):
    if request.method != "POST":
        return redirect("artifacts:table")

    # TODO: Implement actual janitor logic in Phase 5
    messages.info(
        request, "Janitor functionality will be implemented in Phase 5."
    )
    return redirect("artifacts:table")
