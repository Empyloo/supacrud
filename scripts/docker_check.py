import subprocess

def check_docker_running():
    """Check if Docker is running.
    Returns:
        bool: True if Docker is running, raises RuntimeError otherwise.
    """
    try:
        subprocess.check_output(["docker", "ps"])
        return True
    except subprocess.CalledProcessError:
        raise RuntimeError("Docker is not running.")