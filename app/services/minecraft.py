import os
import subprocess
import threading
import shutil
import re
import requests
import minecraft_launcher_lib as mll
from app.utils.paths import DIR
from app.services.versions import VersionService

MIN_VALID_JAR_SIZE = 100000
OPTIFINE_CHUNK_SIZE = 8192
PROGRESS_UPDATE_INTERVAL = 20
MAX_FORGE_RETRIES = 2
REQUEST_TIMEOUT = 15
DOWNLOAD_TIMEOUT = 30

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://optifine.net/downloads',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

FIRST_RUN_OPTIONS = (
    "lang:es_mx\n"
    "narrator:0\n"
    "tutorialStep:none\n"
    "onboardAccessibility:false\n"
    "guiScale:2\n"
    "skipMultiplayerWarning:true\n"
)

REGEX_PATTERNS = {
    'versions': re.compile(r'Minecraft (\d+\.\d+(?:\.\d+)?)</h2>'),
    'main_link': re.compile(
        r'href="https?://adfoc\.us/serve/sitelinks/\?id=\d+&url='
        r'(https?://optifine\.net/adloadx\?f=((?:preview_)?OptiFine_[^&"]+\.jar)&x=([^"]+))"'
    ),
    'mirror_link': re.compile(
        r'<td class=[\'"]colMirror[\'"]><a href="(https?://optifine\.net/adloadx\?f=((?:preview_)?OptiFine_[^"]+\.jar))"'
    ),
    'general_link': re.compile(r'href="(https?://optifine\.net/adloadx\?f=((?:preview_)?OptiFine_[^"]+\.jar))"'),
    'download_link': re.compile(r'href="(https?://optifine\.net/downloadx\?f=((?:preview_)?OptiFine_[^"]+\.jar)[^"]*)"'),
    'any_optifine': re.compile(r'href="([^"]*OptiFine[^"]*\.jar[^"]*)"'),
}


class PlayService:
    def __init__(self, on_play_callback, on_state_change):
        self.on_play_callback = on_play_callback
        self.on_state_change = on_state_change
        self.is_running = False
        self.minecraft_process = None
        self._lock = threading.Lock()

    def launch(self, username, version, ms_account=None, mod_type="vanilla"):
        with self._lock:
            if self.is_running:
                return
            if not username:
                self.on_state_change("error", "Usuario requerido")
                return
            self.is_running = True
        
        threading.Thread(
            target=self._run,
            args=(username, version, ms_account, mod_type),
            daemon=True
        ).start()

    def _first_run_setup(self):
        options_path = os.path.join(DIR, "options.txt")
        if os.path.exists(options_path):
            return
        
        try:
            with open(options_path, "w", encoding="utf-8") as f:
                f.write(FIRST_RUN_OPTIONS)
        except Exception as e:
            print(f"Error creando options.txt: {e}")

    def _install_vanilla(self, version):
        path_version = os.path.join(DIR, "versions", version)
        if not os.path.exists(path_version):
            self.on_state_change("installing")
            mll.install.install_minecraft_version(version, DIR)

    def _clean_corrupt_libraries(self):
        try:
            libraries_path = os.path.join(DIR, "libraries", "org", "ow2", "asm")
            if os.path.exists(libraries_path):
                shutil.rmtree(libraries_path, ignore_errors=True)
        except Exception as e:
            print(f"Error limpiando bibliotecas: {e}")

    def _extract_version_section(self, html, mc_version):
        version_marker = f'Minecraft {mc_version}</h2>'
        
        if version_marker not in html:
            all_versions = REGEX_PATTERNS['versions'].findall(html)
            if all_versions:
                print(f"📋 Versiones disponibles: {', '.join(all_versions[:10])}")
            return None
        
        start = html.find(version_marker)
        next_version = html.find('<h2 class="downloadLineHeader">', start + 100)
        end = next_version if next_version != -1 else start + 5000
        
        return html[start:end]

    def _find_optifine_in_patterns(self, version_section, allow_preview):
        patterns = [
            ('main_link', 3),  
            ('mirror_link', 2),
            ('general_link', 2),
            ('download_link', 2),
        ]
        
        for pattern_key, group_count in patterns:
            pattern = REGEX_PATTERNS[pattern_key]
            matches = pattern.finditer(version_section)
            
            for match in matches:
                url = match.group(1).replace('&amp;', '&')
                filename = match.group(2)
                
                if 'preview_' in filename.lower() and not allow_preview:
                    continue
                
                if group_count == 3:
                    x_param = match.group(3)
                    if '&x=' not in url:
                        url = f"{url}&x={x_param}"
                else:
                    x_match = re.search(rf'{re.escape(filename)}(?:&|&amp;)x=([a-f0-9]+)', version_section)
                    if x_match:
                        url = f"{url}&x={x_match.group(1)}"
                
                url = url.replace('http://', 'https://', 1) if url.startswith('http://') else url
                return url, filename
        
        return None, None

    def _get_optifine_mirror_url(self, mc_version):
        try:
            response = requests.get(
                "https://optifine.net/downloads",
                headers=HTTP_HEADERS,
                timeout=REQUEST_TIMEOUT
            )
            
            version_section = self._extract_version_section(response.text, mc_version)
            if not version_section:
                return None, None
            
            url, filename = self._find_optifine_in_patterns(version_section, allow_preview=False)
            
            if not url:
                url, filename = self._find_optifine_in_patterns(version_section, allow_preview=True)
            
            if url and filename:
                return url, filename
            
            any_links = REGEX_PATTERNS['any_optifine'].findall(version_section)
            if any_links:
                print(f"Enlaces encontrados: {any_links[:5]}")
            
            return None, None
            
        except Exception as e:
            print(f"❌ Error obteniendo URL de OptiFine: {e}")
            return None, None

    def _validate_jar_file(self, content):
        if len(content) < MIN_VALID_JAR_SIZE:
            if b'<html' in content[:500].lower() or b'<!doctype' in content[:500].lower():
                raise Exception("Se descargó una página HTML. OptiFine requiere descarga manual.")
            raise Exception(f"Archivo demasiado pequeño ({len(content)} bytes)")
        
        if not content.startswith(b'PK'):
            raise Exception("El archivo no es un JAR válido")

    def _download_with_progress(self, response, filename):
        content = b''
        total_size = int(response.headers.get('content-length', 0))
        
        if total_size > 0:
            print(f"📦 Tamaño: {total_size / 1024 / 1024:.2f} MB")
        
        downloaded = 0
        last_progress = 0
        
        for chunk in response.iter_content(chunk_size=OPTIFINE_CHUNK_SIZE):
            if chunk:
                content += chunk
                downloaded += len(chunk)
                
                if total_size > 0:
                    progress = int((downloaded / total_size) * 100)
                    if progress >= last_progress + PROGRESS_UPDATE_INTERVAL:
                        print(f"📊 Progreso: {progress}%")
                        last_progress = progress
        
        return content

    def _download_optifine(self, mc_version, mods_folder):
        url, filename = self._get_optifine_mirror_url(mc_version)
        
        if not url or not filename:
            raise Exception(f"OptiFine no está disponible para Minecraft {mc_version}")
        
        os.makedirs(mods_folder, exist_ok=True)
        optifine_path = os.path.join(mods_folder, filename)
        
        if os.path.exists(optifine_path):
            if os.path.getsize(optifine_path) > MIN_VALID_JAR_SIZE:
                return optifine_path
            os.remove(optifine_path)
        
        self.on_state_change("installing")
        
        session = requests.Session()
        
        response1 = session.get(url, headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        
        if response1.status_code != 200:
            raise Exception(f"Error en página intermedia (HTTP {response1.status_code})")
        
        download_pattern = rf'downloadx\?f={re.escape(filename)}(?:&|&amp;)x=([a-f0-9]+)'
        match = re.search(download_pattern, response1.text, re.IGNORECASE)
        
        download_url = (
            f"https://optifine.net/downloadx?f={filename}&x={match.group(1)}"
            if match else f"https://optifine.net/downloadx?f={filename}"
        )
        
        
        response2 = session.get(
            download_url,
            headers=HTTP_HEADERS,
            timeout=DOWNLOAD_TIMEOUT,
            allow_redirects=True,
            stream=True
        )
        
        if response2.status_code != 200:
            raise Exception(f"Error HTTP {response2.status_code} al descargar")
        
        content = self._download_with_progress(response2, filename)
        self._validate_jar_file(content)
        
        with open(optifine_path, 'wb') as f:
            f.write(content)
        
        return optifine_path

    def _install_optimized(self, version):
        forge_version = self._install_forge(version)
        mods_folder = os.path.join(DIR, "mods")
        self._download_optifine(version, mods_folder)
        return forge_version

    def _install_forge(self, version, retry_count=0):
        if not VersionService.is_installed(version):
            self._install_vanilla(version)
        
        existing = VersionService.get_installed_forge_version(version)
        if existing:
            return existing
        
        self.on_state_change("installing")
        
        try:
            if retry_count > 0:
                self._clean_corrupt_libraries()
            
            forge_loader = mll.mod_loader.get_mod_loader("forge")
            
            if not forge_loader.is_minecraft_version_supported(version):
                raise Exception(f"Forge no disponible para Minecraft {version}")
            
            all_versions = forge_loader.get_loader_versions(version, stable_only=False)
            
            if not all_versions:
                raise Exception(f"No hay versiones de Forge para {version}")
            
            def parse_version(v):
                try:
                    return tuple(int(p) for p in v.split('.') if p.isdigit())
                except:
                    return (0, 0, 0)
            
            latest_forge = max(all_versions, key=parse_version)
            
            installed_version = forge_loader.install(
                minecraft_version=version,
                minecraft_directory=DIR,
                loader_version=latest_forge,
                callback={
                    "setStatus": lambda x: print(f"Status: {x}"),
                    "setProgress": lambda x: None,
                    "setMax": lambda x: None
                }
            )
            
            return installed_version
            
        except Exception as e:
            error_msg = str(e)
            
            if ("Checksum" in error_msg or "wrong Checksum" in error_msg) and retry_count < MAX_FORGE_RETRIES:
                return self._install_forge(version, retry_count + 1)
            
            if "UnsupportedVersion" in error_msg or "not supported" in error_msg.lower():
                raise Exception(
                    f"Forge no disponible para {version}. "
                    "Prueba: 1.21.1, 1.20.1, 1.19.2, 1.18.2 o 1.16.5"
                )
            elif "java" in error_msg.lower() and "not found" in error_msg.lower():
                raise Exception("Java no encontrado. Instala Java correctamente.")
            elif "Checksum" in error_msg:
                raise Exception("Error de descarga persistente. Verifica tu conexión.")
            
            raise Exception(f"Error instalando Forge: {error_msg}")

    def _run(self, username, version, ms_account=None, mod_type="vanilla"):
        try:
            launch_version = (
                self._install_optimized(version) if mod_type == "modded"
                else (self._install_vanilla(version), version)[1]
            )
            
            self._first_run_setup()
            self.on_state_change("hide_to_tray")
            self.on_state_change("playing")
            
            options = {
                "username": ms_account.get("name", username) if ms_account else username,
                "uuid": ms_account.get("id", "") if ms_account else "",
                "token": ms_account.get("access_token", "") if ms_account else "",
                "jvmArguments": self._get_jvm_arguments()
            }
            
            cmd = mll.command.get_minecraft_command(launch_version, DIR, options)
            
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            
            self.minecraft_process = subprocess.Popen(
                cmd,
                cwd=DIR,
                creationflags=creationflags,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.minecraft_process.wait()
            self.on_state_change("ready")
            
        except Exception as e:
            self.on_state_change("error", str(e))
        finally:
            with self._lock:
                self.minecraft_process = None
                self.is_running = False

    @staticmethod
    def _get_jvm_arguments():
        return [
            "-Xmx2G",
            "-XX:+UseG1GC",
            "-XX:+UnlockExperimentalVMOptions",
            "-XX:G1NewSizePercent=20",
            "-XX:G1ReservePercent=20",
            "-XX:MaxGCPauseMillis=50",
            "-XX:G1HeapRegionSize=32M"
        ]

    def stop(self):
        with self._lock:
            if self.minecraft_process:
                try:
                    self.minecraft_process.terminate()
                    self.minecraft_process.wait(timeout=5)
                except Exception:
                    try:
                        self.minecraft_process.kill()
                    except Exception:
                        pass
                finally:
                    self.minecraft_process = None
                    self.is_running = False