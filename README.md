# AI Trends Intelligence Platform

A comprehensive intelligence platform for tracking and analyzing AI industry trends, built with Vue.js and FastAPI.

## Tech Stack

- **Frontend**: Vue.js, Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: Neon DB (PostgreSQL)
- **Hosting**: 
  - Backend API: Azure
  - Frontend: Vercel
- **CI/CD**: GitHub Actions (automated workflows via cron jobs)

## API Endpoints

- **Production API**: https://fastapi-trends-app.azurewebsites.net/
- **Hosted Frontend**: https://ai-trends-intelligence-platform.vercel.app/

## Prerequisites

- Node.js (v16 or higher)
- Python 3.8+
- pip (Python package manager)
- npm (Node package manager)

## Setup & Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI-Trends-Intelligence-Platform
```

### 2. Environment Setup

Create a `.env` file in the `frontend` and another in the `backend` directories with all required secrets (API keys, database credentials, etc.) (see .env.example files)

### 3. Backend Setup

#### Create Virtual Environment

```bash
# From project root
python -m venv venv
```

#### Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Frontend Setup

```bash
cd frontend
npm install
```

## Running Locally

### Start the Backend API

From the **project root** directory (with virtual environment activated):

```bash
python -m uvicorn backend.main:app --host 0.0.0.0
```

The API will be available at `http://localhost:8000`

### Start the Frontend

From the **frontend** directory:

```bash
npm run dev
```

The frontend will typically run on `http://localhost:5173` (or the next available port)

### Run Tailwind CSS (Development)

To watch and compile Tailwind CSS changes, run this in a separate terminal from the **frontend** directory:

```bash
npx tailwindcss -i ./src/assets/main.css -o ./src/assets/tailwind.css -w
```

## Documentation Generation

### Prerequisites

- **Doxygen** 1.15.0+: [Install Doxygen](https://www.doxygen.nl/download.html)
- **Graphviz** (optional, for diagrams): [Install Graphviz](https://graphviz.org/download/)

On Windows, you can install both via:
```bash
winget install DimitrivanHeesch.Doxygen
winget install Graphviz.Graphviz
```

### Generate Documentation

From the **project root** directory:

```bash
doxygen Doxyfile
```

This will generate HTML documentation in the `html/` directory, including:
- All Python backend code documentation
- All Vue.js and JavaScript frontend code documentation
- Dependency graphs and class hierarchies
- Searchable namespace and module organization

### Hosting Documentation on GitHub Pages

1. Push the `html/` directory to your repository
2. In your GitHub repository settings, navigate to **Pages**
3. Select `Deploy from a branch` and choose the branch containing your docs
4. Set the directory to `/html`
5. Your documentation will be available at `https://<username>.github.io/<repo-name>/`

### Customizing Documentation

Edit the `Doxyfile` to adjust:
- `EXTRACT_ALL`: Control what gets documented
- `HAVE_DOT`: Enable/disable diagram generation
- `WARN_IF_UNDOCUMENTED`: Get warnings for undocumented code
- `FILE_PATTERNS`: Change which file types to include

## Development Workflow

1. Activate your virtual environment
2. Start the backend API server
3. In a new terminal, navigate to frontend and start the dev server
4. (Optional) In another terminal, run the Tailwind watcher for live CSS updates

## Deployment

### Backend (Azure)

The backend is currently deployed to Azure and automatically updates via GitHub Actions workflows triggered by cron jobs.

### Frontend (Vercel)

The frontend is currently hosted on Vercel and deploys automatically on push to the main branch.

### Database

The application uses Neon DB (serverless PostgreSQL) for data storage.

## Project Structure

```
AI-Trends-Intelligence-Platform/
├── backend/
│   ├── requirements.txt   # Python dependencies
│   ├── main.py           # FastAPI application
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   │   ├── main.css
│   │   │   └── tailwind.css
│   │   └── ...
│   ├── .env              # Environment variables (not in repo)
│   └── package.json
└── venv/                 # Virtual environment (not in repo)
```