# Chatbot Backend Architecture

## Overview
Python FastAPI backend with Supabase PostgreSQL and Gemini AI integration.

## Tech Stack
- **Framework**: FastAPI (Python)
- **Database**: Supabase PostgreSQL with pgvector
- **AI**: Gemini API (gemini-flash-latest)
- **Auth**: JWT tokens with bcrypt
- **Vector Search**: TF-IDF embeddings with pgvector

## Project Structure

```
chatbot-backend/
├── main.py                    # FastAPI entry point
├── config/
│   ├── __init__.py
│   ├── settings.py            # Environment variables
│   ├── database.py            # PostgreSQL connection & migrations
│   └── response.py            # Standardized API responses
├── middleware/
│   └── auth.py                # JWT authentication
├── routes/
│   └── __init__.py            # Root router (includes all modules)
├── modules/
│   ├── auth/
│   │   ├── model.py           # User dataclass
│   │   ├── schema.py          # Pydantic request/response
│   │   ├── service.py         # Business logic
│   │   └── route.py           # API endpoints
│   ├── projects/
│   │   ├── model.py
│   │   ├── schema.py
│   │   ├── service.py
│   │   └── route.py
│   ├── training/
│   │   ├── model.py
│   │   ├── schema.py
│   │   ├── service.py
│   │   ├── route.py
│   │   └── embedding.py       # TF-IDF vector embeddings
│   ├── chat/
│   │   ├── model.py
│   │   ├── schema.py
│   │   ├── service.py
│   │   ├── route.py
│   │   └── gemini.py          # Gemini AI integration
│   ├── prompts/
│   │   ├── model.py
│   │   ├── schema.py
│   │   ├── service.py
│   │   └── route.py
│   ├── files/
│   │   ├── model.py
│   │   ├── schema.py
│   │   ├── service.py
│   │   └── route.py
│   └── settings/
│       ├── model.py
│       ├── schema.py
│       ├── service.py
│       └── route.py
├── sql/
│   └── 000_init.sql           # Database schema
├── uploads/                   # Uploaded files
├── requirements.txt
└── .env                       # Environment variables
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Auth       │  │   Projects   │  │   Training   │      │
│  │   Module     │  │   Module     │  │   Module     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           │                                 │
│  ┌──────────────┐  ┌──────┴───────┐  ┌──────────────┐      │
│  │   Chat       │  │   Prompts    │  │   Files      │      │
│  │   Module     │  │   Module     │  │   Module     │      │
│  └──────┬───────┘  └──────────────┘  └──────────────┘      │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    Gemini AI                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                    Database Layer                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Supabase PostgreSQL                       │  │
│  │  - users, projects, training_data, conversations      │  │
│  │  - messages, prompts, files, settings                 │  │
│  │  - pgvector for semantic search                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register new user |
| POST | /api/auth/login | Login user |
| POST | /api/auth/refresh | Refresh JWT token |
| GET | /api/auth/profile | Get user profile |
| POST | /api/auth/logout | Logout user |

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/projects | Create project |
| GET | /api/projects | List projects (paginated) |
| GET | /api/projects/:id | Get project |
| PUT | /api/projects/:id | Update project |
| DELETE | /api/projects/:id | Delete project |

### Training
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/training/text | Add training text |
| POST | /api/training/pdf | Upload PDF |
| GET | /api/training | List training data |
| DELETE | /api/training/:id | Delete training data |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/chat/conversations | Create conversation |
| GET | /api/chat/conversations | List conversations |
| PUT | /api/chat/conversations/:id | Update conversation |
| DELETE | /api/chat/conversations/:id | Delete conversation |
| POST | /api/chat/conversations/:id/messages | Send message |
| GET | /api/chat/conversations/:id/messages | Get messages |

### Prompts
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/prompts | Create prompt |
| GET | /api/prompts | List prompts |
| GET | /api/prompts/:id | Get prompt |
| PUT | /api/prompts/:id | Update prompt |
| DELETE | /api/prompts/:id | Delete prompt |

### Files
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/files/upload | Upload file |
| GET | /api/files | List files |
| DELETE | /api/files/:id | Delete file |

### Settings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/settings | Get settings |
| PUT | /api/settings | Update settings |
| GET | /api/settings/profile | Get profile |
| PUT | /api/settings/profile | Update profile |

## Data Flow

### Training Flow
```
User → Upload Text/PDF → Extract Content → Generate TF-IDF Embeddings → Store in DB
```

### Chat Flow
```
User Message → Find Relevant Training Data → Build Context → Send to Gemini → Store Response
```

### Vector Search Flow
```
Query → Generate Embedding → Cosine Similarity Search → Return Top K Results
```

## Environment Variables

```env
DATABASE_URL=postgresql://...
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRES_IN=7
GEMINI_API_KEY=your-gemini-key
FRONTEND_URL=http://localhost:3000
PORT=8000
ENV=development
```

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python main.py

# Database migrations run automatically on startup
```

## How to Run

### Prerequisites
- Python 3.8+
- PostgreSQL database (Supabase or local)
- Gemini API key

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
# Copy example env file
cp .env.example .env

# Edit .env with your values
# - DATABASE_URL: Your PostgreSQL connection string
# - JWT_SECRET: Random secret key
# - GEMINI_API_KEY: Your Gemini API key
# - FRONTEND_URLS: Your frontend URL(s)
```

### 5. Run Server
```bash
# Development
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --port 8000
```

### 6. Access API
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Database
Tables are created automatically on first run. Or run manually:
```sql
-- See sql/000_init.sql
```

## Deployment

See [VERCEL_DEPLOYMENT.md](../VERCEL_DEPLOYMENT.md) for Vercel deployment instructions.
