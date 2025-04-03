import shutil

class StorageManager:
    def __init__(self):
        pass

    def get_storage_in_gb():
        """
        Get the current storage usage in GB of the system.
        """
        total, used, free = shutil.disk_usage("/")
        return {
            "total": round(total / (1024 ** 3), 2),
            "used": round(used / (1024 ** 3), 2),
            "free": round(free / (1024 ** 3), 2)
        }