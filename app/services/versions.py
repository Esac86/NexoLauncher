import os
import minecraft_launcher_lib as mll
from app.utils.paths import DIR

class VersionService:
    @staticmethod
    def get_versions(version_type="release"):
        all_versions = mll.utils.get_version_list()
        if version_type == "all":
            return [v["id"] for v in all_versions]
        return [v["id"] for v in all_versions if v["type"] == version_type]

    @staticmethod
    def is_installed(version):
        path_version = os.path.join(DIR, "versions", version)
        version_json = os.path.join(path_version, f"{version}.json")
        version_jar = os.path.join(path_version, f"{version}.jar")
        return os.path.exists(path_version) and os.path.exists(version_json) and os.path.exists(version_jar)

    @staticmethod
    def is_optimized_installed(version):
        return VersionService.is_forge_installed(version)

    @staticmethod
    def is_forge_installed(version):
        versions_dir = os.path.join(DIR, "versions")
        if not os.path.exists(versions_dir):
            return False
        
        try:
            forge_loader = mll.mod_loader.get_mod_loader("forge")
            
            loader_versions = forge_loader.get_loader_versions(version, stable_only=False)
            
            if not loader_versions:
                return False
            
            for folder in os.listdir(versions_dir):
                if version in folder and "forge" in folder.lower():
                    forge_path = os.path.join(versions_dir, folder)
                    json_file = os.path.join(forge_path, f"{folder}.json")
                    if os.path.exists(json_file):
                        return True
        except Exception as e:
            print(f"Error verificando Forge: {e}")
        
        return False

    @staticmethod
    def get_installed_forge_version(version):
        versions_dir = os.path.join(DIR, "versions")
        if not os.path.exists(versions_dir):
            return None
        
        try:
            forge_loader = mll.mod_loader.get_mod_loader("forge")
            loader_versions = forge_loader.get_loader_versions(version, stable_only=False)
            
            if not loader_versions:
                return None
            
            for folder in os.listdir(versions_dir):
                if version in folder and "forge" in folder.lower():
                    forge_path = os.path.join(versions_dir, folder)
                    json_file = os.path.join(forge_path, f"{folder}.json")
                    if os.path.exists(json_file):
                        return folder
        except Exception:
            pass
        
        return None

    @staticmethod
    def latest_release():
        versions = VersionService.get_versions("release")
        return versions[0] if versions else None
    
    @staticmethod
    def get_forge_versions(minecraft_version):
        try:
            forge_loader = mll.mod_loader.get_mod_loader("forge")
            
            if not forge_loader.is_minecraft_version_supported(minecraft_version):
                return []
            
            forge_versions = forge_loader.get_loader_versions(minecraft_version, stable_only=False)
            return forge_versions if forge_versions else []
        except Exception as e:
            print(f"Error obteniendo versiones de Forge: {e}")
            return []
    
    @staticmethod
    def is_forge_supported(minecraft_version):
        try:
            forge_loader = mll.mod_loader.get_mod_loader("forge")
            return forge_loader.is_minecraft_version_supported(minecraft_version)
        except Exception:
            return False