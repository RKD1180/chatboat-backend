# Chatbot Backend

Python FastAPI backend for the Chatbot Platform with Supabase PostgreSQL and Gemini AI.

## Features
- JWT Authentication
- Project Management
- Training Data (Text + PDF)
- Vector Embeddings (TF-IDF)
- Chat with AI (Gemini)
- File Uploads

## Prerequisites
- Python 3.8+
- PostgreSQL database (Supabase)
- Gemini API key

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/chatbot-backend.git
cd chatbot-backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` file:
```env
DATABASE_URL=postgresql://postgres.xxx:password@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres
JWT_SECRET=your-secret-key
GEMINI_API_KEY=your-gemini-api-key
FRONTEND_URLS=http://localhost:3000
```

### 5. Run Server
```bash
python main.py
```

Server starts at http://localhost:8000

### 6. Access API
- API Base: http://localhost:8000/api
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Setup

Tables are created automatically on first run. Or run manually in Supabase SQL Editor:

```sql
-- Copy and paste contents of sql/000_init.sql
```

## Project Structure

```
chatbot-backend/
├── main.py              # FastAPI entry point
├── config/              # Configuration
├── modules/             # Business logic
│   ├── auth/           # Authentication
│   ├── projects/       # Project management
│   ├── training/       # Training data
│   ├── chat/           # Chat & AI
│   ├── prompts/        # Custom prompts
│   ├── files/          # File uploads
│   └── settings/       # User settings
├── sql/                # Database migrations
├── api/                # Vercel serverless
├── requirements.txt    # Dependencies
└── .env.example        # Environment template
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register |
| POST | /api/auth/login | Login |
| POST | /api/projects | Create project |
| GET | /api/projects | List projects |
| POST | /api/training/text | Add training text |
| POST | /api/training/pdf | Upload PDF |
| POST | /api/chat/conversations | Create conversation |
| POST | /api/chat/conversations/:id/messages | Send message |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection | - |
| JWT_SECRET | JWT secret key | raton1234 |
| JWT_ALGORITHM | JWT algorithm | HS256 |
| JWT_EXPIRES_IN | Token expiry (days) | 7 |
| GEMINI_API_KEY | Gemini API key | - |
| FRONTEND_URLS | Allowed CORS origins | http://localhost:3000 |
| PORT | Server port | 8000 |

## Deployment

See [VERCEL_DEPLOYMENT.md](../VERCEL_DEPLOYMENT.md) for Vercel deployment.
