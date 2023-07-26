# Path: scripts/local_supabase_runner.py
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
import asyncio
import os
import json
import socket
import yaml

from supabase_e2e_methods import main_test
from docker_check import check_docker_running
from create_table_and_function import create_table_and_function

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingEnvironmentVariableError(Exception):
    pass


class SupabaseCommandError(Exception):
    pass


async def get_db_credentials() -> dict:
    credentials = {}
    host = socket.gethostbyname(socket.gethostname())
    try:
        status = await get_supabase_status()
        for line in status.split("\n"):
            if "API URL" in line:
                credentials["supabase_url"] = line.split(": ")[1].replace(
                    "localhost", host
                )
            elif "DB URL" in line:
                credentials["supabase_db_url"] = line.split(": ")[1].replace(
                    "localhost", host
                )
            elif "anon key" in line:
                credentials["supabase_anon_key"] = line.split(": ")[1]
            elif "service_role key" in line:
                credentials["supabase_service_role_key"] = line.split(": ")[1]
    except Exception as e:
        logger.error(f"Error getting Supabase status: {str(e)}")
        raise SupabaseCommandError("Error getting Supabase status") from e
    return credentials


async def run_supabase_command(command: str, flags: list = []) -> str:
    command = f"{command} {' '.join(flags)}".strip()
    logger.info("Running Supabase command: %s", command)
    if command[0] == " ":
        command = command[1:]
    process = await asyncio.create_subprocess_exec(
        "supabase",
        *command.split(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if stdout:
        logger.info(stdout.decode())
    if stderr:
        logger.error(stderr.decode())
    if process.returncode != 0:
        raise SupabaseCommandError(
            f"Error running Supabase command '{command}'. Return code: {process.returncode}"
        )
    return stdout.decode()


async def write_e2e_test_config_file(credentials: dict) -> bool:
    if not credentials:
        logger.error("No credentials provided to write to the e2e_test_config.yml file")
        return False

    logger.info("Updating e2e_test_config.yml file with: %s", credentials)

    try:
        with open("config/e2e_test_config.yml", "w") as config_file:
            yaml.dump(credentials, config_file, default_flow_style=False)
        return True
    except Exception as error:
        logger.error(
            f"Failed to write to e2e_test_config.yml file due to error: {str(error)}"
        )
        return False


async def reset_env_file(credentials: dict) -> bool:
    if not credentials:
        logger.error("No credentials provided to write to .env file")
        return False

    env_vars = "\n".join([f"{k.upper()}={v}" for k, v in credentials.items()])
    logger.info("Updating .env file with: %s", env_vars)

    try:
        with open(".env", "w") as env_file:
            env_file.write(env_vars)
        return True
    except Exception as error:
        logger.error(f"Failed to write to .env file due to error: {str(error)}")
        return False


async def start_supabase() -> bool:
    for _ in range(3):
        try:
            await run_supabase_command("start")
            await asyncio.sleep(3)  # Wait for 3 seconds
            status = await get_supabase_status()
            if "DB URL" in status:
                return True
        except SupabaseCommandError:
            await stop_supabase()
            await asyncio.sleep(3)  # Wait for 3 seconds
    return False


async def stop_supabase() -> str:
    return await run_supabase_command("stop", ["--no-backup"])


async def get_supabase_status() -> str:
    return await run_supabase_command("status")


async def get_supabase_credentials() -> str:
    check_docker_running()
    try:
        if not os.path.isdir("supabase"):
            logger.error("Supabase directory does not exist, creating...")
            await run_supabase_command("init")

        await stop_supabase()
        await asyncio.sleep(3)  # Wait for 3 seconds

        if not await start_supabase():
            raise RuntimeError("Failed to start Supabase after multiple attempts.")
        credentials = await get_db_credentials()
        if not credentials:
            logger.error("Error getting DB credentials.")
            raise RuntimeError("Error getting DB credentials.")

        # if not await reset_env_file(credentials=credentials):
        #     raise RuntimeError("Failed to write DB credentials to .env file.")

        if not await write_e2e_test_config_file(credentials=credentials):
            raise RuntimeError(
                "Failed to write DB credentials to e2e_test_config.yml file."
            )

        create_table_and_function(credentials["supabase_db_url"])

        logger.info("DB credentials: %s", credentials)
        test_result = main_test(credentials)
        if not test_result:
            raise RuntimeError("Supabase CRUD operations failed.")
        return json.dumps(credentials)

    except Exception as error:
        logger.error(
            "An error of type %s occurred. Arguments:\n%s",
            type(error).__name__,
            error.args,
        )
        # await stop_supabase()
        raise


if __name__ == "__main__":
    asyncio.run(get_supabase_credentials())
