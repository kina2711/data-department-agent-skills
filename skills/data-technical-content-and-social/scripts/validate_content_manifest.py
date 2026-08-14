#!/usr/bin/env python3
"""Validate content claims, evidence, artifact lineage, channel fit and release authority."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from itertools import combinations
from pathlib import Path


CLAIM_CLASSES = {"fact", "implementation-specific", "convention", "opinion", "hypothesis", "teaching-simplification"}
EVIDENCE_TYPES = {"official-source", "standard", "paper", "runtime-evidence", "test-report", "authority-record", "other"}
FACT_CLASSES = {"fact", "implementation-specific"}
CANONICAL_REVIEW_TYPES = {"technical-accuracy", "claim-traceability", "artifact-validity"}
CHANNEL_REVIEW_TYPES = CANONICAL_REVIEW_TYPES | {"voice-originality", "human-voice", "media-integrity", "platform-fit"}
CANONICAL_TEST_SCOPES = {"claim-traceability", "artifact-validity"}
CHANNEL_TEST_SCOPES = CANONICAL_TEST_SCOPES | {"editorial-depth", "human-voice", "media-contract", "platform-structure", "cross-channel-originality"}
DEFAULT_WORD_LIMITS = {"facebook": (500, 700), "linkedin": (200, 260), "substack": (1200, 2500)}
CHANNEL_LANGUAGES = {"facebook": "vi", "linkedin": "en", "substack": "en"}
MEDIA_ROLES = {"real", "illustration", "code"}
CODE_MATURITY = {"runnable-example", "code-reference", "pseudocode"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def indexed(items: object, key: str, label: str, errors: list[str]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    if not isinstance(items, list):
        errors.append(f"{label} must be an array")
        return result
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{label}[{index}] must be an object")
            continue
        identity = item.get(key)
        if not nonempty(identity):
            errors.append(f"{label}[{index}].{key} must be non-empty")
        elif identity in result:
            errors.append(f"duplicate {key}: {identity}")
        else:
            result[identity] = item
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_iso_date(value: object) -> bool:
    if not nonempty(value):
        return False
    try:
        datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def valid_locator(value: object) -> bool:
    if not nonempty(value):
        return False
    text = str(value).strip()
    return text.startswith(("https://", "http://")) or "/" in text or "\\" in text


def words(text: str) -> list[str]:
    return re.findall(r"\b[\w'-]+\b", text.lower(), flags=re.UNICODE)


def ngrams(text: str, size: int = 5) -> set[tuple[str, ...]]:
    tokens = words(text)
    return {tuple(tokens[index:index + size]) for index in range(max(0, len(tokens) - size + 1))}


def validate(document: object, artifact_root: Path | None = None, mode: str = "complete") -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["manifest root must be a JSON object"]

    for field in ("series_id", "episode_id", "owner", "canonical_artifact"):
        if not nonempty(document.get(field)):
            errors.append(f"{field} must be a non-empty string")

    requested = document.get("requested_channels")
    if not isinstance(requested, list) or not all(nonempty(item) for item in requested):
        errors.append("requested_channels must be an array of non-empty channel names")
        requested = []
    elif len(requested) != len(set(requested)):
        errors.append("requested_channels contains duplicates")

    evidence = indexed(document.get("evidence"), "evidence_id", "evidence", errors)
    evidence_snapshot_text: dict[str, str] = {}
    evidence_claim_supports: dict[str, dict[str, str]] = {}
    for evidence_id, item in evidence.items():
        if item.get("evidence_type") not in EVIDENCE_TYPES:
            errors.append(f"evidence {evidence_id} has invalid evidence_type")
        if not valid_locator(item.get("locator")):
            errors.append(f"evidence {evidence_id}.locator must be an HTTP(S) URL or local path")
        for field in ("locator", "snapshot_path", "content_sha256", "version_or_date", "verified_by", "verified_at"):
            if not nonempty(item.get(field)):
                errors.append(f"evidence {evidence_id}.{field} must be non-empty")
        if not SHA256_RE.fullmatch(str(item.get("content_sha256", "")).lower()):
            errors.append(f"evidence {evidence_id}.content_sha256 must be a full SHA-256")
        if not valid_iso_date(item.get("verified_at")):
            errors.append(f"evidence {evidence_id}.verified_at must be ISO-8601")
        version_text = str(item.get("version_or_date", "")).lower()
        if not any(character.isdigit() for character in version_text) or any(word in version_text for word in ("fake", "placeholder", "unknown", "trust-me", "today")):
            errors.append(f"evidence {evidence_id}.version_or_date is not a concrete version or date")
        if mode in {"complete", "release"} and item.get("verified_by") == document.get("owner"):
            errors.append(f"evidence {evidence_id} must be independently verified in {mode} mode")
        if item.get("verification_status") != "verified":
            errors.append(f"evidence {evidence_id} is not verified")
        if item.get("evidence_type") in {"runtime-evidence", "test-report"} and not nonempty(item.get("environment")):
            errors.append(f"evidence {evidence_id}.environment is required for executable evidence")
        supports = item.get("claim_supports")
        if not isinstance(supports, list):
            errors.append(f"evidence {evidence_id}.claim_supports must be an array")
            supports = []
        support_map: dict[str, str] = {}
        for index, support in enumerate(supports):
            if not isinstance(support, dict) or not nonempty(support.get("claim_id")) or not nonempty(support.get("excerpt")):
                errors.append(f"evidence {evidence_id}.claim_supports[{index}] is invalid")
                continue
            excerpt = str(support["excerpt"]).strip()
            if len(words(excerpt)) < 5:
                errors.append(f"evidence {evidence_id} claim-support excerpt is too short")
            support_map[str(support["claim_id"])] = excerpt
        evidence_claim_supports[evidence_id] = support_map
        if artifact_root is not None and nonempty(item.get("snapshot_path")):
            snapshot = (artifact_root / str(item["snapshot_path"])).resolve()
            try:
                snapshot.relative_to(artifact_root.resolve())
            except ValueError:
                errors.append(f"evidence {evidence_id}.snapshot_path escapes artifact root")
            else:
                if snapshot.is_file():
                    if sha256(snapshot) != str(item.get("content_sha256", "")).lower():
                        errors.append(f"evidence {evidence_id}.content_sha256 does not match snapshot")
                    evidence_snapshot_text[evidence_id] = snapshot.read_text(encoding="utf-8", errors="replace")
                elif mode in {"complete", "release"}:
                    errors.append(f"evidence {evidence_id} snapshot does not exist")

    claims = indexed(document.get("claims"), "claim_id", "claims", errors)
    if not claims:
        errors.append("claims must contain at least one claim")
    for claim_id, claim in claims.items():
        classification = claim.get("classification")
        if classification not in CLAIM_CLASSES:
            errors.append(f"claim {claim_id} has invalid classification")
        refs = claim.get("evidence_refs")
        if not isinstance(refs, list):
            errors.append(f"claim {claim_id}.evidence_refs must be an array")
            refs = []
        missing = [ref for ref in refs if ref not in evidence]
        if missing:
            errors.append(f"claim {claim_id} references unknown evidence: {missing}")
        if classification in FACT_CLASSES and not refs:
            errors.append(f"material factual claim {claim_id} has no evidence_refs")
        for evidence_id in refs:
            excerpt = evidence_claim_supports.get(evidence_id, {}).get(claim_id)
            if not excerpt:
                errors.append(f"claim {claim_id} lacks a claim-support excerpt in evidence {evidence_id}")
            elif mode in {"complete", "release"} and excerpt.lower() not in evidence_snapshot_text.get(evidence_id, "").lower():
                errors.append(f"claim {claim_id} support excerpt is absent from evidence snapshot {evidence_id}")
        claim_text = str(claim.get("text", "")).lower()
        benchmark_or_scale = bool(re.search(r"\b(benchmark|billion|million|rows?|records?|10x|\d+(?:\.\d+)?x)\b|tỷ|triệu|production", claim_text))
        if classification in FACT_CLASSES and benchmark_or_scale and not any(evidence.get(ref, {}).get("evidence_type") == "runtime-evidence" for ref in refs):
            errors.append(f"benchmark/scale/production claim {claim_id} requires runtime-evidence")

    artifacts = indexed(document.get("artifacts"), "artifact_id", "artifacts", errors)
    if not artifacts:
        errors.append("artifacts must contain at least one artifact")
    canonical_id = document.get("canonical_artifact")
    if nonempty(canonical_id) and canonical_id not in artifacts:
        errors.append("canonical_artifact does not match any artifact_id")

    channels: dict[str, str] = {}
    loaded_text: dict[str, str] = {}
    for artifact_id, artifact in artifacts.items():
        channel = artifact.get("channel")
        if not nonempty(channel):
            errors.append(f"artifact {artifact_id}.channel must be non-empty")
        elif channel in channels:
            errors.append(f"duplicate channel variant: {channel}")
        else:
            channels[channel] = artifact_id
        expected_language = CHANNEL_LANGUAGES.get(str(channel))
        if expected_language and artifact.get("language") != expected_language:
            errors.append(
                f"artifact {artifact_id}.language must be {expected_language} for {channel}"
            )
        if artifact_id != canonical_id and artifact.get("derived_from") != canonical_id:
            errors.append(f"artifact {artifact_id}.derived_from must reference canonical_artifact")
        claim_ids = artifact.get("claim_ids")
        if not isinstance(claim_ids, list):
            errors.append(f"artifact {artifact_id}.claim_ids must be an array")
            claim_ids = []
        unknown_claims = [claim_id for claim_id in claim_ids if claim_id not in claims]
        if unknown_claims:
            errors.append(f"artifact {artifact_id} references unknown claims: {unknown_claims}")
        path_text = artifact.get("path")
        if not nonempty(path_text):
            errors.append(f"artifact {artifact_id}.path must be non-empty")
            continue
        status = artifact.get("status")
        if status in {"approved", "published"} or mode in {"complete", "release"}:
            if not claim_ids:
                errors.append(f"artifact {artifact_id} has no governed claim_ids when {status}")
            if not nonempty(artifact.get("version")):
                errors.append(f"artifact {artifact_id}.version is required when {status}")
            if not SHA256_RE.fullmatch(str(artifact.get("sha256", "")).lower()):
                errors.append(f"artifact {artifact_id}.sha256 must be a full SHA-256 when {status}")
        if mode in {"complete", "release"} and status not in {"approved", "published"}:
            errors.append(f"artifact {artifact_id} must be approved or published in {mode} mode")
        required_scopes = artifact.get("required_test_scopes")
        if not isinstance(required_scopes, list) or not all(nonempty(scope) for scope in required_scopes):
            errors.append(f"artifact {artifact_id}.required_test_scopes must contain non-empty scopes")
        if artifact_root is not None:
            path = (artifact_root / str(path_text)).resolve()
            try:
                path.relative_to(artifact_root.resolve())
            except ValueError:
                errors.append(f"artifact {artifact_id}.path escapes artifact root")
                continue
            if path.is_file():
                actual_hash = sha256(path)
                loaded_text[channel] = path.read_text(encoding="utf-8")
                if nonempty(artifact.get("sha256")) and actual_hash != str(artifact["sha256"]).lower():
                    errors.append(f"artifact {artifact_id}.sha256 does not match file")
            elif status in {"approved", "published"} or mode in {"complete", "release"}:
                errors.append(f"artifact {artifact_id} file does not exist in {mode} mode")

    for channel in requested:
        if channel not in channels:
            errors.append(f"requested channel has no artifact: {channel}")

    media_assets = indexed(document.get("media_assets", []), "media_id", "media_assets", errors)
    media_roles_by_artifact: dict[str, set[str]] = {}
    for media_id, media in media_assets.items():
        role = media.get("role")
        if role not in MEDIA_ROLES:
            errors.append(f"media asset {media_id}.role must be one of {sorted(MEDIA_ROLES)}")
        bound_ids = media.get("bound_artifact_ids")
        if not isinstance(bound_ids, list) or not bound_ids or not all(nonempty(item) for item in bound_ids):
            errors.append(f"media asset {media_id}.bound_artifact_ids must contain artifact IDs")
            bound_ids = []
        for artifact_id in bound_ids:
            artifact = artifacts.get(artifact_id)
            if artifact is None:
                errors.append(f"media asset {media_id} references unknown artifact: {artifact_id}")
            elif artifact.get("channel") not in CHANNEL_LANGUAGES:
                errors.append(f"media asset {media_id} must bind only to social channel artifacts")
            elif role in MEDIA_ROLES:
                media_roles_by_artifact.setdefault(str(artifact_id), set()).add(str(role))
        if not nonempty(media.get("alt_text")):
            errors.append(f"media asset {media_id}.alt_text must be non-empty")
        if mode in {"complete", "release"}:
            for field in ("path", "version", "sha256", "source", "origin"):
                if not nonempty(media.get(field)):
                    errors.append(f"media asset {media_id}.{field} must be non-empty in {mode} mode")
            digest = str(media.get("sha256", "")).lower()
            if not SHA256_RE.fullmatch(digest):
                errors.append(f"media asset {media_id}.sha256 must be a full SHA-256")
            if media.get("rights_status") != "cleared":
                errors.append(f"media asset {media_id}.rights_status must be cleared")
            if media.get("redaction_status") not in {"not-required", "completed"}:
                errors.append(f"media asset {media_id}.redaction_status is not release-safe")
            if media.get("validation_status") != "passed":
                errors.append(f"media asset {media_id}.validation_status must be passed")
            media_path_text = media.get("path")
            if nonempty(media_path_text) and artifact_root is not None:
                media_path = (artifact_root / str(media_path_text)).resolve()
                try:
                    media_path.relative_to(artifact_root.resolve())
                except ValueError:
                    errors.append(f"media asset {media_id}.path escapes artifact root")
                else:
                    if not media_path.is_file():
                        errors.append(f"media asset {media_id} file does not exist in {mode} mode")
                    elif SHA256_RE.fullmatch(digest) and sha256(media_path) != digest:
                        errors.append(f"media asset {media_id}.sha256 does not match file")
        if role == "real":
            if media.get("origin") not in {"", None, "real-artifact"}:
                errors.append(f"REAL media asset {media_id} must originate from a real artifact")
            if not nonempty(media.get("what_to_observe")):
                errors.append(f"REAL media asset {media_id}.what_to_observe must be non-empty")
        elif role == "illustration":
            for field in ("learning_claim", "layout", "rendering_method"):
                if not nonempty(media.get(field)):
                    errors.append(f"illustration media asset {media_id}.{field} must be non-empty")
        elif role == "code":
            if media.get("code_maturity") not in CODE_MATURITY:
                errors.append(f"code media asset {media_id}.code_maturity is invalid")
            if not nonempty(media.get("technical_baseline")):
                errors.append(f"code media asset {media_id}.technical_baseline must be non-empty")
            performed = media.get("validation_performed")
            if not isinstance(performed, list) or not all(nonempty(item) for item in performed):
                errors.append(f"code media asset {media_id}.validation_performed must be an array")

    if mode in {"complete", "release"}:
        for channel in requested:
            if channel not in CHANNEL_LANGUAGES or channel not in channels:
                continue
            artifact_id = channels[channel]
            missing_roles = MEDIA_ROLES - media_roles_by_artifact.get(artifact_id, set())
            if missing_roles:
                errors.append(f"social artifact {artifact_id} lacks mandatory media roles: {sorted(missing_roles)}")

    reviews = indexed(document.get("reviews"), "review_id", "reviews", errors)
    review_types_by_artifact: dict[str, set[str]] = {}
    for review_id, review in reviews.items():
        artifact_id = review.get("artifact_id")
        artifact = artifacts.get(artifact_id)
        if artifact is None:
            errors.append(f"review {review_id} references unknown artifact")
            continue
        if review_id not in artifact.get("review_ids", []):
            errors.append(f"review {review_id} is not declared by artifact {artifact_id}")
        if review.get("status") == "passed":
            if review.get("artifact_version") != artifact.get("version") or review.get("artifact_sha256") != artifact.get("sha256"):
                errors.append(f"review {review_id} is not bound to the artifact version and SHA-256")
            if not nonempty(review.get("reviewer")) or not nonempty(review.get("reviewed_at")):
                errors.append(f"review {review_id} lacks reviewer or reviewed_at")
            if not valid_iso_date(review.get("reviewed_at")):
                errors.append(f"review {review_id}.reviewed_at must be ISO-8601")
            if mode in {"complete", "release"} and review.get("reviewer") == document.get("owner"):
                errors.append(f"review {review_id} must be independent in {mode} mode")
            review_types_by_artifact.setdefault(artifact_id, set()).add(str(review.get("review_type")))
    for artifact_id, artifact in artifacts.items():
        for review_id in artifact.get("review_ids", []):
            if review_id not in reviews:
                errors.append(f"artifact {artifact_id} references unknown review: {review_id}")
        if artifact.get("status") in {"approved", "published"} or mode in {"complete", "release"}:
            required_reviews = CANONICAL_REVIEW_TYPES if artifact.get("channel") == "canonical" else CHANNEL_REVIEW_TYPES
            missing = required_reviews - review_types_by_artifact.get(artifact_id, set())
            if missing:
                errors.append(f"artifact {artifact_id} lacks passed required reviews: {sorted(missing)}")
            if artifact_id != canonical_id and artifacts.get(str(canonical_id), {}).get("status") not in {"approved", "published"}:
                errors.append(f"artifact {artifact_id} cannot be approved before canonical_artifact")

    tests = indexed(document.get("tests"), "test_id", "tests", errors)
    passed_scopes_by_artifact: dict[str, set[str]] = {}
    for test_id, test in tests.items():
        if test.get("required") is True:
            if not nonempty(test.get("scope")):
                errors.append(f"required test {test_id}.scope must be non-empty")
            if test.get("status") != "passed":
                errors.append(f"required test {test_id} has not passed")
            evidence_ref = test.get("evidence_ref")
            if evidence_ref not in evidence:
                errors.append(f"required test {test_id} lacks resolvable evidence_ref")
            elif evidence[evidence_ref].get("evidence_type") != "test-report":
                errors.append(f"required test {test_id} evidence_ref is not a test-report")
            elif test.get("status") == "passed":
                passed_scopes_by_artifact.setdefault(str(test.get("artifact_id")), set()).add(str(test.get("scope")))
    for artifact_id, artifact in artifacts.items():
        if artifact.get("status") in {"approved", "published"} or mode in {"complete", "release"}:
            expected_scopes = set(artifact.get("required_test_scopes", []))
            artifact_channel = artifact.get("channel")
            minimum_scopes = CANONICAL_TEST_SCOPES if artifact_channel == "canonical" else CHANNEL_TEST_SCOPES
            if artifact_channel in CHANNEL_LANGUAGES:
                minimum_scopes = minimum_scopes | {"channel-language"}
            undeclared_scopes = minimum_scopes - expected_scopes
            if undeclared_scopes:
                errors.append(f"artifact {artifact_id} does not declare mandatory test scopes: {sorted(undeclared_scopes)}")
            missing_scopes = expected_scopes - passed_scopes_by_artifact.get(artifact_id, set())
            if missing_scopes:
                errors.append(f"artifact {artifact_id} lacks passed required test scopes: {sorted(missing_scopes)}")

    approvals = indexed(document.get("approvals"), "approval_id", "approvals", errors)
    publication = document.get("publication")
    if not isinstance(publication, dict):
        errors.append("publication must be an object")
    elif publication.get("status") == "published":
        requested_publication = publication.get("requested_channels")
        if not isinstance(requested_publication, list) or not all(nonempty(item) for item in requested_publication):
            errors.append("published content requires publication.requested_channels")
            requested_publication = []
        published_channels = publication.get("channels")
        if not isinstance(published_channels, list) or not published_channels:
            errors.append("published content requires publication.channels")
            published_channels = []
        observed_publication_channels: list[str] = []
        for index, release in enumerate(published_channels):
            if not isinstance(release, dict):
                errors.append(f"publication.channels[{index}] must be an object")
                continue
            channel = release.get("channel")
            observed_publication_channels.append(str(channel))
            artifact_id = release.get("artifact_id")
            approved_version = release.get("approved_version")
            approved_hash = str(release.get("approved_sha256", "")).lower()
            approval_id = release.get("approval_id")
            if channels.get(channel) != artifact_id:
                errors.append(f"publication record does not identify the channel artifact: {channel}")
            artifact = artifacts.get(artifact_id, {})
            if not artifact_id or artifact.get("status") != "published":
                errors.append(f"published channel lacks a published artifact: {channel}")
                continue
            if artifact.get("version") != approved_version or artifact.get("sha256") != approved_hash:
                errors.append(f"publication version/hash does not match {channel} artifact")
            approval = approvals.get(approval_id, {})
            authority_ref = approval.get("authority_evidence_ref")
            if not (approval.get("status") == "approved" and approval.get("artifact_id") == artifact_id and approval.get("artifact_version") == approved_version and approval.get("artifact_sha256") == approved_hash and channel in approval.get("channels", []) and nonempty(approval.get("approver")) and approval.get("approver") != document.get("owner") and nonempty(approval.get("authority_scope")) and authority_ref in evidence and nonempty(approval.get("approved_at")) and valid_iso_date(approval.get("approved_at"))):
                errors.append(f"published channel lacks exact-version channel authority: {channel}")
            if not nonempty(release.get("published_at")):
                errors.append(f"published channel lacks published_at: {channel}")
            elif not valid_iso_date(release.get("published_at")):
                errors.append(f"published_at must be ISO-8601: {channel}")
        if sorted(observed_publication_channels) != sorted(requested_publication):
            errors.append("publication channels do not exactly cover publication.requested_channels")
    elif mode == "release":
        errors.append("release mode requires publication.status=published")

    for channel, text in loaded_text.items():
        if channel in DEFAULT_WORD_LIMITS:
            artifact = artifacts[channels[channel]]
            default_low, default_high = DEFAULT_WORD_LIMITS[channel]
            low = artifact.get("min_words") or default_low
            high = artifact.get("max_words") or default_high
            if not isinstance(low, int) or not isinstance(high, int) or low <= 0 or high < low:
                errors.append(f"{channel} artifact has invalid min_words/max_words")
                continue
            count = len(words(text))
            if not low <= count <= high:
                errors.append(f"{channel} artifact word count {count} is outside {low}-{high}")
        if channel == "substack":
            marker_groups = (("subject", "tiêu đề"), ("preheader", "dòng xem trước", "mô tả xem trước"), ("reference", "tài liệu tham khảo", "nguồn"), ("next episode", "bài tiếp theo"))
            for alternatives in marker_groups:
                if not any(marker in text.lower() for marker in alternatives):
                    errors.append(f"substack artifact lacks required marker: {'/'.join(alternatives)}")
        if channel in CHANNEL_LANGUAGES:
            artifact = artifacts[channels[channel]]
            structure = artifact.get("structure_evidence")
            required = (
                "core_claim_excerpt",
                "evidence_or_mechanism_excerpt",
                "failure_or_boundary_excerpt",
                "decision_excerpt",
                "real_asset_bridge_excerpt",
                "illustration_asset_bridge_excerpt",
                "code_asset_bridge_excerpt",
            )
            if channel in {"facebook", "linkedin"}:
                required = required + ("hook_excerpt", "takeaway_excerpt", "discussion_question_excerpt")
            if not isinstance(structure, dict):
                errors.append(f"{channel} artifact lacks structure_evidence")
            else:
                for field in required:
                    excerpt = structure.get(field)
                    if not nonempty(excerpt) or str(excerpt).lower() not in text.lower():
                        errors.append(f"{channel} structure evidence is missing from text: {field}")
                question = structure.get("discussion_question_excerpt")
                if channel in {"facebook", "linkedin"} and nonempty(question) and "?" not in str(question):
                    errors.append(f"{channel} discussion_question_excerpt is not a question")
    for left, right in combinations(sorted(loaded_text), 2):
        if left == "canonical" or right == "canonical":
            continue
        a, b = ngrams(loaded_text[left]), ngrams(loaded_text[right])
        if a and b and len(a & b) / len(a | b) > 0.45:
            errors.append(f"channel variants are too textually similar: {left}, {right}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Path to content-manifest.json")
    parser.add_argument("--artifact-root", type=Path, help="Root used to verify artifact files and hashes; defaults to manifest directory")
    parser.add_argument("--mode", choices=("plan", "complete", "release"), default="complete", help="Validation strength; default complete requires real artifacts, evidence snapshots, reviews and tests")
    args = parser.parse_args()
    try:
        document = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    root = (args.artifact_root or args.manifest.parent).resolve()
    errors = validate(document, root, args.mode)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} validation error(s)")
        return 1
    print("PASS: claims, evidence, lineage, channel fit and release authority are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
