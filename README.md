# SETBP1 Literature Search & Report Generator

Automated tool to search PubMed, bioRxiv, and medRxiv for SETBP1 and Schinzel-Giedion Syndrome papers and generate comprehensive Excel and PDF reports.

## 📋 Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Automated Weekly Searches](#automated-weekly-searches)
- [Output Files](#output-files)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- **Multi-Database Search**: Queries PubMed, bioRxiv, and medRxiv
- **Comprehensive Reports**: Generates both Excel and PDF outputs
- **Automatic Categorization**: Papers organized by research area
- **Smart Summaries**: Creates concise summaries and key findings
- **Date-Based Naming**: Files named with end date (YYYYMMDD-PKD-Literature-*.*)
- **Robust Error Handling**: Retry logic and graceful failure recovery

## 📦 Requirements

### Python Version
- Python 3.7 or higher

### Required Python Packages
```bash
pip install requests openpyxl reportlab
```

Individual package descriptions:
- `requests` - For API calls to PubMed and preprint servers
- `openpyxl` - For Excel file generation
- `reportlab` - For PDF report generation

## 🔧 Installation

### Option 1: Quick Setup
```bash
# Download the script
wget https://[your-url]/setbp1_literature_search.py

# Install dependencies
pip install requests openpyxl reportlab

# Make executable
chmod +x pkd_literature_search.py
```

### Option 2: Using Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv setbp1-env

# Activate virtual environment
source setbp1-env/bin/activate  # On Linux/Mac
# OR
setbp1-env\Scripts\activate  # On Windows

# Install dependencies
pip install requests openpyxl reportlab

# Download script
wget https://[your-url]/setbp1_literature_search.py
```

## 🚀 Usage

### Basic Usage

#### Search Last 7 Days (Default)
```bash
python setbp1_literature_search.py
```

#### Search Specific Date Range
```bash
python setbp1_literature_search.py --start 2026-02-01 --end 2026-02-08
```

#### Custom Output Directory
```bash
python setbp1_literature_search.py --start 2026-02-01 --end 2026-02-08 --output /path/to/output
```

### Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--start` | Start date (YYYY-MM-DD) | `--start 2026-02-01` |
| `--end` | End date (YYYY-MM-DD) | `--end 2026-02-08` |
| `--output` | Output directory | `--output /tmp/reports` |

### Examples

#### Weekly Search (Last 7 Days)
```bash
# Run every Monday for previous week
python setbp1_literature_search.py
```

#### Monthly Search
```bash
# First day of month for previous month
python setbp1_literature_search.py --start 2026-01-01 --end 2026-01-31
```

#### Custom Date Range
```bash
# Conference preparation - last 6 months
python setbp1_literature_search.py --start 2025-08-01 --end 2026-02-08
```

## ⏰ Automated Weekly Searches

### Option 1: Cron (Linux/Mac)

#### Setup Weekly Search (Every Monday at 8 AM)
```bash
# Open crontab editor
crontab -e

# Add this line (adjust paths as needed):
0 8 * * 1 cd /path/to/script && /usr/bin/python3 setbp1_literature_search.py >> /path/to/logs/setbp1_search.log 2>&1
```

#### Cron Schedule Examples
```bash
# Every Monday at 8 AM
0 8 * * 1 python3 /path/to/setbp1_literature_search.py

# First day of every month at 9 AM
0 9 1 * * python3 /path/to/setbp1_literature_search.py

# Every Friday at 5 PM
0 17 * * 5 python3 /path/to/setbp1_literature_search.py
```

#### Complete Cron Setup Script
```bash
#!/bin/bash
# save as: setup_weekly_setbp1_search.sh

# Variables
SCRIPT_DIR="/path/to/your/script"
PYTHON_PATH="/usr/bin/python3"
LOG_DIR="$SCRIPT_DIR/logs"

# Create log directory
mkdir -p "$LOG_DIR"

# Add to crontab
(crontab -l 2>/dev/null; echo "0 8 * * 1 cd $SCRIPT_DIR && $PYTHON_PATH setbp1_literature_search.py >> $LOG_DIR/setbp1_search.log 2>&1") | crontab -

echo "Weekly search scheduled for Mondays at 8 AM"
echo "Logs will be saved to: $LOG_DIR/setbp1_search.log"
```

### Option 2: Windows Task Scheduler

#### Setup Using GUI:
1. Open **Task Scheduler**
2. Click **Create Basic Task**
3. Name: "SETBP1 Weekly Literature Search"
4. Trigger: **Weekly** → Select day (e.g., Monday)
5. Action: **Start a Program**
   - Program: `C:\Python39\python.exe`
   - Arguments: `C:\path\to\setbp1_literature_search.py`
   - Start in: `C:\path\to\script\directory`
6. Click **Finish**

#### Setup Using Command Line:
```powershell
# Create weekly task (Mondays at 8 AM)
schtasks /create /tn "SETBP1 Literature Search" /tr "C:\Python39\python.exe C:\path\to\pkd_literature_search.py" /sc weekly /d MON /st 08:00
```

### Option 3: Python Scheduler (Cross-Platform)

Create a wrapper script `run_weekly.py`:
```python
import schedule
import time
import subprocess
import logging

# Setup logging
logging.basicConfig(
    filename='pkd_scheduler.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def run_search():
    """Run the SETBP1 literature search"""
    logging.info("Starting SETBP1 literature search...")
    try:
        result = subprocess.run(
            ['python', 'setbp1_literature_search.py'],
            capture_output=True,
            text=True
        )
        logging.info(f"Search completed with exit code: {result.returncode}")
        logging.info(f"Output: {result.stdout}")
        if result.stderr:
            logging.error(f"Errors: {result.stderr}")
    except Exception as e:
        logging.error(f"Failed to run search: {e}")

# Schedule the search
schedule.every().monday.at("08:00").do(run_search)

# Keep the scheduler running
logging.info("Scheduler started. Waiting for scheduled times...")
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

Install schedule package:
```bash
pip install schedule
```

Run the scheduler:
```bash
# Keep running in background
nohup python run_weekly.py &
```

### Option 4: Docker Container (Recommended for Production)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install requests openpyxl reportlab schedule

# Copy script
COPY setbp1_literature_search.py .
COPY run_weekly.py .

# Run scheduler
CMD ["python", "run_weekly.py"]
```

Build and run:
```bash
docker build -t setbp1-search .
docker run -d -v /path/to/output:/mnt/user-data/outputs setbp1-search
```

## 📤 Output Files

### File Naming Convention
Files are named with the END DATE of the search range in YYYYMMDD format:

```
20260208-SETBP1-Literature-Data.xlsx      # Excel spreadsheet
20260208-SETBP1-Literature-Summary.pdf    # PDF report
```

### Excel File Structure

| Column | Content | Width | Description |
|--------|---------|-------|-------------|
| A | *Blank* | 5 | Reserved |
| B | *Blank* | 5 | Reserved |
| C | *Blank* | 5 | Reserved |
| D | **Summary** | 35 | Less than 8 words |
| E | **Last Author** | 15 | Last author's last name |
| F | **Journal** | 25 | Journal name |
| G | **Key Findings** | 60 | 20 words or less |
| H | *Blank* | 5 | Reserved |
| I | *Blank* | 5 | Reserved |
| J | **Link** | 45 | Clickable DOI or PubMed URL |

### PDF Report Contents

1. **Search Summary**
   - Total papers found
   - Date range
   - Database breakdown (PubMed, bioRxiv, medRxiv)

2. **Notable Findings** (Organized by category)
   - Mechanism
   - Therapeutics
   - Models
   - New Data Sets

3. **Complete Paper List**
   - Full author lists
   - Complete citations
   - Clickable links

## 🐛 Troubleshooting

### Common Issues

#### No Papers Found
```bash
# Check date range is correct
python setbp1_literature_search.py --start 2026-02-01 --end 2026-02-08

# Verify network connectivity
ping eutils.ncbi.nlm.nih.gov
```

#### API Rate Limiting
The script includes automatic rate limiting (0.5 seconds between batches). If you still encounter issues:
- Reduce batch size: Edit script and change `batch_size=100` to `batch_size=50`
- Increase delay: Change `time.sleep(0.5)` to `time.sleep(1.0)`

#### Missing Dependencies
```bash
# Reinstall all dependencies
pip install --upgrade requests openpyxl reportlab

# Or use requirements file
pip install -r requirements.txt
```

#### Permission Denied
```bash
# Make script executable
chmod +x pkd_literature_search.py

# Or run with python explicitly
python3 pkd_literature_search.py
```

#### Output Directory Not Found
```bash
# Create output directory
mkdir -p /mnt/user-data/outputs

# Or specify existing directory
python setbp1_literature_search.py --output ~/Documents/PKD_Reports
```

### Debug Mode

To see detailed output:
```bash
# Run with verbose logging
python setbp1_literature_search.py --start 2026-02-01 --end 2026-02-08 2>&1 | tee debug.log
```

### Contact & Support

For issues, questions, or feature requests:
1. Check the troubleshooting section above
2. Review the script comments for implementation details
3. Check PubMed E-utilities documentation: https://www.ncbi.nlm.nih.gov/books/NBK25501/

## 📝 Notes

### Rate Limits
- PubMed: 3 requests/second without API key, 10/second with key
- Script includes automatic rate limiting (0.5s delay between batches)
- Consider registering for NCBI API key for higher limits

### Data Freshness
- PubMed: Updated daily
- bioRxiv/medRxiv: Updated continuously
- Recommend weekly searches to capture all new papers

### Customization
To customize the search query, edit line 43 in `setbp1_literature_search.py`:
```python
query = '("SETBP1" OR "Schinzel-Giedion Syndrome" OR "Schinzel Giedion" OR "SET binding protein 1")'
```

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🔄 Version History

- v1.0.0 (2026-02-11): Initial release with PubMed, bioRxiv, medRxiv support for SETBP1 and Schinzel-Giedion Syndrome
