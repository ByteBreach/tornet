# TorNet v2.0.1

<div align="center">

![TorNet Banner](https://img.shields.io/badge/TorNet-2.0.1-blue)
![Python](https://img.shields.io/badge/Python-3.6%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey)

**Automate IP address changes using Tor network with advanced features**
- TorNet is a Python package that automates IP address changes using Tor. It is a top tool for securing your networks by frequently changing your IP address, making it difficult for trackers to pinpoint your location.
</div>

## Benefits

- **Enhanced Privacy** : By regularly changing your IP address, TorNet makes it much harder for websites and trackers to monitor your online activity.
- **Increased Security** : Frequent IP changes can help protect you from targeted attacks and make it more difficult for malicious actors to track your online presence.
- **Anonymity** : Using Tor, TorNet helps you maintain a high level of anonymity while browsing the internet.
- **Ease of Use** : TorNet is designed to be simple and easy to use, whether you prefer command-line tools or integrating it directly into your Python scripts.
- **Protection from Tracking** : With your IP address changing frequently, tracking services and advertisers will find it more challenging to build a profile on you.
- **Peace of Mind**: Knowing that your IP address is regularly changed can give you confidence in your online privacy and security.

## Table of Contents
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Commands](#-commands)
- [Configuration](#-configuration)
- [Country Selection](#-country-selection)

## Features

- **Automatic IP Rotation** - Change your IP address at regular intervals
- **Country Selection** - Choose exit nodes from specific countries
- **Kill Switch** - Block all non-Tor traffic for maximum privacy
- **DNS Leak Test** - Verify your anonymity setup
- **Auto-Fix** - Automatic dependency installation
- **Status Monitoring** - Real-time system status display
- **Logging** - Detailed log file with follow capability
- **Configurable** - Custom configuration via YAML/JSON files
- **Scheduling** - Flexible scheduling options (seconds, minutes, hours, days)

## Installation

```bash
pip install tornet==2.0.1
```

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

## Commands

### Basic Commands
| Command | Description | Example |
|---------|-------------|---------|
| `--ip` | Display current IP address | `tornet --ip` |
| `--change` | Change IP once and exit | `tornet --change` |
| `--interval` | Time between changes (seconds or range) | `tornet --interval 30` |
| `--count` | Number of IP changes (0 = infinite) | `tornet --count 20` |
| `--stop` | Stop all Tor services | `tornet --stop` |
| `--version` | Show version | `tornet --version` |

### Advanced Commands
| Command | Description | Example |
|---------|-------------|---------|
| `--status` | Show system status | `tornet --status` |
| `--country` | Specify exit country | `tornet --country jp` |
| `--schedule` | Schedule IP changes | `tornet --schedule 5m` |
| `--dns-leak-test` | Test for DNS leaks | `tornet --dns-leak-test` |
| `--kill-switch` | Toggle kill switch | `tornet --kill-switch` |
| `--log --follow` | View/follow logs | `tornet --log --follow` |
| `--json` | JSON output format | `tornet --ip --json` |
| `--config` | Use custom config | `tornet --config myconfig.yml` |
| `--auto-fix` | Auto-install dependencies | `tornet --auto-fix` |
| `--list-countries` | List country codes | `tornet --list-countries` |
| `--restore-default` | Restore default config | `tornet --restore-default` |

### Schedule Formats
- `30s` - Every 30 seconds
- `5m` - Every 5 minutes
- `2h` - Every 2 hours
- `1d` - Every 1 day

### Interval Formats
- `60` - Exactly 60 seconds
- `30-120` - Random between 30 and 120 seconds

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
# Test your Tor connection for DNS leaks
tornet --dns-leak-test
```

### Log Management
```bash
# View log file
tornet --log

# Follow log file in real-time
tornet --log --follow
```

### JSON Output
```bash
# Get IP in JSON format
tornet --ip --json

# Change IP with JSON output
tornet --change --json
```

### Complete Example
```bash
# Start with US exit nodes, change every 2-5 minutes, run 50 times
tornet --country us --interval 120-300 --count 50

# Schedule hourly IP changes with German exit nodes
tornet --country de --schedule 1h

# Run with custom configuration and JSON output
tornet --config custom.yml --json --interval 30 --count 100
```

## Troubleshooting

### Common Issues

1. **Permission Denied Errors**
```bash
# Run with sudo for system operations
sudo tornet --kill-switch
```

2. **Tor Not Starting**
```bash
# Check if Tor is installed
which tor

# Start Tor service manually
sudo systemctl start tor
# or
sudo service tor start
```

3. **Dependency Issues**
```bash
# Use auto-fix to install dependencies
tornet --auto-fix

# Manual dependency check
python3 -c "import requests"
tor --version
```

4. **Connection Issues**
```bash
# Check internet connection
curl -s https://api.ipify.org

# Check Tor connection
curl --socks5 127.0.0.1:9050 https://api.ipify.org
```

### Log Files
- **TorNet Logs**: `~/.tornet/tornet.log`
- **Tor Configuration**: `~/.tornet/torrc.custom`
- **Country Settings**: `~/.tornet/current_country`

### Status Information
```bash
# Get detailed system status
tornet --status
```

Output includes:
- Tor installation status
- Tor running status
- Current IP address
- IP country location
- Configured country
- Service manager
- Package manager
- Config/log file locations

## Disclaimer

**TorNet is intended for educational and privacy purposes only.**

### Important Notes:
1. **Legal Compliance**: Ensure you comply with all applicable laws and regulations in your jurisdiction
2. **Terms of Service**: Respect websites' terms of service and robots.txt files
3. **Responsible Use**: Do not use for illegal activities, harassment, or unauthorized access
4. **No Warranty**: This software is provided "as is" without any warranty
5. **Privacy**: While Tor provides anonymity, always practice good operational security
6. **Security**: Keep your system updated and use additional security measures as needed

### Ethical Guidelines:
- Use for privacy protection and security testing (with permission)
- Respect network resources and bandwidth
- Do not overload services with excessive requests
- Always obtain proper authorization before testing

### Limitations:
- Tor exit nodes may be blocked by some services
- Connection speed may be slower than direct connections
- Some features require root/sudo privileges
- Not all countries may have reliable Tor exit nodes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Author

- GitHub: [@ByteBreach](https://github.com/ByteBreach)

### *Thanks to all contributors*:

<table>
  <tr align="center">
    <td><a href="https://github.com/mr-fidal"><img src="https://avatars.githubusercontent.com/u/154952367?s=100" /><br /><sub><b>Mr-Fidal</b></sub></a></td>
    <td><a href="https://github.com/GH05T-HUNTER5"><img src="https://avatars.githubusercontent.com/u/108191615?s=100" /><br /><sub><b>GH05T-HUNTER5</b></sub></a></td>
  </tr>
<table>

##  Support

If you find this project useful, please consider:
- Giving it a star 
- Reporting issues 
- Suggesting new features 
- Sharing with others 

---

## Acknowledgements

We would like to thank the developers of the Tor project for their work in creating a robust and secure anonymity network.

## Thanks

Thank you for using TorNet! We hope this tool helps you secure your network and maintain your privacy. If you have any feedback or suggestions, please feel free to reach out to us.

<div align="center">
Made with ❤️ for the privacy-conscious community
</div>



---

By following this guide, you should be able to effectively use TorNet to enhance your online privacy and security. Happy browsing!
