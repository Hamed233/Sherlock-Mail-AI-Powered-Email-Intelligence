#!/usr/bin/env python3
"""
Sherlock Mail - AI-Powered Email Intelligence Tool
===============================================

A sophisticated OSINT tool that uses artificial intelligence to uncover and analyze
information about email addresses. Like its namesake detective, it employs advanced
deduction methods combined with modern AI to reveal insights about email addresses
and their digital footprint.

Author: Your Name
License: MIT
Version: 1.0.0
"""

import sys
import re
import json
import time
import hashlib
import socket
import whois
import dns.resolver
import requests
import asyncio
import nltk
import spacy
import torch
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
import os

class SherlockMail:
    """
    Main class for the Sherlock Mail tool. Handles email analysis using AI and OSINT techniques.
    """
    
    def __init__(self, email):
        """
        Initialize Sherlock Mail with an email address.
        
        Args:
            email (str): The email address to investigate
        """
        self.email = email
        self.username = email.split('@')[0]
        self.domain = email.split('@')[1]
        self.console = Console()
        self.results = defaultdict(dict)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        # Initialize AI models
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.nlp = spacy.load("en_core_web_sm")
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')

    def analyze_name_patterns(self):
        """
        Use NLP to analyze name patterns in the username.
        
        Returns:
            dict: Analysis results including entities, possible names, and language pattern
        """
        doc = self.nlp(self.username.replace('.', ' '))
        
        name_info = {
            "entities": [],
            "possible_names": [],
            "language_pattern": str(doc.lang_),
        }

        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG']:
                name_info["entities"].append({
                    "text": ent.text,
                    "type": ent.label_
                })

        # Advanced pattern analysis
        parts = self.username.split('.')
        for part in parts:
            # Check if part looks like a name
            if part.isalpha() and len(part) > 2:
                name_info["possible_names"].append(part)

        return name_info

    def analyze_content_sentiment(self, text):
        """
        Analyze sentiment of text content using transformer models.
        
        Args:
            text (str): Text content to analyze
            
        Returns:
            dict: Sentiment analysis results
        """
        try:
            result = self.sentiment_analyzer(text)
            return result[0]
        except Exception:
            return {"label": "UNKNOWN", "score": 0.0}

    def extract_keywords(self, text):
        """
        Extract important keywords from text using TF-IDF.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            list: Important keywords found in the text
        """
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text.lower())
        
        # Filter out stop words and short terms
        keywords = [w for w in word_tokens if w not in stop_words and len(w) > 2]
        
        # Use TF-IDF to find important terms
        vectorizer = TfidfVectorizer(max_features=10)
        try:
            tfidf_matrix = vectorizer.fit_transform([' '.join(keywords)])
            feature_names = vectorizer.get_feature_names_out()
            return list(feature_names)
        except:
            return keywords[:10]  # Fallback to simple frequency

    async def analyze_social_presence(self):
        """
        Analyze social media presence with sentiment analysis.
        
        Returns:
            dict: Social media analysis results
        """
        platforms = {
            'Twitter': [
                f"https://twitter.com/{self.username}",
                f"https://twitter.com/search?q={self.email}"
            ],
            'Instagram': [f"https://www.instagram.com/{self.username}"],
            'LinkedIn': [f"https://www.linkedin.com/search/results/all/?keywords={self.email}"],
            'GitHub': [
                f"https://github.com/{self.username}",
                f"https://api.github.com/search/users?q={self.email}"
            ],
            'Medium': [f"https://medium.com/@{self.username}"],
        }

        social_analysis = defaultdict(dict)
        
        for platform, urls in platforms.items():
            platform_data = {
                "urls": [],
                "content_analysis": {},
                "sentiment": {},
                "keywords": []
            }
            
            for url in urls:
                try:
                    response = requests.get(url, headers=self.headers, timeout=5)
                    if response.status_code == 200:
                        platform_data["urls"].append(url)
                        
                        # Extract text content
                        soup = BeautifulSoup(response.text, 'html.parser')
                        text_content = soup.get_text(separator=' ', strip=True)
                        
                        # Analyze content
                        platform_data["sentiment"] = self.analyze_content_sentiment(text_content[:512])
                        platform_data["keywords"] = self.extract_keywords(text_content)
                        
                        # Special handling for GitHub
                        if platform == 'GitHub' and 'api' in url:
                            data = response.json()
                            if data.get('total_count', 0) > 0:
                                for item in data['items']:
                                    platform_data["profile_data"] = {
                                        'username': item['login'],
                                        'profile': item['html_url'],
                                        'type': item['type']
                                    }
                except Exception as e:
                    platform_data["errors"] = str(e)
                    continue
            
            if platform_data["urls"]:
                social_analysis[platform] = platform_data

        return social_analysis

    async def run_social_analysis(self):
        """Run social media analysis asynchronously."""
        return await self.analyze_social_presence()

    def analyze_email_reputation(self):
        """
        Analyze email reputation using various factors.
        
        Returns:
            dict: Reputation analysis results
        """
        reputation_score = 0
        factors = []

        # Domain age factor
        try:
            w = whois.whois(self.domain)
            if w.creation_date:
                creation_date = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
                domain_age = (datetime.now() - creation_date).days
                if domain_age > 365:
                    reputation_score += 20
                    factors.append(f"Domain age: {domain_age} days")
        except Exception:
            pass

        # Email pattern factor
        if re.match(r'^[a-zA-Z]+\.[a-zA-Z]+', self.username):
            reputation_score += 15
            factors.append("Professional email pattern")
        elif re.match(r'^[a-zA-Z]+$', self.username):
            reputation_score += 10
            factors.append("Simple email pattern")

        # Length factor
        if 6 <= len(self.username) <= 24:
            reputation_score += 10
            factors.append("Appropriate length")

        # Character variety
        char_types = sum([
            bool(re.search(r'[a-z]', self.username)),
            bool(re.search(r'[A-Z]', self.username)),
            bool(re.search(r'[0-9]', self.username)),
            bool(re.search(r'[._-]', self.username))
        ])
        reputation_score += char_types * 5
        factors.append(f"Character variety: {char_types} types")

        return {
            "score": min(reputation_score, 100),
            "factors": factors,
            "risk_level": "Low" if reputation_score > 70 else "Medium" if reputation_score > 40 else "High"
        }

    def create_investigation_report(self):
        """
        Create a rich, formatted investigation report.
        
        Returns:
            Layout: Rich layout object containing the formatted report
        """
        layout = Layout()
        layout.split_column(
            Layout(Panel(Text("🔍 Sherlock Mail Investigation", justify="center", style="bold blue")), size=3),
            Layout(name="main")
        )
        layout["main"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )

        # Name Analysis Table
        name_table = Table(title="🧠 AI Name Analysis", show_header=True)
        name_table.add_column("Type", style="cyan")
        name_table.add_column("Analysis", style="green")
        
        name_analysis = self.analyze_name_patterns()
        for key, value in name_analysis.items():
            name_table.add_row(key.replace("_", " ").title(), str(value))

        # Reputation Table
        reputation_table = Table(title="🎯 Email Reputation Analysis", show_header=True)
        reputation_table.add_column("Factor", style="cyan")
        reputation_table.add_column("Value", style="green")
        
        reputation = self.analyze_email_reputation()
        reputation_table.add_row("Overall Score", f"{reputation['score']}/100")
        reputation_table.add_row("Risk Level", reputation['risk_level'])
        for factor in reputation['factors']:
            reputation_table.add_row("Factor", factor)

        # Social Analysis Table
        social_table = Table(title="🌐 AI Social Media Analysis", show_header=True)
        social_table.add_column("Platform", style="cyan")
        social_table.add_column("Analysis", style="green")
        
        social_analysis = asyncio.run(self.run_social_analysis())
        for platform, data in social_analysis.items():
            if data.get("sentiment"):
                sentiment = data["sentiment"]
                social_table.add_row(
                    platform,
                    f"Sentiment: {sentiment['label']} ({sentiment['score']:.2f})\n" +
                    f"Keywords: {', '.join(data.get('keywords', []))[:50]}"
                )

        # Add tables to layout
        layout["left"].update(name_table)
        layout["right"].update(reputation_table)
        layout["main"].update(social_table)

        return layout

    def create_header(self):
        """Create a stylish header for the tool."""
        header = Panel(
            Text.assemble(
                ("🔍 ", "bold yellow"),
                ("Sherlock Mail ", "bold blue"),
                ("v1.0.0\n", "bold cyan"),
                ("Made with ❤️  by ", "white"),
                ("Hamed Esam", "bold green"),
                justify="center"
            ),
            border_style="blue",
            padding=(1, 2)
        )
        return header

    def create_footer(self):
        """Create a footer with contact information."""
        footer = Panel(
            Text.assemble(
                ("Twitter: ", "white"), ("@hamedesam_dev\n", "cyan"),
                ("Website: ", "white"), ("albashmoparmeg.com\n", "cyan"),
                ("GitHub: ", "white"), ("@Hamed233", "cyan"),
                justify="center"
            ),
            border_style="blue",
            padding=(1, 2)
        )
        return footer

    def create_animated_banner(self):
        """Create an animated ASCII art banner."""
        frames = [
            """
[bold blue]
   ____  _               _            _    __  __       _ _ 
  / ___|| |__   ___ _ __| | ___   ___| | _|  \/  | __ _(_) |
  \___ \| '_ \ / _ \ '__| |/ _ \ / __| |/ / |\/| |/ _` | | |
   ___) | | | |  __/ |  | | (_) | (__|   <| |  | | (_| | | |
  |____/|_| |_|\___|_|  |_|\___/ \___|_|\_\_|  |_|\__,_|_|_|
[/bold blue]
            """,
            """
[bold cyan]
   ____  _               _            _    __  __       _ _ 
  / ___|| |__   ___ _ __| | ___   ___| | _|  \/  | __ _(_) |
  \___ \| '_ \ / _ \ '__| |/ _ \ / __| |/ / |\/| |/ _` | | |
   ___) | | | |  __/ |  | | (_) | (__|   <| |  | | (_| | | |
  |____/|_| |_|\___|_|  |_|\___/ \___|_|\_\_|  |_|\__,_|_|_|
[/bold cyan]
            """
        ]
        return frames

    def create_loading_animation(self):
        """Create a loading animation with emojis."""
        return ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def display_animated_banner(self):
        """Display the animated banner."""
        frames = self.create_animated_banner()
        for _ in range(3):  # Animate 3 times
            for frame in frames:
                self.console.clear()
                self.console.print(frame)
                time.sleep(0.5)

    def create_stats_panel(self, stats):
        """Create a panel showing investigation statistics."""
        return Panel(
            Text.assemble(
                ("📊 Total Sources: ", "white"), (f"{stats['sources']}\n", "cyan"),
                ("🔍 Patterns Found: ", "white"), (f"{stats['patterns']}\n", "cyan"),
                ("⚡ Processing Time: ", "white"), (f"{stats['time']:.2f}s\n", "cyan"),
                ("🎯 Confidence Score: ", "white"), (f"{stats['confidence']}%", "cyan"),
                justify="center"
            ),
            title="[bold blue]Investigation Stats",
            border_style="blue",
            padding=(1, 2)
        )

    def create_summary_table(self, results):
        """Create a summary table of findings."""
        table = Table(
            title="[bold blue]🔍 Key Findings Summary",
            show_header=True,
            header_style="bold cyan",
            border_style="blue"
        )
        table.add_column("Category", style="cyan")
        table.add_column("Finding", style="green")
        table.add_column("Confidence", style="yellow")
        
        # Add findings to table
        for category, data in results.items():
            if isinstance(data, dict) and 'summary' in data:
                table.add_row(
                    category.replace('_', ' ').title(),
                    data['summary'],
                    f"{data.get('confidence', '--')}%"
                )
        
        return table

    def run_investigation(self):
        """Run the complete email investigation process."""
        start_time = time.time()
        
        # Display animated banner
        self.display_animated_banner()
        
        # Display header
        self.console.print(self.create_header())
        self.console.print("\n")
        
        # Initialize progress
        status = {"message": "Initializing investigation..."}
        
        with Live(
            Panel(Text(status["message"], justify="center"), title="[bold blue]Status", border_style="blue"),
            refresh_per_second=4
        ) as live:
            tasks = [
                ("🧠 Analyzing name patterns...", self.analyze_name_patterns),
                ("⭐ Calculating reputation score...", self.analyze_email_reputation),
                ("🌐 Investigating social presence...", lambda: asyncio.run(self.run_social_analysis())),
                ("👥 Gathering personal information...", self.analyze_personal_info)
            ]
            
            stats = {"sources": 0, "patterns": 0, "confidence": 0}
            
            for desc, task in tasks:
                # Update progress with animation
                for frame in self.create_loading_animation():
                    status["message"] = f"{frame} {desc}"
                    live.update(
                        Panel(Text(status["message"], justify="center"), 
                              title="[bold blue]Status", 
                              border_style="blue")
                    )
                    time.sleep(0.1)
                
                try:
                    # Execute task
                    result = task()
                    self.results[desc] = result
                    
                    # Update stats
                    stats["sources"] += len(result) if isinstance(result, dict) else 1
                    stats["patterns"] += sum(1 for _ in str(result).split('\n'))
                    stats["confidence"] = min(100, stats["confidence"] + 33)
                except Exception as e:
                    self.console.print(f"[red]Error in {desc}: {str(e)}[/red]")
                    continue
                
                # Show completion
                status["message"] = f"✅ {desc} Complete!"
                live.update(
                    Panel(Text(status["message"], justify="center"), 
                          title="[bold blue]Status", 
                          border_style="blue")
                )
                time.sleep(0.5)
        
        # Calculate total time
        stats["time"] = time.time() - start_time
        
        # Display results with enhanced styling
        self.console.print("\n")
        self.console.print(self.create_stats_panel(stats))
        self.console.print("\n")
        self.console.print(self.create_summary_table(self.results))
        self.console.print("\n")
        self.console.print(self.create_investigation_report())
        self.console.print("\n")
        self.console.print(self.create_personal_info_panel(self.results["👥 Gathering personal information..."]))
        
        # Save results animation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            transient=True,
        ) as progress:
            save_task = progress.add_task("💾 Saving report...", total=100)
            
            # Simulate save progress
            filename = f"report_{self.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            while not progress.finished:
                progress.update(save_task, advance=10)
                time.sleep(0.1)
                
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=4, default=str)
        
        # Final success message
        self.console.print("\n")
        self.console.print(Panel(
            Text.assemble(
                ("✨ Investigation Complete! ✨\n\n", "bold green"),
                ("Report saved to: ", "white"), (filename, "cyan"),
                justify="center"
            ),
            border_style="green",
            padding=(1, 2)
        ))
        
        # Display footer
        self.console.print("\n")
        self.console.print(self.create_footer())

    def analyze_personal_info(self):
        """Analyze and gather personal information associated with the email without using paid APIs."""
        personal_info = {
            "basic_info": {},
            "social_profiles": {},
            "contact_info": {},
            "professional_info": {},
            "digital_footprint": {},
            "domain_analysis": {},
            "tech_presence": {}
        }
        
        # Extract basic information from email pattern
        username_parts = self.username.split('.')
        if len(username_parts) >= 1:
            # Handle various username patterns
            name_parts = []
            for part in username_parts:
                # Extract potential year
                year_match = re.search(r'(19|20)\d{2}', part)
                if year_match:
                    personal_info["basic_info"]["possible_birth_year"] = year_match.group()
                    part = part.replace(year_match.group(), '')
                
                # Clean and add name parts
                cleaned_part = re.sub(r'[0-9_]', '', part)
                if cleaned_part:
                    name_parts.append(cleaned_part.capitalize())
            
            if name_parts:
                personal_info["basic_info"]["possible_name"] = {
                    "first": name_parts[0],
                    "last": name_parts[-1] if len(name_parts) > 1 else None,
                    "full": " ".join(name_parts)
                }
        
        # Enhanced social media profile discovery
        social_platforms = {
            "LinkedIn": [
                f"https://www.linkedin.com/in/{self.username}",
                f"https://www.linkedin.com/in/{'-'.join(username_parts)}",
                f"https://www.linkedin.com/in/{username_parts[0]}-{username_parts[-1]}" if len(username_parts) > 1 else None
            ],
            "Twitter": [
                f"https://twitter.com/{self.username}",
                f"https://twitter.com/{username_parts[0]}_{username_parts[-1]}" if len(username_parts) > 1 else None
            ],
            "GitHub": [
                f"https://github.com/{self.username}",
                f"https://github.com/{username_parts[0]}{username_parts[-1]}" if len(username_parts) > 1 else None
            ],
            "Instagram": [
                f"https://www.instagram.com/{self.username}",
                f"https://www.instagram.com/{username_parts[0]}_{username_parts[-1]}" if len(username_parts) > 1 else None
            ],
            "Medium": [
                f"https://medium.com/@{self.username}",
                f"https://medium.com/@{username_parts[0]}.{username_parts[-1]}" if len(username_parts) > 1 else None
            ],
            "Dev.to": [
                f"https://dev.to/{self.username}",
                f"https://dev.to/{username_parts[0]}{username_parts[-1]}" if len(username_parts) > 1 else None
            ],
            "Stack Overflow": [
                f"https://stackoverflow.com/users/{self.username}",
                f"https://stackoverflow.com/users/{'-'.join(username_parts)}" if len(username_parts) > 1 else None
            ],
            "Behance": [
                f"https://www.behance.net/{self.username}",
                f"https://www.behance.net/{username_parts[0]}{username_parts[-1]}" if len(username_parts) > 1 else None
            ],
            "Dribbble": [
                f"https://dribbble.com/{self.username}",
                f"https://dribbble.com/{username_parts[0]}{username_parts[-1]}" if len(username_parts) > 1 else None
            ],
            "Facebook": [
                f"https://www.facebook.com/{self.username}",
                f"https://www.facebook.com/{'.'.join(username_parts)}" if len(username_parts) > 1 else None
            ],
            "YouTube": [
                f"https://www.youtube.com/@{self.username}",
                f"https://www.youtube.com/@{username_parts[0]}{username_parts[-1]}" if len(username_parts) > 1 else None
            ],
            "Reddit": [
                f"https://www.reddit.com/user/{self.username}",
                f"https://www.reddit.com/user/{username_parts[0]}_{username_parts[-1]}" if len(username_parts) > 1 else None
            ],
            "Kaggle": [
                f"https://www.kaggle.com/{self.username}",
                f"https://www.kaggle.com/{username_parts[0]}{username_parts[-1]}" if len(username_parts) > 1 else None
            ],
            "PyPI": [
                f"https://pypi.org/user/{self.username}",
                f"https://pypi.org/user/{username_parts[0]}{username_parts[-1]}" if len(username_parts) > 1 else None
            ]
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for platform, urls in social_platforms.items():
            for url in urls:
                if url is None:
                    continue
                try:
                    response = requests.get(url, headers=headers, timeout=5)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        title = soup.title.string if soup.title else ""
                        
                        # Check if it's a valid profile page
                        if not any(term in title.lower() for term in ['not found', 'error', '404', 'page doesn\'t exist']):
                            personal_info["social_profiles"][platform] = {
                                "url": url,
                                "status": "Found",
                                "username": self.username,
                                "title": title
                            }
                            
                            # Platform-specific data extraction
                            if platform == "GitHub":
                                try:
                                    # Extract public repositories count
                                    repos_element = soup.find('span', {'class': 'Counter'})
                                    if repos_element:
                                        personal_info["social_profiles"][platform]["repos"] = repos_element.text.strip()
                                    
                                    # Extract contribution information
                                    contrib_element = soup.find('h2', {'class': 'f4 text-normal mb-2'})
                                    if contrib_element:
                                        personal_info["social_profiles"][platform]["contributions"] = contrib_element.text.strip()
                                    
                                    # Extract bio
                                    bio_element = soup.find('div', {'class': 'p-note user-profile-bio'})
                                    if bio_element:
                                        personal_info["social_profiles"][platform]["bio"] = bio_element.text.strip()
                                except Exception:
                                    pass
                            
                            elif platform == "LinkedIn":
                                try:
                                    # Extract headline and location
                                    headline = soup.find('div', {'class': 'text-body-medium'})
                                    location = soup.find('span', {'class': 'text-body-small inline t-black--light break-words'})
                                    if headline:
                                        personal_info["social_profiles"][platform]["headline"] = headline.text.strip()
                                    if location:
                                        personal_info["social_profiles"][platform]["location"] = location.text.strip()
                                except Exception:
                                    pass
                            
                            elif platform == "Twitter":
                                try:
                                    # Extract follower count and bio
                                    followers = soup.find('span', {'class': 'followers-count'})
                                    bio = soup.find('div', {'class': 'bio'})
                                    if followers:
                                        personal_info["social_profiles"][platform]["followers"] = followers.text.strip()
                                    if bio:
                                        personal_info["social_profiles"][platform]["bio"] = bio.text.strip()
                                except Exception:
                                    pass
                            
                            break  # Found a valid profile, no need to check other URLs
                except Exception:
                    continue
        
        # Enhanced domain analysis
        domain = self.email.split('@')[1]
        try:
            domain_info = whois.whois(domain)
            
            # DNS records analysis
            dns_info = {}
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                dns_info["mx_records"] = [str(x.exchange) for x in mx_records]
            except Exception:
                dns_info["mx_records"] = []
            
            try:
                txt_records = dns.resolver.resolve(domain, 'TXT')
                dns_info["txt_records"] = [str(x) for x in txt_records]
                
                # Check for SPF and DMARC
                dns_info["spf_record"] = next((r for r in dns_info["txt_records"] if "v=spf1" in r), None)
                try:
                    dmarc_records = dns.resolver.resolve(f"_dmarc.{domain}", 'TXT')
                    dns_info["dmarc_record"] = next((str(r) for r in dmarc_records if "v=DMARC1" in str(r)), None)
                except Exception:
                    dns_info["dmarc_record"] = None
            except Exception:
                dns_info["txt_records"] = []
            
            personal_info["domain_analysis"] = {
                "name": domain,
                "creation_date": str(domain_info.creation_date[0] if isinstance(domain_info.creation_date, list) 
                               else domain_info.creation_date),
                "organization": domain_info.org if hasattr(domain_info, 'org') else None,
                "country": domain_info.country if hasattr(domain_info, 'country') else None,
                "dns_info": dns_info,
                "email_security": {
                    "has_spf": bool(dns_info.get("spf_record")),
                    "has_dmarc": bool(dns_info.get("dmarc_record")),
                    "mx_providers": dns_info.get("mx_records", [])
                }
            }
        except Exception:
            personal_info["domain_analysis"] = {
                "name": domain,
                "error": "Could not fetch domain information"
            }
        
        # Enhanced digital footprint analysis
        try:
            # Common data breach and security check URLs
            breach_urls = [
                f"https://haveibeenpwned.com/account/{self.email}",
                f"https://ghostproject.fr/search/{self.email}",
                f"https://dehashed.com/search?query={self.email}",
                f"https://intelx.io/?s={self.email}",
                f"https://leakcheck.io/search?query={self.email}"
            ]
            
            # Additional tech presence checks
            tech_urls = [
                f"https://npm.io/~{self.username}",  # NPM packages
                f"https://rubygems.org/profiles/{self.username}",  # Ruby Gems
                f"https://hub.docker.com/u/{self.username}",  # Docker Hub
                f"https://wordpress.org/support/users/{self.username}",  # WordPress
                f"https://gitlab.com/{self.username}"  # GitLab
            ]
            
            personal_info["digital_footprint"]["breach_check"] = {
                "message": "⚠️ For security reasons, please check these URLs manually:",
                "urls": breach_urls
            }
            
            personal_info["tech_presence"] = {
                "message": "🔍 Check technical presence:",
                "urls": tech_urls
            }
            
        except Exception:
            pass

        return personal_info

    def create_personal_info_panel(self, info):
        """Create a rich panel displaying personal information."""
        layout = Layout()
        
        # Create basic info panel
        basic_info = info.get("basic_info", {})
        possible_name = basic_info.get("possible_name", {})
        name_str = f"{possible_name.get('full', 'N/A')}"
        birth_year = basic_info.get("possible_birth_year", "N/A")
        
        basic_panel = Panel(
            Text.assemble(
                ("Basic Information\n\n", "bold blue"),
                (f"Full Name: {name_str}\n", "white"),
                (f"Email: {self.email}\n", "white"),
                (f"Possible Birth Year: {birth_year}\n", "white"),
                justify="left"
            ),
            title="👤 Personal Details",
            border_style="blue"
        )
        
        # Create social profiles panel with enhanced information
        social_text = []
        for platform, data in info.get("social_profiles", {}).items():
            if data.get("status") == "Found":
                social_text.append(f"[green]✓ {platform}[/green]")
                social_text.append(f"  URL: {data.get('url', 'N/A')}")
                
                if platform == "GitHub":
                    if data.get("repos"):
                        social_text.append(f"  Repositories: {data.get('repos')}")
                    if data.get("contributions"):
                        social_text.append(f"  Activity: {data.get('contributions')}")
                    if data.get("bio"):
                        social_text.append(f"  Bio: {data.get('bio')}")
                
                elif platform == "LinkedIn":
                    if data.get("headline"):
                        social_text.append(f"  Headline: {data.get('headline')}")
                    if data.get("location"):
                        social_text.append(f"  Location: {data.get('location')}")
                
                elif platform == "Twitter":
                    if data.get("followers"):
                        social_text.append(f"  Followers: {data.get('followers')}")
                    if data.get("bio"):
                        social_text.append(f"  Bio: {data.get('bio')}")
                
                social_text.append("")  # Add spacing between platforms
        
        social_panel = Panel(
            Text.assemble(
                ("Social Media Profiles\n\n", "bold blue"),
                ("\n".join(social_text) if social_text else "No profiles found", ""),
                justify="left"
            ),
            title="🌐 Social Media",
            border_style="blue"
        )
        
        # Create domain analysis panel
        domain_info = info.get("domain_analysis", {})
        dns_info = domain_info.get("dns_info", {})
        email_security = domain_info.get("email_security", {})
        
        domain_text = [
            f"Domain: {domain_info.get('name', 'N/A')}",
            f"Organization: {domain_info.get('organization', 'N/A')}",
            f"Creation Date: {domain_info.get('creation_date', 'N/A')}",
            f"Country: {domain_info.get('country', 'N/A')}",
            "",
            "Email Security:",
            f"  SPF Record: {'✓' if email_security.get('has_spf') else '✗'}",
            f"  DMARC Record: {'✓' if email_security.get('has_dmarc') else '✗'}",
            "",
            "Mail Providers:",
        ]
        
        for provider in email_security.get("mx_providers", []):
            domain_text.append(f"  • {provider}")
        
        domain_panel = Panel(
            Text.assemble(
                ("Domain Analysis\n\n", "bold blue"),
                ("\n".join(domain_text), "white"),
                justify="left"
            ),
            title="🔒 Domain Security",
            border_style="blue"
        )
        
        # Create digital footprint panel with tech presence
        footprint = info.get("digital_footprint", {})
        tech_presence = info.get("tech_presence", {})
        
        breach_check = footprint.get("breach_check", {})
        
        footprint_text = [
            breach_check.get("message", ""),
            "",
            "Security Check URLs:"
        ]
        
        for url in breach_check.get("urls", []):
            footprint_text.append(f"  • {url}")
        
        footprint_text.extend([
            "",
            tech_presence.get("message", ""),
            ""
        ])
        
        for url in tech_presence.get("urls", []):
            footprint_text.append(f"  • {url}")
        
        footprint_panel = Panel(
            Text.assemble(
                ("Digital Footprint & Tech Presence\n\n", "bold red"),
                ("\n".join(footprint_text), "yellow"),
                justify="left"
            ),
            title="🔍 Digital Footprint",
            border_style="red"
        )
        
        # Combine all panels
        layout.split_column(
            Layout(basic_panel),
            Layout().split_row(
                Layout(social_panel),
                Layout(domain_panel)
            ),
            Layout(footprint_panel)
        )
        
        return layout

    def analyze_professional_score(self):
        """Analyze professional characteristics of the email."""
        score = 0
        factors = []
        
        # Check for full name pattern
        if '.' in self.username:
            parts = self.username.split('.')
            if len(parts) == 2 and all(len(p) > 2 for p in parts):
                score += 25
                factors.append("Full name format (firstname.lastname)")
        
        # Check for common professional domains
        professional_domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'icloud.com']
        if self.domain in professional_domains:
            score += 15
            factors.append(f"Professional domain ({self.domain})")
        
        # Check for length appropriateness
        if 6 <= len(self.username) <= 30:
            score += 10
            factors.append("Appropriate length")
        
        # Check for clean formatting
        if re.match(r'^[a-zA-Z0-9._-]+$', self.username):
            score += 15
            factors.append("Clean character usage")
        
        # Check for no numbers in username
        if not any(c.isdigit() for c in self.username):
            score += 15
            factors.append("No numeric characters")
        
        return {
            "score": score,
            "factors": factors,
            "level": "High" if score >= 70 else "Medium" if score >= 40 else "Low"
        }

    def analyze_security_risks(self):
        """Analyze potential security risks associated with the email."""
        risks = []
        risk_level = "Low"
        
        # Check for common security patterns
        if len(self.username) < 6:
            risks.append("Short username (easier to guess)")
            risk_level = "Medium"
        
        if any(c.isdigit() for c in self.username):
            risks.append("Contains numbers (potential birth year/date)")
        
        if '.' in self.username:
            risks.append("Contains full name (potential privacy concern)")
            risk_level = "Medium"
        
        # Check domain age and reputation
        try:
            w = whois.whois(self.domain)
            if w.creation_date:
                creation_date = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
                domain_age = (datetime.now() - creation_date).days
                if domain_age < 365:
                    risks.append("Domain less than 1 year old")
                    risk_level = "High"
        except Exception:
            risks.append("Unable to verify domain age")
            risk_level = "Medium"
        
        return {
            "risks": risks,
            "level": risk_level,
            "recommendations": [
                "Use 2FA where available",
                "Avoid using personal information in email",
                "Consider using an email alias for public services"
            ] if risks else ["Good security practices detected"]
        }

    def analyze_social_footprint(self):
        """Analyze the social media footprint of the email."""
        footprint = {
            "platforms": {},
            "visibility_score": 0,
            "risk_level": "Low",
            "recommendations": []
        }
        
        platforms = {
            "GitHub": f"https://api.github.com/search/users?q={self.email}",
            "LinkedIn": f"https://www.linkedin.com/pub/dir/?email={self.email}",
            "Twitter": f"https://twitter.com/{self.username}",
            "Instagram": f"https://www.instagram.com/{self.username}",
            "Facebook": f"https://www.facebook.com/{self.username}",
            "Medium": f"https://medium.com/@{self.username}",
            "Dev.to": f"https://dev.to/{self.username}",
            "Stack Overflow": f"https://stackoverflow.com/users/{self.username}"
        }
        
        for platform, url in platforms.items():
            try:
                response = requests.get(url, headers=self.headers, timeout=5)
                if response.status_code == 200:
                    footprint["platforms"][platform] = {
                        "found": True,
                        "url": url,
                        "status": "Active"
                    }
                    footprint["visibility_score"] += 12.5  # Each platform adds to visibility
            except Exception:
                footprint["platforms"][platform] = {
                    "found": False,
                    "status": "Not found or private"
                }
        
        # Calculate risk level based on visibility
        if footprint["visibility_score"] >= 75:
            footprint["risk_level"] = "High"
            footprint["recommendations"].append("Consider reducing public social media presence")
        elif footprint["visibility_score"] >= 50:
            footprint["risk_level"] = "Medium"
            footprint["recommendations"].append("Review privacy settings on social media")
        else:
            footprint["recommendations"].append("Good privacy practices detected")
        
        return footprint

    def create_detailed_report(self):
        """Create a detailed analysis report."""
        report = {
            "email_analysis": {
                "email": self.email,
                "username": self.username,
                "domain": self.domain,
                "timestamp": datetime.now().isoformat(),
                "professional_score": self.analyze_professional_score(),
                "security_analysis": self.analyze_security_risks(),
                "social_footprint": self.analyze_social_footprint(),
                "name_analysis": self.analyze_name_patterns(),
                "reputation": self.analyze_email_reputation()
            },
            "metadata": {
                "tool_version": "1.0.0",
                "analysis_duration": None,
                "confidence_score": None
            }
        }
        
        return report

    def create_visualization_panel(self, report):
        """Create a rich visualization panel for the report."""
        layout = Layout()
        
        # Create header
        header = Panel(
            Text.assemble(
                ("🔍 Detailed Email Intelligence Report\n", "bold blue"),
                (f"Email: {self.email}\n", "cyan"),
                (f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "white"),
                justify="center"
            ),
            border_style="blue"
        )
        
        # Create professional score panel
        prof_score = report["email_analysis"]["professional_score"]
        prof_panel = Panel(
            Text.assemble(
                ("Professional Score\n\n", "bold blue"),
                (f"Score: {prof_score['score']}/100\n", "cyan"),
                (f"Level: {prof_score['level']}\n\n", "green" if prof_score['level'] == "High" else "yellow"),
                ("Factors:\n", "white"),
                ("\n".join(f"✓ {factor}" for factor in prof_score['factors']), "green"),
                justify="left"
            ),
            title="👔 Professional Analysis",
            border_style="blue"
        )
        
        # Create security panel
        security = report["email_analysis"]["security_analysis"]
        security_panel = Panel(
            Text.assemble(
                ("Security Analysis\n\n", "bold red"),
                (f"Risk Level: {security['level']}\n\n", "red" if security['level'] == "High" else "yellow"),
                ("Risks:\n", "white"),
                ("\n".join(f"⚠️ {risk}" for risk in security['risks']), "yellow"),
                ("\n\nRecommendations:\n", "white"),
                ("\n".join(f"→ {rec}" for rec in security['recommendations']), "green"),
                justify="left"
            ),
            title="🛡️ Security Assessment",
            border_style="red"
        )
        
        # Create social footprint panel
        social = report["email_analysis"]["social_footprint"]
        social_text = []
        for platform, data in social["platforms"].items():
            if data["found"]:
                social_text.append(f"[green]✓ {platform}: Active[/green]")
            else:
                social_text.append(f"[grey]✗ {platform}: Not Found[/grey]")
        
        social_panel = Panel(
            Text.assemble(
                ("Social Media Presence\n\n", "bold blue"),
                (f"Visibility Score: {social['visibility_score']:.1f}%\n", "cyan"),
                (f"Risk Level: {social['risk_level']}\n\n", "yellow"),
                ("Platforms:\n", "white"),
                ("\n".join(social_text), ""),
                justify="left"
            ),
            title="🌐 Social Footprint",
            border_style="blue"
        )
        
        # Combine all panels
        layout.split_column(
            Layout(header),
            Layout().split_row(
                Layout(prof_panel),
                Layout(security_panel)
            ),
            Layout(social_panel)
        )
        
        return layout

def main():
    """
    Main entry point for Sherlock Mail.
    """
    if len(sys.argv) != 2:
        Console().print("[red]Usage: python sherlock_mail.py <email>")
        sys.exit(1)

    email = sys.argv[1]
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        Console().print("[red]Invalid email format!")
        sys.exit(1)

    investigator = SherlockMail(email)
    investigator.run_investigation()

if __name__ == "__main__":
    main()
