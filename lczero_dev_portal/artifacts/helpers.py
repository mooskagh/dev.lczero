from dataclasses import dataclass
from typing import List, Optional

from .models import Artifact, Revision, Target


@dataclass
class ArtifactsTableRow:
    revision: Revision
    artifacts: List[Optional[Artifact]]


def get_artifacts_table_data(
    limit: int = 50,
) -> tuple[List[Target], List[ArtifactsTableRow]]:
    revisions = Revision.objects.filter(is_hidden=False).prefetch_related(
        "artifact_set__target"
    )[:limit]

    # Collect all target IDs
    target_ids = {
        artifact.target.id
        for revision in revisions
        for artifact in revision.artifact_set.all()
    }

    targets = list(Target.objects.filter(id__in=target_ids).order_by("id"))

    return targets, [
        ArtifactsTableRow(
            revision=revision,
            artifacts=[
                next(
                    (
                        a
                        for a in revision.artifact_set.all()
                        if a.target.id == target.id
                    ),
                    None,
                )
                for target in targets
            ],
        )
        for revision in revisions
    ]
