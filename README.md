# Google Custom Search API

## Security Note

- Never commit secrets (API keys, service account JSON, or `.env` files) into the repository.
- Keep credentials in local `.env` files or a secure secrets manager.

## Setup

### Backend

1. Navigate to backend folder:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Get your credentials and add to `.env`:
   - API Key: https://console.cloud.google.com/apis/credentials
   - Search Engine ID: https://programmablesearchengine.google.com/

5. Run the API:
```bash
python app.py
```

### Frontend

1. Navigate to frontend folder:
```bash
cd frontend
```

2. Install dependencies:
```bash
bun install
```

3. Run the dev server:
```bash
bun run dev
```

The frontend will be available at http://localhost:5173

## Usage

1. Start the backend API (port 5000)
2. Start the frontend dev server (port 5173)
3. Enter a domain in the search box
4. View results with title, link, and snippet

Rate limit: 10 requests per minute, 100 per day
