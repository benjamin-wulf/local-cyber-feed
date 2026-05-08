# local-cyber-feed

## Overview

local-cyber-feed is intended to be a small personal project, ultimately being an RSS Reader and news aggregator. The system operates as a locally hosted server which can be accessed via browser.
**But *why?*** Because I was bored and wanted to work on a dev project, but wanted to create something distinctly functional and useful for my day-to-day operations. Also, some existing alternatives are overcomplicated, bloated, or feel the need to inject AI summaries *everywhere*. I'm not against implementing AI, but let's be real here that's overkill.

## Getting Started

### Prerequisites

This project requires python and has successfully run on 3.13.x and 3.14.x.
Ultimately cross compatible between Windows, Linux, and macOS, as of now testing has only been done on Windows and macOS.

### Installation

1. Clone the repo
`git clone https://github.com/benjamin-wulf/local-cyber-feed.git`
2. Create Python virtual environment (optional but recommended)
`python -m venv venv`
3. Install required packages
`pip install -r requirements.txt`
4. Run the application
`python run.py`
5. Access the application via browser by navigating to `http://127.0.0.1:5000` (or the ip/port used by your local flask app)
