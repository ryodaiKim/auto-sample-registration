# Auto Sample Registration

Local OCR pipeline that reads clinical specimen receipt PDFs (治験受付検体一覧),
extracts structured data via image-based OCR, and writes results to a Google Sheet.

## Prerequisites

- Python 3.10+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) with Japanese language data
- [Poppler](https://poppler.freedesktop.org/) (provides `pdftoppm` for PDF-to-image conversion)

### macOS (Homebrew)

```bash
brew install tesseract tesseract-lang poppler
```

### Ubuntu/Debian

```bash
sudo apt install tesseract-ocr tesseract-ocr-jpn poppler-utils
```

### Windows

#### 1. Install Tesseract

1. Download the installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer — during setup, check **Additional language data** and select **Japanese**
3. Note the install path (default: `C:\Program Files\Tesseract-OCR`)

#### 2. Install Poppler

1. Download from [poppler-windows releases](https://github.com/osber/poppler-windows/releases) (or use `conda install poppler`)
2. Extract to a folder, e.g. `C:\poppler`
3. Note the `bin` directory path (e.g. `C:\poppler\Library\bin`)

#### 3. Set paths in `.env`

```
POPPLER_PATH=C:\poppler\Library\bin
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

> You do **not** need to add these to your system PATH — the pipeline reads them from `.env`.

## Setup

### 1. Clone and install

```bash
git clone https://github.com/ryodaiKim/auto-sample-registration.git
cd auto-sample-registration
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, replace the activate command:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Google Cloud service account

The pipeline writes to a Google Sheet using a service account.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or use an existing one)
3. Enable the **Google Sheets API**
4. Go to **IAM & Admin > Service Accounts**, create a service account
5. Create a JSON key and save it as `credentials.json` in this directory
6. Share your target Google Sheet with the service account email (Editor access)

### 3. Configure

```bash
cp .env.example .env
```

Edit `.env`:

```
PDF_FOLDER=~/Google Drive/My Drive/検体受付_CIDP/01_初回登録
GOOGLE_SHEET_ID=your-sheet-id-here
SERVICE_ACCOUNT_JSON=credentials.json
```

The Sheet ID is the long string in the URL: `https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`

On Windows, use a Windows-style path for `PDF_FOLDER`:

```
PDF_FOLDER=C:\Users\YourName\Google Drive\My Drive\検体受付_CIDP\01_初回登録
```

## Usage

### Manual run

```bash
source .venv/bin/activate
python pipeline.py
```

On Windows:

```powershell
.venv\Scripts\activate
python pipeline.py
```

### Dry run (parse only, no sheet write)

```bash
python pipeline.py --dry-run
```

### Automated weekly run

#### macOS/Linux (cron)

```bash
crontab -e
```

Add this line (runs every Monday at 9:00 AM):

```
0 9 * * 1 cd /path/to/auto-sample-registration && .venv/bin/python pipeline.py >> pipeline.log 2>&1
```

Replace `/path/to/auto-sample-registration` with the actual path.

#### Windows (Task Scheduler)

1. Open **Task Scheduler** (`taskschd.msc`)
2. Click **Create Basic Task**
3. Name: `Auto Sample Registration`, Trigger: **Weekly** (Monday, 9:00 AM)
4. Action: **Start a program**
   - Program/script: `C:\path\to\auto-sample-registration\.venv\Scripts\python.exe`
   - Arguments: `pipeline.py`
   - Start in: `C:\path\to\auto-sample-registration`
5. Finish

> Replace `C:\path\to\auto-sample-registration` with the actual path.

## How it works

1. Scans `PDF_FOLDER` for `*.pdf` files
2. Skips files already listed in `processed_log.json`
3. Converts each PDF page to an image, runs Tesseract OCR (Japanese)
4. Parses the OCR text to extract: trial name, subject ID, gender, collection date, visit point, test items
5. Expands grouped items (e.g., `【血清分離・血漿分離・DNA】` becomes 3 rows)
6. Appends rows to the Google Sheet
7. Records the filename in `processed_log.json` so it won't be reprocessed

### Reprocessing a file

Delete its entry from `processed_log.json` and run the pipeline again.

## Output columns

| Column | Example |
|--------|---------|
| 試験名 | レジストリ研究 |
| 被験者番号 | CIDP-KPU-0010 |
| 性別 | 男 |
| 採取日 | 20250702 |
| ポイント名 | 初回登録時 |
| 検査項目 | 血清分離（用手法） |
