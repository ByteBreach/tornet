#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import platform

from typing import Optional, List, Tuple

REQUIRED_BINARIES = {
    "python3": "Python 3 interpreter",
    "tor": "Tor binary",
}

PACKAGE_MANAGERS = [
    ("apt", "Debian/Ubuntu/LinuxMint", ["apt"]),
    ("dnf", "Fedora/RHEL/CentOS (modern)", ["dnf"]),
    ("yum", "RHEL/CentOS (legacy)", ["yum"]),
    ("pacman", "Arch/Manjaro", ["pacman"]),
    ("apk", "Alpine", ["apk"]),
    ("zypper", "openSUSE/SLE", ["zypper"]),
]

TOR_PACKAGE_NAMES = {
    "apt": "tor",
    "dnf": "tor",
    "yum": "tor",
    "pacman": "tor",
    "apk": "tor",
    "zypper": "tor",
}

PIP_SYSTEM_PACKAGES = {
    "apt": "python3-pip",
    "dnf": "python3-pip",
    "yum": "python3-pip",
    "pacman": "python-pip",
    "apk": "py3-pip",
    "zypper": "python3-pip",
}

def log(msg: str):
    print(f"[INFO] {msg}", file=sys.stderr)

def error(msg: str, exit_code: int = 1):
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(exit_code)

def is_root() -> bool:
    return os.geteuid() == 0

def which(bin_name: str) -> Optional[str]:
    return shutil.which(bin_name)

def run_cmd(cmd: List[str], use_sudo: bool = False, check: bool = True) -> subprocess.CompletedProcess:
    if use_sudo and not is_root():
        sudo_path = which("sudo")
        if not sudo_path:
            error("Sudo is required but not found. Please run as root or install sudo.", 2)
        cmd = [sudo_path] + cmd
    log(f"Running command: {' '.join(cmd)}")
    try:
        return subprocess.run(cmd, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {' '.join(cmd)}", file=sys.stderr)
        if e.stdout:
            print(f"[STDOUT]\n{e.stdout}", file=sys.stderr)
        if e.stderr:
            print(f"[STDERR]\n{e.stderr}", file=sys.stderr)
        sys.exit(e.returncode)

def read_os_release() -> dict:
    os_release = {}
    try:
        with open("/etc/os-release", "r") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    os_release[k] = v.strip('"')
    except Exception:
        pass
    return os_release

def detect_package_manager() -> Tuple[Optional[str], Optional[str]]:
    os_release = read_os_release()
    distro_id = os_release.get("ID", "").lower()
    distro_like = os_release.get("ID_LIKE", "").lower()
    for pm, desc, ids in PACKAGE_MANAGERS:
        if distro_id in [i.lower() for i in ids] or any(i in distro_like for i in ids):
            if which(pm):
                return pm, desc
    for pm, desc, ids in PACKAGE_MANAGERS:
        if which(pm):
            return pm, desc
    return None, None

def ensure_binary(bin_name: str, description: str):
    if not which(bin_name):
        error(f"Required binary '{bin_name}' ({description}) not found in PATH.", 3)

def ensure_pip(pm: Optional[str]):
    log("Checking for pip module...")
    try:
        subprocess.run([sys.executable, "-c", "import pip"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log("pip is already installed.")
        return
    except subprocess.CalledProcessError:
        log("pip not found. Attempting to install pip...")

    if pm and pm in PIP_SYSTEM_PACKAGES:
        pkg = PIP_SYSTEM_PACKAGES[pm]
        install_system_package(pm, pkg)
    else:
        log("Attempting to bootstrap pip using ensurepip...")
        try:
            run_cmd([sys.executable, "-m", "ensurepip", "--upgrade"], use_sudo=not is_root())
        except Exception as e:
            error("Failed to install pip using ensurepip. Please install pip manually.", 4)

    log("Upgrading pip to latest version...")
    run_cmd([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], use_sudo=not is_root())

def ensure_requests():
    log("Checking for 'requests' Python package...")
    try:
        subprocess.run([sys.executable, "-c", "import requests"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log("'requests' is already installed.")
    except subprocess.CalledProcessError:
        log("'requests' not found. Installing via pip...")
        run_cmd([sys.executable, "-m", "pip", "install", "requests"], use_sudo=not is_root())
    log("Ensuring 'requests[socks]' is installed...")
    run_cmd([sys.executable, "-m", "pip", "install", "requests[socks]"], use_sudo=not is_root())

def install_system_package(pm: str, pkg: str):
    log(f"Installing system package '{pkg}' using {pm}...")
    if pm == "apt":
        run_cmd(["apt-get", "update"], use_sudo=not is_root())
        run_cmd(["apt-get", "install", "-y", pkg], use_sudo=not is_root())
    elif pm == "dnf":
        run_cmd(["dnf", "install", "-y", pkg], use_sudo=not is_root())
    elif pm == "yum":
        run_cmd(["yum", "install", "-y", pkg], use_sudo=not is_root())
    elif pm == "pacman":
        run_cmd(["pacman", "-Sy", "--noconfirm", pkg], use_sudo=not is_root())
    elif pm == "apk":
        run_cmd(["apk", "add", pkg], use_sudo=not is_root())
    elif pm == "zypper":
        run_cmd(["zypper", "--non-interactive", "install", pkg], use_sudo=not is_root())
    else:
        error(f"Unknown or unsupported package manager: {pm}", 5)

def ensure_tor(pm: Optional[str]):
    log("Checking for 'tor' binary...")
    if which("tor"):
        log("'tor' is already installed.")
        return
    if not pm:
        error("Please install Tor manually. Could not detect a supported package manager.", 6)
    tor_pkg = TOR_PACKAGE_NAMES.get(pm, "tor")
    install_system_package(pm, tor_pkg)
    if not which("tor"):
        error("Failed to install 'tor'. Please install Tor manually and try again.", 7)
    log("'tor' installed successfully.")

def check_python3():
    if not which("python3"):
        error("python3 is required but not found in PATH.", 8)

def main():
    log("Starting cross-distribution dependency checker for pip, requests, and tor.")

    check_python3()

    pm, pm_desc = detect_package_manager()
    if pm:
        log(f"Detected package manager: {pm} ({pm_desc})")
    else:
        log("No supported package manager detected. Will attempt to use ensurepip for pip, but cannot install system packages.")

    ensure_pip(pm)
    ensure_requests()
    ensure_tor(pm)

    log("All dependencies are installed and verified.")
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        error("Interrupted by user.", 130)
