import os
import asyncio
import shlex
import logging
from typing import Tuple
from git import Repo, GitCommandError, InvalidGitRepositoryError

import config
from ..logging import LOGGER

logger = LOGGER(__name__)

def install_req(cmd: str) -> Tuple[str, str, int, int]:
    async def install_requirements():
        args = shlex.split(cmd)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return (
            stdout.decode("utf-8", "replace").strip(),
            stderr.decode("utf-8", "replace").strip(),
            process.returncode,
            process.pid,
        )

    return asyncio.get_event_loop().run_until_complete(install_requirements())

def git():
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
    
    if ENVIRONMENT == "production":
        logger.info("[GIT] Production environment detected, skipping git operations.")
        return

    if not os.path.exists(".git"):
        logger.warning("[GIT] No .git directory found, skipping git operations.")
        return

    REPO_LINK = config.UPSTREAM_REPO
    if config.GIT_TOKEN:
        GIT_USERNAME = REPO_LINK.split("com/")[1].split("/")[0]
        TEMP_REPO = REPO_LINK.split("https://")[1]
        UPSTREAM_REPO = f"https://{GIT_USERNAME}:{config.GIT_TOKEN}@{TEMP_REPO}"
    else:
        UPSTREAM_REPO = config.UPSTREAM_REPO

    try:
        repo = Repo()
        logger.info(f"[GIT] Git Client Found [VPS/Local Deployer]")
        origin = repo.remotes.origin
        origin.fetch()
        origin.pull()
        logger.info(f"[GIT] Successfully fetched and pulled latest changes.")
        install_req("pip3 install --no-cache-dir -r requirements.txt")
    except (GitCommandError, InvalidGitRepositoryError) as e:
        logger.error(f"[GIT] Git Error: {e}")
