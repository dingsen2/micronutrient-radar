# Micronutrient Radar

A smart nutrition tracking app that converts grocery receipts into micronutrient insights.

## Overview

Micronutrient Radar helps users track their micronutrient intake by analyzing grocery receipts. Instead of manual food logging, it:
- Converts grocery receipts into a weekly micronutrient ledger
- Visualizes gaps in a radar chart
- Suggests three concrete foods to close those gaps

## Tech Stack

- **Frontend**: Next.js 14 (React)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **OCR**: Tesseract.js (client-side) + Cloud OCR fallback
- **Nutrition Data**: USDA FoodData Central API

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- PostgreSQL 14+

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/micronutrient-radar.git
cd micronutrient-radar
```

2. Set up the frontend:
```bash
cd frontend
npm install
npm run dev
```

3. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

4. Set up the database:
```bash
# Create a PostgreSQL database named 'micronutrient_radar'
# Update the .env file with your database credentials
```

5. Set up environment variables:
```bash
# Copy the example env files
cp frontend/.env.example frontend/.env
cp backend/.env.example backend/.env
```

## Project Structure

```
micronutrient-radar/
├── frontend/           # Next.js frontend application
├── backend/           # FastAPI backend service
├── docs/             # Project documentation
└── README.md         # This file
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 