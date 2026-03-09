# User Login and Landing Page Access

This project implements a secure user login system and provides access to a landing page, as defined by Jira issue SCRUM-32 and its associated High-Level Design (HLD).

## Architecture

The system follows a microservices architecture with a clear separation of concerns:

- **Frontend**: A web-based user interface for login, built with HTML, CSS, and JavaScript.
- **Backend**: A Python-based Authentication Service that handles user authentication, password hashing, and session management. It exposes a `/api/login` endpoint.
- **Database**: PostgreSQL for securely storing user credentials (hashed passwords and salts).

All communication is secured using HTTPS.

## Features

- User authentication via username and password.
- Secure storage of user credentials using bcrypt hashing and salting.
- Secure session management with session ID regeneration.
- Client-side and server-side input validation for login fields.
- Generic error messages for failed login attempts to prevent information leakage.
- Redirection to a designated landing page upon successful login.

## Setup Instructions

### Prerequisites

- Docker
- Docker Compose (for local development)
- Python 3.x
- PostgreSQL client (optional, for direct database interaction)

### Local Development Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/p67428378-afk/login-page.git
    cd login-page
    ```

2.  **Environment Variables:**
    Create a `.env` file in the root directory with the following content:
    ```
    DATABASE_URL="postgresql://user:password@db:5432/login_db"
    SECRET_KEY="your_super_secret_key_for_session_management"
    ```
    Replace `user`, `password`, and `login_db` with your desired PostgreSQL credentials and database name. Replace `your_super_secret_key_for_session_management` with a strong, randomly generated key.

3.  **Build and run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    This will:
    -   Build the Docker images for the backend and database.
    -   Start the PostgreSQL database.
    -   Run database migrations (if any, will be added later).
    -   Start the backend authentication service.
    -   Serve the frontend application.

4.  **Access the application:**
    Open your web browser and navigate to `http://localhost:8000` (or the port configured for the frontend).

### Database Schema

The PostgreSQL database will contain a `users` table with the following structure:

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Deployment (GCP - Kubernetes)

The HLD specifies deployment on Google Cloud Platform using Google Kubernetes Engine (GKE).
A `Dockerfile` for the backend service will be provided, enabling containerization.
Kubernetes manifests (e.g., `deployment.yaml`, `service.yaml`) would be used for deployment, along with a CI/CD pipeline (e.g., Cloud Build) to automate builds and deployments.

*(Note: Kubernetes manifests and CI/CD pipeline configurations are out of scope for the initial implementation of SCRUM-32 but are part of the overall HLD.)*

## Usage

1.  Open the login page in your browser.
2.  Enter your username and password.
3.  Click "Login".
4.  Upon successful login, you will be redirected to the landing page.
5.  If login fails, a generic error message will be displayed.

## Project Structure

```
.
├── .env.example
├── Dockerfile          # Dockerfile for the backend service
├── docker-compose.yml  # Docker Compose for local development
├── README.md           # This file
├── requirements.txt    # Python dependencies for the backend
└── src/
    ├── backend/
    │   ├── main.py     # FastAPI application for authentication
    │   └── database.py # Database connection and user model
    └── frontend/
        ├── index.html  # Login page HTML
        └── script.js   # Frontend JavaScript for login logic
        └── style.css   # Frontend CSS for styling
```
