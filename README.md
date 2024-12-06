# 🔍 Sherlock Mail - Advanced Email Intelligence Tool

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/Hamed233/Sherlock-Mail-AI-Powered-Email-Intelligence/graphs/commit-activity)

## 🌟 Overview

Sherlock Mail is an advanced AI-powered email intelligence and OSINT tool that provides comprehensive analysis of email addresses. It helps gather and analyze publicly available information associated with email addresses, making it a valuable tool for security researchers, HR professionals, and digital investigators.

## ✨ Features

### 🎯 Core Capabilities

1. **Personal Information Analysis**
   - Name extraction and pattern analysis
   - Birth year detection from email patterns
   - Language pattern detection
   - Professional background insights

2. **Domain Intelligence**
   - Domain age and reputation analysis
   - Email security assessment (SPF, DMARC)
   - MX records analysis
   - Organization details

3. **Digital Footprint Analysis**
   - Multiple breach database checks
   - Security vulnerability assessment
   - Historical data analysis
   - Risk level evaluation

4. **Social Media Discovery**
   - Profile discovery across 15+ platforms
   - Activity analysis where available
   - Bio and description extraction
   - Connection analysis

5. **Technical Presence**
   - Developer platform detection
   - Package registry searches
   - Code repository analysis
   - Technical community participation

### 🛡️ Privacy & Security

- Uses only publicly available information
- No API keys required
- Respects rate limits and platform policies
- Secure data handling
- No data storage or tracking

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/Hamed233/Sherlock-Mail-AI-Powered-Email-Intelligence.git
cd Sherlock-Mail-AI-Powered-Email-Intelligence
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## 💻 Usage

Basic usage:
```bash
python Sherlock-Mail-AI-Powered-Email-Intelligence.py email@example.com
```

Advanced usage with options:
```bash
python Sherlock-Mail-AI-Powered-Email-Intelligence.py email@example.com --output json --timeout 30 --verbose
```

## 📋 Example Output

Here's an example output for a sample email (john.developer1995@gmail.com):

```
╭──────────────────────────────────────────────────────────────────────────────╮
│                           🔍 Sherlock Mail v1.0.0                            │
│                          Advanced Email Intelligence                         │
╰──────────────────────────────────────────────────────────────────────────────╯

╭──────────────────────────── 👤 Personal Details ─────────────────────────────╮
│ Basic Information                                                            │
│                                                                              │
│ Full Name: John Developer                                                    │
│ Email: john.developer1995@gmail.com                                          │
│ Possible Birth Year: 1995                                                    │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

╭─────────────────────────── 🌐 Social Profiles ──────────────────────────────╮
│ Social Media Profiles                                                       │
│                                                                            │
│ ✓ GitHub                                                                   │
│   URL: https://github.com/johndeveloper                                    │
│   Repositories: 45                                                         │
│   Activity: 1,234 contributions in 2023                                    │
│   Bio: Full-stack developer | Open source enthusiast                       │
│                                                                            │
│ ✓ LinkedIn                                                                 │
│   URL: https://www.linkedin.com/in/john-developer                          │
│   Headline: Senior Software Engineer at Tech Corp                          │
│   Location: San Francisco, CA                                              │
│                                                                            │
│ ✓ Twitter                                                                  │
│   URL: https://twitter.com/johndeveloper                                   │
│   Followers: 2,500                                                         │
│   Bio: Building cool stuff with code 👨‍💻                                    │
╰────────────────────────────────────────────────────────────────────────────╯

╭────────────────────────── 🔒 Domain Security ───────────────────────────────╮
│ Domain Analysis                                                             │
│                                                                            │
│ Domain: gmail.com                                                          │
│ Organization: Google LLC                                                   │
│ Creation Date: 2004-04-01                                                  │
│ Country: United States                                                     │
│                                                                            │
│ Email Security:                                                            │
│   SPF Record: ✓                                                            │
│   DMARC Record: ✓                                                          │
│                                                                            │
│ Mail Providers:                                                            │
│   • aspmx.l.google.com                                                     │
│   • alt1.aspmx.l.google.com                                               │
│   • alt2.aspmx.l.google.com                                               │
╰────────────────────────────────────────────────────────────────────────────╯

╭─────────────────── 🔍 Digital Footprint & Tech Presence ───────────────────╮
│ Security Check URLs:                                                       │
│   • https://haveibeenpwned.com/account/john.developer1995@gmail.com       │
│   • https://ghostproject.fr/search/john.developer1995@gmail.com           │
│   • https://dehashed.com/search?query=john.developer1995@gmail.com        │
│                                                                           │
│ Technical Presence:                                                       │
│   • NPM: 3 packages published                                            │
│   • PyPI: 2 packages published                                           │
│   • Docker Hub: 5 public images                                          │
│   • Stack Overflow: 5,432 reputation                                     │
╰───────────────────────────────────────────────────────────────────────────╯

╭──────────────────────────── Investigation Stats ────────────────────────────╮
│                                                                            │
│                           📊 Total Sources: 18                             │
│                           🔍 Patterns Found: 12                            │
│                        ⚡ Processing Time: 35.35s                          │
│                        🎯 Confidence Score: 85%                            │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯
```

## 🛠️ Advanced Options

- `--output`: Output format (text, json, html)
- `--timeout`: Request timeout in seconds
- `--verbose`: Enable detailed logging
- `--no-color`: Disable colored output
- `--save`: Save results to file

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

- **Name**: Hamed Esam
- **Twitter**: [@hamedesam_dev](https://twitter.com/hamedesam_dev)
- **Website**: [albashmoparmeg.com](https://albashmoparmeg.com)
- **GitHub**: [@Hamed233](https://github.com/Hamed233)

## ⚠️ Disclaimer

This tool is for educational purposes only. Always respect privacy and terms of service when gathering information. The author is not responsible for any misuse of this tool.
