from pathlib import Path
from datetime import datetime, timedelta
import json
import os
import shutil

PROJECT_DIR = Path(__file__).resolve().parent

TARGET_FOLDERS = [
    PROJECT_DIR / "qr",
    PROJECT_DIR / "labels",
]

LOG_FILE = PROJECT_DIR / "maintenance.log"
STATE_FILE = PROJECT_DIR / "maintenance_state.json"
LOCK_FILE = PROJECT_DIR / ".maintenance.lock"

SCHEDULE_HOUR = 4
LOCK_STALE_HOURS = 2


def write_log(message):
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{timestamp} - {message}\n")


def _acquire_lock():
    if LOCK_FILE.exists():
        try:
            age_seconds = datetime.now().timestamp() - LOCK_FILE.stat().st_mtime
            if age_seconds > LOCK_STALE_HOURS * 60 * 60:
                LOCK_FILE.unlink()
        except Exception:
            return None

    try:
        fd = os.open(
            LOCK_FILE,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY
        )
        os.write(fd, str(os.getpid()).encode("utf-8"))
        return fd
    except FileExistsError:
        return None


def _release_lock(fd):
    if fd is None:
        return

    try:
        os.close(fd)
    except Exception:
        pass

    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except Exception:
        pass


def _load_last_successful_cleanup():
    if not STATE_FILE.exists():
        return None

    try:
        data = json.loads(
            STATE_FILE.read_text(encoding="utf-8")
        )

        value = data.get("last_successful_cleanup")

        if not value:
            return None

        return datetime.fromisoformat(value)

    except Exception:
        return None


def _save_last_successful_cleanup(when):
    data = {
        "last_successful_cleanup":
            when.isoformat(timespec="seconds")
    }

    STATE_FILE.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def _most_recent_scheduled_cleanup(now=None):
    if now is None:
        now = datetime.now().astimezone()

    monday_date = (
        now.date()
        - timedelta(days=now.weekday())
    )

    scheduled = datetime(
        monday_date.year,
        monday_date.month,
        monday_date.day,
        SCHEDULE_HOUR,
        0,
        0,
        tzinfo=now.tzinfo
    )

    if now < scheduled:
        scheduled -= timedelta(days=7)

    return scheduled


def cleanup_is_due(now=None):
    if now is None:
        now = datetime.now().astimezone()

    scheduled = _most_recent_scheduled_cleanup(now)
    last_cleanup = _load_last_successful_cleanup()

    if last_cleanup is None:
        return True

    if last_cleanup.tzinfo is None:
        last_cleanup = last_cleanup.replace(
            tzinfo=now.tzinfo
        )

    return last_cleanup < scheduled


def clean_folder(folder):
    deleted_files = 0
    deleted_folders = 0
    errors = []

    folder.mkdir(
        parents=True,
        exist_ok=True
    )

    for item in list(folder.iterdir()):
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
                deleted_files += 1

            elif item.is_dir():
                shutil.rmtree(item)
                deleted_folders += 1

        except FileNotFoundError:
            continue

        except Exception as exc:
            errors.append(
                f"{item.name}: {exc}"
            )

    return (
        deleted_files,
        deleted_folders,
        errors
    )


def run_cleanup(source="manual"):
    """
    Deletes ALL generated content inside qr/ and labels/.
    It never deletes pallets.db or either folder itself.
    """

    lock_fd = _acquire_lock()

    if lock_fd is None:
        write_log(
            f"Maintenance skipped ({source}): "
            "another cleanup is already running."
        )

        return {
            "executed": False,
            "reason": "already_running",
            "deleted_files": 0,
            "deleted_folders": 0,
            "errors": 0
        }

    try:
        write_log(
            f"Maintenance started. Source: {source}."
        )

        total_files = 0
        total_folders = 0
        all_errors = []

        for folder in TARGET_FOLDERS:
            (
                files_deleted,
                folders_deleted,
                errors
            ) = clean_folder(folder)

            total_files += files_deleted
            total_folders += folders_deleted

            write_log(
                f"{folder.name}: deleted "
                f"{files_deleted} file(s) and "
                f"{folders_deleted} subfolder(s)."
            )

            for error in errors:
                write_log(
                    f"ERROR in {folder.name}: {error}"
                )
                all_errors.append(
                    f"{folder.name}: {error}"
                )

        if all_errors:
            write_log(
                "Maintenance completed with "
                f"{len(all_errors)} error(s). "
                f"Total deleted: "
                f"{total_files} file(s), "
                f"{total_folders} subfolder(s)."
            )

            return {
                "executed": True,
                "reason": "completed_with_errors",
                "deleted_files": total_files,
                "deleted_folders": total_folders,
                "errors": len(all_errors)
            }

        completed_at = datetime.now().astimezone()

        _save_last_successful_cleanup(
            completed_at
        )

        write_log(
            "Maintenance completed successfully. "
            f"Total deleted: "
            f"{total_files} file(s), "
            f"{total_folders} subfolder(s)."
        )

        return {
            "executed": True,
            "reason": "success",
            "deleted_files": total_files,
            "deleted_folders": total_folders,
            "errors": 0
        }

    finally:
        _release_lock(lock_fd)


def run_if_due():
    """
    Fallback used when Pallet ID System starts.
    Runs only if the most recent Monday 4:00 AM cleanup was missed.
    """

    if not cleanup_is_due():
        return {
            "executed": False,
            "reason": "not_due",
            "deleted_files": 0,
            "deleted_folders": 0,
            "errors": 0
        }

    return run_cleanup(
        source="application_fallback"
    )


def main():
    # The Windows scheduled task calls this directly every Monday.
    run_cleanup(
        source="windows_task_scheduler"
    )


if __name__ == "__main__":
    main()
