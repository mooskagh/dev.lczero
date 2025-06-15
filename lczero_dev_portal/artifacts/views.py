import logging
from datetime import datetime
from typing import Any, Dict, Tuple

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.http import (
    Http404,
    HttpRequest,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

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


def parse_upload_parameters(request: HttpRequest) -> Dict[str, Any]:
    uploaded_file: UploadedFile = request.FILES["file"]

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
    params: Dict[str, Any],
) -> Tuple[Revision, Target]:
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

        uploaded_file: UploadedFile = request.FILES["file"]
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

            return JsonResponse(
                {
                    "success": True,
                    "artifact_id": artifact.pk,
                    "file_path": file_path,
                    "size": params["file"].size,
                }
            )

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


class DownloadView(View):
    def get(
        self, request: HttpRequest, artifact_id: int
    ) -> HttpResponseRedirect:
        artifact = get_object_or_404(Artifact, id=artifact_id)

        if artifact.revision.is_hidden:
            raise Http404("Artifact not found")

        full_path = ensure_directory_exists(artifact.file_path)
        if not full_path.exists():
            raise Http404("File not found")

        return HttpResponseRedirect(artifact.download_url)
