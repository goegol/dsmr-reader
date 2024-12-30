import logging
import time
import os
from typing import Iterable

from django.utils.translation import gettext as _
from django.conf import settings
import dropbox
import dropbox.exceptions

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_backup.models.settings import DropboxSettings
from dsmr_dropbox.dropboxinc.dropbox_content_hasher import DropboxContentHasher
import dsmr_backup.services.backup
import dsmr_frontend.services


logger = logging.getLogger("dsmrreader")


def run(scheduled_process: ScheduledProcess) -> None:
    dropbox_settings = DropboxSettings.get_solo()

    if not dropbox_settings.refresh_token:
        # Should not happen, safe fallback
        scheduled_process.disable()
        return

    dropbox_client = get_dropbox_client(scheduled_process=scheduled_process)
    backup_directory = dsmr_backup.services.backup.get_backup_directory()

    # Sync each file, recursively.
    for current_file in list_files_in_dir(directory=backup_directory):
        if not should_sync_file(current_file):
            continue

        sync_file(
            scheduled_process=scheduled_process,
            dropbox_client=dropbox_client,
            local_root_dir=backup_directory,
            abs_file_path=current_file,
        )

    scheduled_process.delay(hours=settings.DSMRREADER_DROPBOX_SYNC_INTERVAL)


def get_dropbox_client(scheduled_process: ScheduledProcess) -> dropbox.Dropbox:
    """
    The Dropbox refresh token we locally store (after linking the user's Dropbox account) never expires. This method
    returns a new and authenticated instance of the Dropbox client that can be used for its (short) duration.
    """
    dropbox_settings = DropboxSettings.get_solo()
    dbx = dropbox.Dropbox(
        oauth2_refresh_token=dropbox_settings.refresh_token,
        app_key=settings.DSMRREADER_DROPBOX_APP_KEY,
    )

    try:
        dbx.refresh_access_token()
        dbx.check_user()  # No-op, just to verify the client/session.
    except Exception as error:
        logger.error(" - Dropbox error: %s", error)

        # Network errors should NOT reset the client side app token (see further below). Only API errors should do so.
        if not isinstance(error, dropbox.exceptions.DropboxException):
            scheduled_process.delay(minutes=1)
            raise

        logger.error(" - Removing Dropbox credentials due to API failure")
        message = _(
            "Unable to authenticate with Dropbox, removing credentials. Error: {}".format(
                error
            )
        )
        dsmr_frontend.services.display_dashboard_message(message=message)
        DropboxSettings.objects.update(
            refresh_token=None,
        )  # Does not trigger auto disable
        scheduled_process.disable()
        raise

    logger.info("Dropbox: Auth/user check OK")
    return dbx


def list_files_in_dir(directory: str) -> Iterable:
    """Lists all files recursively in the specified (backup) directory."""
    files = []

    for root, __, filenames in os.walk(directory):
        for current_file in filenames:
            files.append(os.path.abspath(os.path.join(root, current_file)))

    return files


def should_sync_file(abs_file_path: str) -> bool:
    """Checks whether we should include this file for sync."""
    file_stat = os.stat(abs_file_path)

    # Ignore empty files.
    if file_stat.st_size == 0:
        logger.debug("Dropbox: Ignoring file with zero Bytes: %s", abs_file_path)
        return False

    # Ignore file that haven't been updated in a while.
    seconds_since_last_modification = int(time.time() - file_stat.st_mtime)

    if (
        seconds_since_last_modification
        > settings.DSMRREADER_DROPBOX_MAX_FILE_MODIFICATION_TIME
    ):
        logger.debug(
            "Dropbox: Ignoring file: Time since last modification too high (%s secs): %s",
            seconds_since_last_modification,
            abs_file_path,
        )
        return False

    return True


def sync_file(
    scheduled_process: ScheduledProcess,
    dropbox_client: dropbox.Dropbox,
    local_root_dir: str,
    abs_file_path: str,
) -> None:
    # The path we use in our Dropbox app folder.
    relative_file_path = abs_file_path.replace(local_root_dir, "")

    try:
        # Check whether the file is already at Dropbox, if so, check its hash.
        dropbox_meta = dropbox_client.files_get_metadata(relative_file_path)
    except dropbox.exceptions.ApiError as exception:
        error_message = str(exception.error)
        dropbox_meta = None

        # Unexpected.
        if "not_found" not in error_message:
            logger.error(" - Dropbox error: %s", error_message)
            return

    # Calculate local hash and compare with remote. Ignore if the remote file is exactly the same.
    if (
        dropbox_meta
        and calculate_content_hash(abs_file_path) == dropbox_meta.content_hash
    ):
        logger.debug(
            "Dropbox: Content hash is the same, skipping: %s", relative_file_path
        )
        return

    try:
        upload_chunked(
            dropbox_client=dropbox_client,
            local_file_path=abs_file_path,
            remote_file_path=relative_file_path,
        )
    except dropbox.exceptions.DropboxException as exception:
        error_message = str(exception.error)
        logger.error("Dropbox: %s", error_message)

        if "insufficient_space" in error_message:
            message = _(
                "Unable to upload files to Dropbox due to {}. Ignoring new files for the next {} hours...".format(
                    error_message, settings.DSMRREADER_DROPBOX_ERROR_INTERVAL
                )
            )
            dsmr_frontend.services.display_dashboard_message(message=message)
            scheduled_process.delay(hours=settings.DSMRREADER_DROPBOX_ERROR_INTERVAL)

        raise  # pragma: no cover


def upload_chunked(
    dropbox_client: dropbox.Dropbox, local_file_path: str, remote_file_path: str
) -> None:
    """Uploads a file in chucks to Dropbox, allowing it to resume on (connection) failure."""
    logger.info("Dropbox: Syncing file %s", remote_file_path)

    write_mode = dropbox.files.WriteMode.overwrite

    file_handle = open(local_file_path, "rb")
    file_size = os.path.getsize(local_file_path)

    # Many thanks to https://stackoverflow.com/documentation/dropbox-api/409/uploading-a-file/1927/uploading-a-file-usin
    # g-the-dropbox-python-sdk#t=201610181733061624381
    CHUNK_SIZE = 2 * 1024 * 1024

    # Small uploads should be transfers at one go.
    if file_size <= CHUNK_SIZE:
        dropbox_client.files_upload(
            file_handle.read(), remote_file_path, mode=write_mode
        )

    # Large uploads can be sent in chunks, by creating a session allowing multiple separate uploads.
    else:
        upload_session_start_result = dropbox_client.files_upload_session_start(
            file_handle.read(CHUNK_SIZE)
        )

        cursor = dropbox.files.UploadSessionCursor(
            session_id=upload_session_start_result.session_id, offset=file_handle.tell()
        )
        commit = dropbox.files.CommitInfo(path=remote_file_path, mode=write_mode)

        # We keep sending the data in chunks, until we reach the last one, then we instruct Dropbox to finish the upload
        # by combining all the chunks sent previously.
        while file_handle.tell() < file_size:
            if (file_size - file_handle.tell()) <= CHUNK_SIZE:
                dropbox_client.files_upload_session_finish(
                    file_handle.read(CHUNK_SIZE), cursor, commit
                )
            else:
                dropbox_client.files_upload_session_append_v2(
                    file_handle.read(CHUNK_SIZE), cursor
                )
                cursor.offset = file_handle.tell()

    file_handle.close()


def calculate_content_hash(file_path: str) -> str:
    """Calculates the Dropbox hash of a file: https://www.dropbox.com/developers/reference/content-hash"""
    hasher = DropboxContentHasher()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(DropboxContentHasher.BLOCK_SIZE)
            if len(chunk) == 0:
                break
            hasher.update(chunk)

    return hasher.hexdigest()
