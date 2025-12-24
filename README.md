# TorNet v2.0.2

<div align="center">

![TorNet Banner](https://img.shields.io/badge/TorNet-2.0.2-blue)
![Python](https://img.shields.io/badge/Python-3.6%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20EXE%20%7C%20Linux%20%7C%20Android%20APP-blue)

**Automate IP address changes using the Tor network with advanced privacy features**

TorNet is a privacy-focused tool that automates IP address rotation using Tor.  
It is designed to improve anonymity, security, and resistance to tracking across multiple platforms.

</div>

---

## Benefits

- **Enhanced Privacy** – Frequent IP changes make tracking difficult
- **Increased Security** – Reduces exposure to targeted attacks
- **Anonymity** – Routes traffic through the Tor network
- **Ease of Use** – Simple CLI and future GUI apps
- **Anti-Tracking** – Limits profiling by advertisers and trackers
- **Cross-Platform Vision** – Desktop and mobile support

---

## Table of Contents

- [Features](#features)
- [Platform Support](#platform-support)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Commands](#commands)
- [Configuration](#configuration)
- [Country Selection](#country-selection)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- Automatic IP rotation
- Country-based Tor exit nodes
- Kill switch (platform-dependent)
- DNS leak testing
- Auto dependency fixing
- Status monitoring
- Logging & log following
- YAML / JSON configuration
- Scheduled IP rotation

---

## Platform Support

TorNet is designed to be a **real application**, not just a script.

### Supported Platforms

- **Linux** – Native support (primary & most stable)
- **Windows** – Standalone **`.exe` application**
- **Android** – Dedicated **Android app (APK)**

### Platform Notes

- **Linux**
  - Full feature support
  - CLI-based
  - Recommended platform

- **Windows**
  - Distributed as a compiled **EXE**
  - No Python installation required
  - Uses system or bundled Tor

- **Android**
  - Distributed as an **APK**
  - Designed for mobile privacy
  - Uses embedded Tor services

> ⚠️ Some features (like kill switch) may vary due to OS restrictions.

---

## Installation

### Linux

```bash
pip install tornet==2.0.2
````

---

## Quick Start

### Basic Usage

```bash
# Display current IP address
tornet --ip

# Change IP once
tornet --change

# Change IP every 60 seconds, 10 times
tornet --interval 60 --count 10

# Change IP indefinitely every 30-120 seconds (random interval)
tornet --interval 30-120 --count 0

tornet --status  
```

### Start with Country Selection

```bash
# Use US exit nodes, change IP every minute
tornet --country us --interval 60

# Use German exit nodes
tornet --country de --interval 120

# Use random countries (default)
tornet --country auto --interval 60
```

---

## Commands

### Basic Commands

| Command      | Description                             | Example                |
| ------------ | --------------------------------------- | ---------------------- |
| `--ip`       | Display current IP address              | `tornet --ip`          |
| `--change`   | Change IP once and exit                 | `tornet --change`      |
| `--interval` | Time between changes (seconds or range) | `tornet --interval 30` |
| `--count`    | Number of IP changes (0 = infinite)     | `tornet --count 20`    |
| `--stop`     | Stop all Tor services                   | `tornet --stop`        |
| `--version`  | Show version                            | `tornet --version`     |

### Advanced Commands

| Command             | Description               | Example                        |
| ------------------- | ------------------------- | ------------------------------ |
| `--status`          | Show system status        | `tornet --status`              |
| `--country`         | Specify exit country      | `tornet --country jp`          |
| `--schedule`        | Schedule IP changes       | `tornet --schedule 5m`         |
| `--dns-leak-test`   | Test for DNS leaks        | `tornet --dns-leak-test`       |
| `--kill-switch`     | Toggle kill switch        | `tornet --kill-switch`         |
| `--log --follow`    | View/follow logs          | `tornet --log --follow`        |
| `--json`            | JSON output format        | `tornet --ip --json`           |
| `--config`          | Use custom config         | `tornet --config myconfig.yml` |
| `--auto-fix`        | Auto-install dependencies | `tornet --auto-fix`            |
| `--list-countries`  | List country codes        | `tornet --list-countries`      |
| `--restore-default` | Restore default config    | `tornet --restore-default`     |

---

### Schedule Formats

* `30s` - Every 30 seconds
* `5m` - Every 5 minutes
* `2h` - Every 2 hours
* `1d` - Every 1 day

### Interval Formats

* `60` - Exactly 60 seconds
* `30-120` - Random between 30 and 120 seconds

---

## Country Selection

### List Available Countries

```bash
tornet --list-countries
```

### Available Country Codes

```
US - United States        DE - Germany          JP - Japan
GB - United Kingdom       FR - France           CA - Canada
AU - Australia            NL - Netherlands      SE - Sweden
CH - Switzerland          NO - Norway           DK - Denmark
FI - Finland              RU - Russia           CN - China
IN - India                BR - Brazil           MX - Mexico
ZA - South Africa         SG - Singapore        HK - Hong Kong
TW - Taiwan               IT - Italy            ES - Spain
```

### Using Country Selection

```bash
# Use specific country
tornet --country us --interval 60

# Use random countries (default)
tornet --country auto --interval 60

# Restore to default configuration
tornet --restore-default
```

---

## Configuration

### Configuration File

TorNet uses `~/.tornet/config.yml` by default. Create a custom configuration:

```yaml
# ~/.tornet/custom.yml
default:
  interval: 60
  count: 0
  country: auto
  schedule: null

network:
  proxy_port: 9050
  dns_port: 53
  control_port: 9051

security:
  kill_switch: false
  dns_protection: true
  log_level: info

advanced:
  max_retries: 3
  timeout: 30
  verify_ssl: true
```

### Using Custom Config

```bash
tornet --config ~/.tornet/custom.yml --interval 120
```

---

## Advanced Usage

### Kill Switch

```bash
# Enable kill switch (requires root)
sudo tornet --kill-switch

# Disable kill switch
sudo tornet --kill-switch
```

### DNS Leak Testing

```bash
tornet --dns-leak-test
```

### Log Management

```bash
tornet --log
tornet --log --follow
```

### JSON Output

```bash
tornet --ip --json
tornet --change --json
```

### Complete Example

```bash
tornet --country us --interval 120-300 --count 50
tornet --country de --schedule 1h
tornet --config custom.yml --json --interval 30 --count 100
```

---

## Troubleshooting

### Common Issues

1. **Permission Denied Errors**

```bash
sudo tornet --kill-switch
```

2. **Tor Not Starting**

```bash
which tor
sudo systemctl start tor
# or
sudo service tor start
```

3. **Dependency Issues**

```bash
tornet --auto-fix
python3 -c "import requests"
tor --version
```

4. **Connection Issues**

```bash
curl -s https://api.ipify.org
curl --socks5 127.0.0.1:9050 https://api.ipify.org
```

### Log Files

* TorNet Logs: `~/.tornet/tornet.log`
* Tor Configuration: `~/.tornet/torrc.custom`
* Country Settings: `~/.tornet/current_country`

### Status Information

```bash
tornet --status
```

---

## Configuring Your Browser to Use TorNet

**Firefox**:

1. Go to `Preferences` > `General` > `Network Settings`.
2. Select `Manual proxy configuration`.
3. Enter `127.0.0.1` for `SOCKS Host` and `9050` for the `Port`.
4. Check `Proxy DNS when using SOCKS v5`.
5. Click `OK`.

<img src="https://bytebreach.github.io/img/port.png" alt="Firefox Configuration Example" />

---

## Disclaimer

**TorNet is intended for educational and privacy purposes only.**

**Important Notes:**

1. Legal compliance
2. Terms of service
3. Responsible use
4. No warranty
5. Privacy
6. Security

**Ethical Guidelines:**

* Use for privacy protection and security testing
* Respect network resources
* Avoid excessive requests
* Obtain proper authorization before testing

**Limitations:**

* Tor exit nodes may be blocked
* Slower connection speed
* Some features require root
* Not all countries have reliable Tor exit nodes

---

## Contributing

Contributions are welcome! Submit a Pull Request.

---

## License

MIT License - see LICENSE file.

---

## Author

* GitHub: [@ByteBreach](https://github.com/ByteBreach)

### Thanks to all contributors:

<table>
  <tr align="center">
    <td><a href="https://github.com/mr-fidal"><img src="https://avatars.githubusercontent.com/u/154952367?s=100" /><br /><sub><b>Mr-Fidal</b></sub></a></td>
    <td><a href="https://github.com/GH05T-HUNTER5"><img src="https://avatars.githubusercontent.com/u/108191615?s=100" /><br /><sub><b>GH05T-HUNTER5</b></sub></a></td>
  </tr>
</table>

---

## Support

* Give a star ⭐
* Report issues
* Suggest features
* Share with others

---

## Acknowledgements

Thanks to the Tor project developers.

---

<div align="center">
Made with ❤️ for the privacy-conscious community
</div>

---
