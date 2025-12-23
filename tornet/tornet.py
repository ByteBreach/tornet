#!/usr/bin/env python3

import os
import sys
import time
import argparse
import requests
import subprocess
import signal
import shutil
import random
import json
import yaml
import threading
import socket
import select
import re
import tempfile
import shlex
from datetime import datetime, timedelta
from pathlib import Path
from .banner import print_banner

TOOL_NAME = "tornet"
VERSION = "2.2.1"
CONFIG_FILE = os.path.expanduser("~/.tornet/config.yml")
LOG_FILE = os.path.expanduser("~/.tornet/tornet.log")
TORRC_FILE = os.path.expanduser("~/.tornet/torrc.custom")
CURRENT_COUNTRY_FILE = os.path.expanduser("~/.tornet/current_country")

green = "\033[92m"
red = "\033[91m"
white = "\033[97m"
reset = "\033[0m"
cyan = "\033[36m"
yellow = "\033[93m"
blue = "\033[94m"

def log(msg: str):
    print(f"{white} [{green}+{white}]{green} {msg}{reset}")

def error(msg: str, exit_code: int = 1):
    print(f"{white} [{red}!{white}] {red}{msg}{reset}")
    if exit_code > 0:
        sys.exit(exit_code)

def warning(msg: str):
    print(f"{white} [{red}!{white}] {red}{msg}{reset}")

def info(msg: str):
    print(f"{white} [{blue}*{white}]{blue} {msg}{reset}")

def is_root():
    return os.geteuid() == 0

def has_sudo():
    return shutil.which("sudo") is not None

def run_cmd(cmd, use_sudo=False, check=True, capture_output=True):
    if use_sudo and not is_root():
        if not has_sudo():
            error("Root privileges required but sudo not available. Run as root or install sudo.", 2)
        cmd = ["sudo"] + cmd
    
    try:
        if capture_output:
            result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, check=check)
            result.stdout = ""
            result.stderr = ""
            result.returncode = 0
        return result
    except subprocess.CalledProcessError as e:
        if check:
            error(f"Command failed: {' '.join(cmd)}\nError: {e.stderr.strip()}")
        return e

def detect_service_manager():
    if shutil.which("systemctl") and os.path.exists("/run/systemd/system"):
        return "systemctl"
    elif shutil.which("service"):
        return "service"
    return None

def service_action(action):
    service_mgr = detect_service_manager()
    
    if service_mgr == "systemctl":
        cmd = ["systemctl", action, "tor"]
    elif service_mgr == "service":
        cmd = ["service", "tor", action]
    else:
        error("No supported service manager found (systemctl or service)", 3)
    
    result = run_cmd(cmd, use_sudo=True, check=False)
    if result.returncode != 0:
        warning(f"Failed to {action} tor service: {result.stderr.strip()}")

def detect_package_manager():
    managers = [
        ("apt", ["apt-get"]),
        ("dnf", ["dnf"]),
        ("yum", ["yum"]), 
        ("pacman", ["pacman"]),
        ("apk", ["apk"]),
        ("zypper", ["zypper"])
    ]
    
    for pm, binaries in managers:
        if any(shutil.which(binary) for binary in binaries):
            return pm
    return None

def install_package(package_name):
    pm = detect_package_manager()
    if not pm:
        error("No supported package manager found. Please install packages manually.", 4)
    
    if pm == "apt":
        run_cmd(["apt-get", "update"], use_sudo=True)
        run_cmd(["apt-get", "install", "-y", package_name], use_sudo=True)
    elif pm == "dnf":
        run_cmd(["dnf", "install", "-y", package_name], use_sudo=True)
    elif pm == "yum":
        run_cmd(["yum", "install", "-y", package_name], use_sudo=True)
    elif pm == "pacman":
        run_cmd(["pacman", "-Sy", "--noconfirm", package_name], use_sudo=True)
    elif pm == "apk":
        run_cmd(["apk", "add", package_name], use_sudo=True)
    elif pm == "zypper":
        run_cmd(["zypper", "--non-interactive", "install", package_name], use_sudo=True)

def ensure_pip():
    try:
        subprocess.run([sys.executable, "-c", "import pip"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        log("pip not found, attempting to install...")
        
        try:
            run_cmd([sys.executable, "-m", "ensurepip", "--upgrade"])
            return True
        except:
            pass
        
        try:
            pm = detect_package_manager()
            if pm == "apt":
                install_package("python3-pip")
            elif pm in ["dnf", "yum"]:
                install_package("python3-pip")
            elif pm == "pacman":
                install_package("python-pip")
            elif pm == "apk":
                install_package("py3-pip")
            elif pm == "zypper":
                install_package("python3-pip")
            return True
        except:
            error("Failed to install pip. Please install pip manually.", 5)

def ensure_requests():
    try:
        import requests
        return True
    except ImportError:
        log("requests package not found, installing...")
        ensure_pip()
        try:
            run_cmd([sys.executable, "-m", "pip", "install", "requests", "requests[socks]"])
            return True
        except:
            error("Failed to install requests package.", 6)

def is_tor_installed():
    return shutil.which("tor") is not None

def ensure_tor():
    if is_tor_installed():
        return True
    
    log("tor not found, installing...")
    try:
        install_package("tor")
        return True
    except:
        error("Please install Tor manually then try this command again.", 7)

def is_tor_running():
    if shutil.which("pgrep"):
        try:
            subprocess.run(["pgrep", "-x", "tor"], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    try:
        for pid in os.listdir("/proc"):
            if pid.isdigit():
                try:
                    with open(f"/proc/{pid}/comm", "r") as f:
                        if f.read().strip() == "tor":
                            return True
                except:
                    continue
    except:
        pass
    
    return False

def get_current_ip():
    if is_tor_running():
        return get_ip_via_tor()
    else:
        return get_ip_direct()

def get_ip_via_tor():
    url = 'https://api.ipify.org'
    proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }
    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException:
        warning("Having trouble connecting to the Tor network. Please wait a moment.")
        return None

def get_ip_direct():
    try:
        response = requests.get('https://api.ipify.org', timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException:
        warning("Having trouble fetching IP address. Please check your internet connection.")
        return None

def get_ip_with_country():
    url = 'https://ipapi.co/json/'
    proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }
    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('ip'), data.get('country_code'), data.get('country_name')
    except:
        try:
            ip = get_ip_via_tor()
            return ip, None, None
        except:
            return None, None, None

def change_ip(country=None):
    if country and country != "auto":
        configure_tor_country(country)
    
    service_action("reload")
    time.sleep(2)
    return get_current_ip()

def configure_tor_country(country_code):
    os.makedirs(os.path.dirname(TORRC_FILE), exist_ok=True)
    
    try:
        with open(TORRC_FILE, "w") as f:
            f.write(f"ExitNodes {{{country_code.upper()}}}\n")
            f.write("StrictNodes 1\n")
        
        with open(CURRENT_COUNTRY_FILE, "w") as f:
            f.write(country_code.upper())
        
        log(f"Configured Tor to use exit nodes from {country_code.upper()}")
        
        service_action("stop")
        time.sleep(1)
        
        tor_cmd = ["tor", "-f", TORRC_FILE, "--RunAsDaemon", "1"]
        result = run_cmd(tor_cmd, use_sudo=False, check=False)
        
        if result.returncode != 0:
            log("Starting Tor with custom configuration...")
            time.sleep(3)
        
    except Exception as e:
        warning(f"Could not configure Tor country: {e}")

def restore_default_tor():
    try:
        if os.path.exists(TORRC_FILE):
            os.remove(TORRC_FILE)
        if os.path.exists(CURRENT_COUNTRY_FILE):
            os.remove(CURRENT_COUNTRY_FILE)
        
        service_action("stop")
        time.sleep(1)
        service_action("start")
        time.sleep(2)
        
        log("Restored default Tor configuration")
    except Exception as e:
        warning(f"Could not restore default Tor configuration: {e}")

def get_current_country():
    if os.path.exists(CURRENT_COUNTRY_FILE):
        try:
            with open(CURRENT_COUNTRY_FILE, "r") as f:
                return f.read().strip()
        except:
            pass
    return "Auto (Random)"

def print_ip(ip):
    log(f"Your IP address is: {white}{ip}")

def change_ip_repeatedly(interval_str, count, country=None, json_output=False):
    if count == 0:
        while True:
            try:
                sleep_time = parse_interval(interval_str)
                time.sleep(sleep_time)
                new_ip = change_ip(country)
                if new_ip:
                    if json_output:
                        print(json.dumps({"timestamp": time.time(), "ip": new_ip}))
                    else:
                        print_ip(new_ip)
            except KeyboardInterrupt:
                break
    else:
        for i in range(count):
            try:
                sleep_time = parse_interval(interval_str)
                time.sleep(sleep_time)
                new_ip = change_ip(country)
                if new_ip:
                    if json_output:
                        print(json.dumps({"timestamp": time.time(), "ip": new_ip, "count": i+1}))
                    else:
                        print_ip(new_ip)
            except KeyboardInterrupt:
                break

def parse_interval(interval_str):
    try:
        if "-" in str(interval_str):
            start, end = map(int, str(interval_str).split("-", 1))
            return random.randint(start, end)
        else:
            return int(interval_str)
    except ValueError:
        error("Invalid interval format. Use number or range (e.g., '60' or '30-120')", 8)

def auto_fix():
    log("Running auto-fix...")
    ensure_pip()
    ensure_requests()
    ensure_tor()
    log("Auto-fix complete")

def stop_services():
    restore_default_tor()
    try:
        subprocess.run(["pkill", "-f", "tor"], check=False, capture_output=True)
    except:
        pass
    try:
        subprocess.run(["pkill", "-f", TOOL_NAME], check=False, capture_output=True)
    except:
        pass
    log(f"Tor services and {TOOL_NAME} processes stopped.")

def signal_handler(sig, frame):
    stop_services()
    print(f"\n{white} [{red}!{white}] {red}Program terminated by user.{reset}")
    sys.exit(0)

def check_internet_connection():
    try:
        response = requests.get('http://www.google.com', timeout=5)
        return True
    except requests.RequestException:
        error("Internet connection required but not available.", 9)

def initialize_environment():
    service_action("start")
    log("Tor service started. Please wait for Tor to establish connection.")
    log("Configure your browser to use Tor proxy (127.0.0.1:9050) for anonymity.")

def show_status():
    tor_installed = is_tor_installed()
    tor_running = is_tor_running()
    ip, country_code, country_name = get_ip_with_country()
    current_country = get_current_country()
    service_mgr = detect_service_manager()
    pm = detect_package_manager()
    print(f"{white} ─────────────[{green} TorNet Status {white}]─────────────{reset}")
    print(f"{white} {cyan}Tor Installed:{reset} {'✓' if tor_installed else '✗'}")
    print(f"{white} {cyan}Tor Running:{reset} {'✓' if tor_running else '✗'}")
    
    if ip:
        print(f"{white} {cyan}Current IP:{reset} {white}{ip}{reset}")
        if country_code and country_name:
            print(f"{white} {cyan}IP Country:{reset} {country_name} ({country_code})")
    else:
        print(f"{white} {cyan}Current IP:{reset} {red}Unknown{reset}")
    
    print(f"{white} {cyan}Configured Country:{reset} {current_country}")
    print(f"{white} {cyan}Service Manager:{reset} {service_mgr or 'Unknown'}")
    print(f"{white} {cyan}Package Manager:{reset} {pm or 'Unknown'}")
    print(f"{white} {cyan}Config File:{reset} {CONFIG_FILE}")
    print(f"{white} {cyan}Log File:{reset} {LOG_FILE}")
    print(f"{white}──────────────────────────────────────────{reset}")

def change_ip_once(country=None, json_output=False):
    log("Changing IP address...")
    new_ip = change_ip(country)
    if new_ip:
        if json_output:
            print(json.dumps({"action": "ip_change", "timestamp": time.time(), "ip": new_ip}))
        else:
            print_ip(new_ip)
            log("IP changed successfully!")
    else:
        if json_output:
            print(json.dumps({"action": "ip_change", "timestamp": time.time(), "error": "Failed to change IP"}))
        else:
            warning("Failed to change IP address")

def parse_schedule(schedule_str):
    unit = schedule_str[-1].lower()
    value = int(schedule_str[:-1])
    
    if unit == 's':
        return value
    elif unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 86400
    else:
        error("Invalid schedule format. Use like '30s', '5m', '2h', '1d'", 12)

def run_scheduled(schedule_str, country=None, json_output=False):
    interval = parse_schedule(schedule_str)
    log(f"Scheduled IP change every {schedule_str}")
    change_ip_repeatedly(str(interval), 0, country, json_output)

def dns_leak_test():
    test_urls = [
        "https://dnsleaktest.com",
        "https://ipleak.net",
        "https://www.dnsleaktest.com"
    ]
    print(f"{white}─────────────[{green} DNS Leak Test {white}]─────────────{reset}")
    
    for url in test_urls:
        try:
            proxies = {
                'http': 'socks5://127.0.0.1:9050',
                'https': 'socks5://127.0.0.1:9050'
            }
            response = requests.get(url, proxies=proxies, timeout=10)
            if response.status_code == 200:
                print(f"{white} {cyan}{url}:{reset} {green}Accessible via Tor ✓{reset}")
            else:
                print(f"{white} {cyan}{url}:{reset} {red}Inaccessible via Tor ✗{reset}")
        except:
            print(f"{white} {cyan}{url}:{reset} {red}Failed to connect via Tor ✗{reset}")
    
    print(f"{white}──────────────────────────────────────────{reset}")
    info("For detailed DNS leak test, visit: https://dnsleaktest.com while using Tor")

def toggle_kill_switch():
    iptables = shutil.which("iptables")
    if not iptables:
        error("iptables not found. Kill switch requires iptables.", 13)
    
    if not is_root():
        error("Kill switch requires root privileges. Run with sudo.", 14)
    
    cmd = [iptables, "-L"]
    result = run_cmd(cmd, use_sudo=False, check=False)
    
    if "TORNET-KILLSWITCH" in result.stdout:
        cmd = [iptables, "-D", "OUTPUT", "-j", "TORNET-KILLSWITCH"]
        run_cmd(cmd, use_sudo=False)
        cmd = [iptables, "-F", "TORNET-KILLSWITCH"]
        run_cmd(cmd, use_sudo=False)
        cmd = [iptables, "-X", "TORNET-KILLSWITCH"]
        run_cmd(cmd, use_sudo=False)
        log("Kill switch disabled")
    else:
        cmd = [iptables, "-N", "TORNET-KILLSWITCH"]
        run_cmd(cmd, use_sudo=False)
        cmd = [iptables, "-A", "TORNET-KILLSWITCH", "-d", "127.0.0.1/8", "-j", "ACCEPT"]
        run_cmd(cmd, use_sudo=False)
        cmd = [iptables, "-A", "TORNET-KILLSWITCH", "-d", "192.168.0.0/16", "-j", "ACCEPT"]
        run_cmd(cmd, use_sudo=False)
        cmd = [iptables, "-A", "TORNET-KILLSWITCH", "-d", "172.16.0.0/12", "-j", "ACCEPT"]
        run_cmd(cmd, use_sudo=False)
        cmd = [iptables, "-A", "TORNET-KILLSWITCH", "-d", "10.0.0.0/8", "-j", "ACCEPT"]
        run_cmd(cmd, use_sudo=False)
        cmd = [iptables, "-A", "TORNET-KILLSWITCH", "-p", "tcp", "--dport", "9050", "-j", "ACCEPT"]
        run_cmd(cmd, use_sudo=False)
        cmd = [iptables, "-A", "TORNET-KILLSWITCH", "-j", "DROP"]
        run_cmd(cmd, use_sudo=False)
        cmd = [iptables, "-A", "OUTPUT", "-j", "TORNET-KILLSWITCH"]
        run_cmd(cmd, use_sudo=False)
        log("Kill switch enabled - All traffic must go through Tor")

def follow_logs(follow=False):
    log_dir = os.path.dirname(LOG_FILE)
    os.makedirs(log_dir, exist_ok=True)
    
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write(f"TorNet Log File - Created {datetime.now()}\n")
    
    if follow:
        try:
            with open(LOG_FILE, "r") as f:
                f.seek(0, 2)
                while True:
                    line = f.readline()
                    if line:
                        print(line.strip())
                    else:
                        time.sleep(0.1)
        except KeyboardInterrupt:
            return
    else:
        try:
            with open(LOG_FILE, "r") as f:
                content = f.read()
                if content:
                    print(content)
                else:
                    log("Log file is empty")
        except Exception as e:
            error(f"Could not read log file: {e}", 15)

def load_config(config_file):
    if not os.path.exists(config_file):
        return {}
    
    try:
        with open(config_file, "r") as f:
            if config_file.endswith(".yml") or config_file.endswith(".yaml"):
                return yaml.safe_load(f) or {}
            elif config_file.endswith(".json"):
                return json.load(f)
            else:
                warning(f"Unsupported config format: {config_file}")
                return {}
    except Exception as e:
        warning(f"Could not load config file: {e}")
        return {}

def save_config(config_file, config):
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    try:
        with open(config_file, "w") as f:
            if config_file.endswith(".yml") or config_file.endswith(".yaml"):
                yaml.dump(config, f, default_flow_style=False)
            elif config_file.endswith(".json"):
                json.dump(config, f, indent=2)
        log(f"Config saved to {config_file}")
    except Exception as e:
        warning(f"Could not save config: {e}")

def get_ip_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def get_country_name(country_code):
    country_map = {
        "US": "United States",
        "GB": "United Kingdom",
        "DE": "Germany",
        "FR": "France",
        "CA": "Canada",
        "AU": "Australia",
        "JP": "Japan",
        "CN": "China",
        "IN": "India",
        "BR": "Brazil",
        "RU": "Russia",
        "KR": "South Korea",
        "IT": "Italy",
        "ES": "Spain",
        "NL": "Netherlands",
        "SE": "Sweden",
        "CH": "Switzerland",
        "NO": "Norway",
        "DK": "Denmark",
        "FI": "Finland",
        "PL": "Poland",
        "TR": "Turkey",
        "MX": "Mexico",
        "ZA": "South Africa",
        "EG": "Egypt",
        "NG": "Nigeria",
        "KE": "Kenya",
        "SG": "Singapore",
        "HK": "Hong Kong",
        "TW": "Taiwan",
        "IL": "Israel",
        "AE": "United Arab Emirates",
        "SA": "Saudi Arabia",
    }
    return country_map.get(country_code.upper(), country_code.upper())

def list_countries():
    countries = {
        "US": "United States",
        "GB": "United Kingdom",
        "DE": "Germany",
        "FR": "France",
        "CA": "Canada",
        "AU": "Australia",
        "JP": "Japan",
        "NL": "Netherlands",
        "SE": "Sweden",
        "CH": "Switzerland",
        "NO": "Norway",
        "DK": "Denmark",
        "FI": "Finland",
        "RU": "Russia",
        "CN": "China",
        "IN": "India",
        "BR": "Brazil",
        "MX": "Mexico",
        "ZA": "South Africa",
        "SG": "Singapore",
        "HK": "Hong Kong",
        "TW": "Taiwan",
    }
    print(f"{white}─────────────[{green} Available Countries {white}]─────────────{reset}")
    for code, name in countries.items():
        print(f"{white} {cyan}{code}:{reset} {name}")
    print(f"{white} {cyan}AUTO:{reset} Random country (default)")
    print(f"{white}──────────────────────────────────────────────{reset}")
    info("Use: tornet --country CODE (e.g., tornet --country US)")

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)

    parser = argparse.ArgumentParser(description="TorNet - Automate IP address changes using Tor")
    parser.add_argument('--interval', type=str, default='60', help='Time in seconds between IP changes (or range like "30-120")')
    parser.add_argument('--count', type=int, default=10, help='Number of times to change IP. If 0, change IP indefinitely')
    parser.add_argument('--ip', action='store_true', help='Display current IP address and exit')
    parser.add_argument('--auto-fix', action='store_true', help='Automatically install missing dependencies')
    parser.add_argument('--stop', action='store_true', help='Stop all Tor services and tornet processes')
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--change', action='store_true', help='Change IP once')
    parser.add_argument('--country', type=str, help='Use specific country exit nodes (e.g., "us", "de", "jp", "auto")')
    parser.add_argument('--schedule', type=str, help='Schedule IP changes (e.g., "30s", "5m", "2h", "1d")')
    parser.add_argument('--dns-leak-test', action='store_true', help='Test for DNS leaks')
    parser.add_argument('--kill-switch', action='store_true', help='Toggle kill switch')
    parser.add_argument('--log', action='store_true', help='Show log file')
    parser.add_argument('--follow', action='store_true', help='Follow log file (use with --log)')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--config', type=str, help='Use custom config file')
    parser.add_argument('--list-countries', action='store_true', help='List available country codes')
    parser.add_argument('--restore-default', action='store_true', help='Restore default Tor configuration')
    
    args = parser.parse_args()

    config_file = args.config or CONFIG_FILE
    config = load_config(config_file)

    if args.stop:
        stop_services()
        return

    if args.restore_default:
        restore_default_tor()
        return

    if args.list_countries:
        list_countries()
        return

    if args.status:
        show_status()
        return

    if args.ip:
        ip = get_current_ip()
        if ip:
            if args.json:
                ip_info = get_ip_info(ip)
                output = {"ip": ip}
                if ip_info and ip_info.get("status") == "success":
                    output.update(ip_info)
                print(json.dumps(output))
            else:
                print_ip(ip)
        return

    if args.change:
        change_ip_once(args.country, args.json)
        return

    if args.dns_leak_test:
        dns_leak_test()
        return

    if args.kill_switch:
        toggle_kill_switch()
        return

    if args.log:
        follow_logs(args.follow)
        return

    if args.schedule:
        run_scheduled(args.schedule, args.country, args.json)
        return

    if args.auto_fix:
        auto_fix()
        return

    if not is_tor_installed():
        error("Tor is not installed. Please install Tor manually then try this command again.", 10)

    try:
        import requests
    except ImportError:
        error("requests package not found. Run with --auto-fix to install automatically.", 11)

    check_internet_connection()
    
    if not args.json:
        print_banner()
    
    initialize_environment()
    
    time.sleep(5)
    
    change_ip_repeatedly(args.interval, args.count, args.country, args.json)

if __name__ == "__main__":
    main()
