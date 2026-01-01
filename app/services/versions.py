import os
import minecraft_launcher_lib as mll
from app.utils.paths import MC_DIR

class VersionService:
    @staticmethod
    def get_versions(version_type="release"):
        all_versions = mll.utils.get_version_list()
        if version_type == "all":
            return [v["id"] for v in all_versions]
        return [v["id"] for v in all_versions if v["type"] == version_type]

    @staticmethod
    def is_installed(version):
        path_version = os.path.join(MC_DIR, "versions", version)
        version_json = os.path.join(path_version, f"{version}.json")
        version_jar = os.path.join(path_version, f"{version}.jar")
        return os.path.exists(path_version) and os.path.exists(version_json) and os.path.exists(version_jar)

    @staticmethod
    def latest_release():
        versions = VersionService.get_versions("release")
        return versions[0] if versions else None