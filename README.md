# 🛡️ ThreatLens

### AI-Powered Website Threat Detection & Intelligence Platform

> **See the threat before you trust the link.**

ThreatLens is a cybersecurity platform that analyzes URLs and websites using **machine learning, URL intelligence, domain analysis, DNS/SSL information, and external threat intelligence** to identify potentially malicious and phishing websites.

Instead of providing only a binary *"Phishing / Legitimate"* result, ThreatLens generates an **explainable risk score** and shows the security factors that contributed to the decision.

---

## ✨ Features

### 🔍 Intelligent URL Scanner

Analyze a URL for suspicious characteristics such as:

* Suspicious URL structure
* Excessive subdomains
* IP-based URLs
* Suspicious keywords
* URL obfuscation
* Special characters
* URL length and entropy
* Shortened URLs

### 🤖 Machine Learning Detection

ThreatLens uses machine learning to classify URLs as:

* 🟢 Safe
* 🟡 Suspicious
* 🔴 Malicious

The ML pipeline extracts URL features and generates a phishing probability score.

### 🌐 Domain Intelligence

Analyze domain-level information including:

* Domain age
* WHOIS information
* DNS records
* Nameservers
* SSL/TLS information
* Redirect behavior

### 🛡️ Threat Intelligence

ThreatLens can integrate external threat-intelligence services to identify known malicious or phishing URLs.

### 📊 Risk Scoring

Multiple security signals are combined into a unified risk score.

Example:

```text
Risk Score: 91 / 100

Classification: HIGH RISK

Contributing factors:
⚠ Recently registered domain
⚠ Suspicious URL structure
⚠ Login-related keywords
⚠ Poor reputation
✓ HTTPS enabled
```

### 🧠 Explainable Detection

ThreatLens doesn't simply say:

```text
PHISHING
```

It explains:

```text
WHY?
```

This makes the system easier for users, analysts, and security teams to understand.

### 📈 Security Dashboard

The dashboard provides:

* Total scans
* Threats detected
* Safe URLs
* Risk statistics
* Recent scans
* Threat trends
* Scan history

---

# 🏗️ System Architecture

```text
                         ┌──────────────────┐
                         │      USER        │
                         │ Web Dashboard    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ React Frontend   │
                         │ ThreatLens UI    │
                         └────────┬─────────┘
                                  │
                              HTTPS / REST
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ FastAPI Backend  │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
       ┌─────────────┐    ┌──────────────┐    ┌──────────────┐
       │ URL Analyzer│    │ Domain Intel │    │ Reputation   │
       └──────┬──────┘    └──────┬───────┘    └──────┬───────┘
              │                  │                   │
              └──────────────────┼───────────────────┘
                                 ▼
                       ┌──────────────────┐
                       │ Feature          │
                       │ Extraction       │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ ML Classifier    │
                       │ Random Forest /  │
                       │ XGBoost          │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Risk Engine      │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Explainable      │
                       │ Security Report  │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ PostgreSQL       │
                       │ Scan History     │
                       └──────────────────┘
```

---

# 🧰 Technology Stack

| Layer               | Technology                  |
| ------------------- | --------------------------- |
| Frontend            | React + Vite                |
| UI                  | Tailwind CSS                |
| Charts              | Recharts                    |
| Backend             | FastAPI                     |
| Language            | Python                      |
| Machine Learning    | Scikit-learn / XGBoost      |
| Database            | PostgreSQL                  |
| DNS Analysis        | dnspython                   |
| Domain Analysis     | WHOIS                       |
| HTTP Client         | httpx                       |
| Threat Intelligence | VirusTotal API              |
| Authentication      | JWT                         |
| Containerization    | Docker                      |
| Development         | GitHub Codespaces + VS Code |

---

# 📁 Project Structure

```text
threatlens/
├── .github/
├── .devcontainer/
├── frontend/
├── backend/
├── ml/
├── docs/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── LICENSE
```

---

# 🚀 Development Roadmap

## Phase 1 — Project Foundation

* [ ] Repository setup
* [ ] Codespaces configuration
* [ ] React frontend
* [ ] FastAPI backend
* [ ] Database configuration
* [ ] API structure

## Phase 2 — URL Analysis

* [ ] URL parser
* [ ] URL feature extraction
* [ ] Suspicious keyword detection
* [ ] IP-based URL detection
* [ ] URL entropy analysis
* [ ] HTTPS analysis

## Phase 3 — Machine Learning

* [ ] Dataset preparation
* [ ] Data preprocessing
* [ ] Feature engineering
* [ ] Model training
* [ ] Model evaluation
* [ ] Model integration

## Phase 4 — Threat Intelligence

* [ ] DNS analysis
* [ ] WHOIS/domain analysis
* [ ] SSL analysis
* [ ] Reputation API
* [ ] Threat intelligence integration

## Phase 5 — Risk Engine

* [ ] ML probability
* [ ] Reputation score
* [ ] Domain risk
* [ ] Security signals
* [ ] Unified risk score
* [ ] Explainable results

## Phase 6 — Web Application

* [ ] Dashboard
* [ ] URL scanner
* [ ] Scan history
* [ ] Analytics
* [ ] Detailed security report
* [ ] Authentication

## Phase 7 — Deployment

* [ ] Docker configuration
* [ ] Backend deployment
* [ ] Frontend deployment
* [ ] Database deployment
* [ ] Security testing
* [ ] Final documentation

---

# 🔐 Security Considerations

ThreatLens is designed primarily for **defensive cybersecurity analysis**.

The scanner should:

* Avoid submitting sensitive URLs to third-party services without user consent.
* Validate and sanitize user input.
* Apply request timeouts.
* Restrict server-side URL fetching.
* Protect API keys using environment variables.
* Never commit secrets to Git.
* Implement rate limiting.
* Avoid executing downloaded website content.
* Log security-relevant events safely.

---

# 🎯 Project Goal

The goal of ThreatLens is to demonstrate how multiple cybersecurity techniques can work together:

```text
URL Analysis
      +
Domain Intelligence
      +
DNS / SSL Analysis
      +
Threat Intelligence
      +
Machine Learning
      +
Risk Scoring
      +
Explainable Security
      =
ThreatLens
```

---

# 👨‍💻 Development

This project is being developed as a cybersecurity internship project with a focus on practical application of:

* Cybersecurity
* Web technologies
* Machine learning
* Threat intelligence
* API development
* Secure software development

---

## ⚠️ Disclaimer

ThreatLens is intended for educational and defensive security purposes. Detection results are probabilistic and should not be treated as definitive proof that a website is malicious or legitimate.
