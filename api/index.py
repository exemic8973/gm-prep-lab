"""Coding Prep API — FastAPI + PostgreSQL.

Local:   uvicorn api.index:app --port 8000   (also serves the static site)
Vercel:  @vercel/python build; vercel.json routes /api/* here

Accounts live in PostgreSQL. Passwords are hashed with bcrypt server-side;
sessions are opaque, revocable bearer tokens stored in the users table.
"""
import json
import logging
import os
import secrets

import bcrypt
import psycopg
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logger = logging.getLogger("coding-prep")

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres@127.0.0.1:5432/coding_prep_dev")
VALID_DOMAINS = {"problems", "tracker", "design", "behav"}

app = FastAPI(title="Coding Prep API")
# Same-origin architecture (Vercel routes /api/* and the static site together;
# local dev serves both from uvicorn). CORS is restricted to known origins only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "https://gm-prep-lab.vercel.app",
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


class Creds(BaseModel):
    username: str
    password: str


class StatePayload(BaseModel):
    data: dict


def db():
    try:
        # prepare_threshold=None: disables server-side prepared statements,
        # required when running through a pgbouncer/Neon pooled connection.
        return psycopg.connect(DATABASE_URL, prepare_threshold=None, connect_timeout=10)
    except Exception:
        raise HTTPException(503, "Database unavailable")


SCHEMA = [
    """CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        pass_hash TEXT NOT NULL,
        token TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""",
    """CREATE TABLE IF NOT EXISTS user_state (
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        domain TEXT NOT NULL,
        data JSONB NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        PRIMARY KEY (user_id, domain)
    )""",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS token_created_at TIMESTAMPTZ",
]


def init_schema():
    """Create/migrate tables on startup so a fresh deployment (e.g. Vercel)
    is self-sufficient once DATABASE_URL points at a reachable Postgres."""
    try:
        with db() as conn:
            for stmt in SCHEMA:
                conn.execute(stmt)
            conn.commit()
    except Exception as e:
        logger.warning("schema init skipped (database unavailable?): %s", e)


init_schema()


def bearer(authorization: str) -> str:
    return (authorization or "").removeprefix("Bearer ").strip()


def auth_user(token: str):
    if not token:
        raise HTTPException(401, "Not signed in")
    with db() as conn:
        row = conn.execute(
            "SELECT id, username FROM users WHERE token = %s"
            " AND (token_created_at IS NULL OR token_created_at > now() - interval '30 days')",
            (token,),
        ).fetchone()
    if not row:
        raise HTTPException(401, "Not signed in")
    return {"id": row[0], "username": row[1]}


@app.get("/api/health")
def health():
    try:
        with db() as conn:
            conn.execute("SELECT 1")
        return {"ok": True, "db": True}
    except Exception as e:
        logger.warning("health check DB error: %s", e)
        return {"ok": True, "db": False}


@app.post("/api/register")
def register(creds: Creds):
    user = creds.username.strip().lower()
    if "@" in user:
        raise HTTPException(400, "That\u2019s an email \u2014 this app uses a username. Pick one like wei8973 (letters/numbers/_/- only).")
    if not user or not all(c.isalnum() or c in "_-" for c in user) or not (3 <= len(user) <= 24):
        raise HTTPException(400, "Username: 3\u201324 characters, letters/numbers/_/-.")
    if len(creds.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters.")
    if len(creds.password.encode("utf-8")) > 72:
        raise HTTPException(400, "Password too long (max 72 bytes).")
    pass_hash = bcrypt.hashpw(creds.password.encode(), bcrypt.gensalt()).decode()
    token = secrets.token_urlsafe(32)
    with db() as conn:
        try:
            row = conn.execute(
                "INSERT INTO users (username, pass_hash, token, token_created_at)"
                " VALUES (%s, %s, %s, now()) RETURNING id, username",
                (user, pass_hash, token),
            ).fetchone()
            conn.commit()
        except psycopg.errors.UniqueViolation:
            # rely on the unique constraint — no check-then-act race
            raise HTTPException(409, "Username already exists \u2014 log in instead.")
    return {"token": token, "user": row[1]}


@app.post("/api/login")
def login(creds: Creds):
    user = creds.username.strip().lower()
    if len(creds.password.encode("utf-8")) > 72:
        raise HTTPException(401, "Wrong password.")   # reject early — no unbounded bcrypt cost
    with db() as conn:
        row = conn.execute(
            "SELECT id, username, pass_hash FROM users WHERE username = %s", (user,)
        ).fetchone()
        if not row or not bcrypt.checkpw(creds.password.encode(), row[2].encode()):
            raise HTTPException(401, "Wrong password.")
        token = secrets.token_urlsafe(32)
        conn.execute(
            "UPDATE users SET token = %s, token_created_at = now() WHERE id = %s",
            (token, row[0]),
        )
        conn.commit()
    return {"token": token, "user": row[1]}


@app.post("/api/logout")
def logout(authorization: str = Header(default="")):
    token = bearer(authorization)
    if token:
        with db() as conn:
            conn.execute("UPDATE users SET token = NULL WHERE token = %s", (token,))
            conn.commit()
    return {"ok": True}


@app.get("/api/me")
def me(authorization: str = Header(default="")):
    return auth_user(bearer(authorization))


@app.get("/api/state/{domain}")
def get_state(domain: str, authorization: str = Header(default="")):
    if domain not in VALID_DOMAINS:
        raise HTTPException(404, "Unknown domain")
    u = auth_user(bearer(authorization))
    with db() as conn:
        row = conn.execute(
            "SELECT data FROM user_state WHERE user_id = %s AND domain = %s",
            (u["id"], domain),
        ).fetchone()
    # psycopg 3 parses JSONB into Python objects automatically
    return {"data": row[0] if row else None}


@app.put("/api/state/{domain}")
def put_state(domain: str, payload: StatePayload, authorization: str = Header(default="")):
    if domain not in VALID_DOMAINS:
        raise HTTPException(404, "Unknown domain")
    u = auth_user(bearer(authorization))
    with db() as conn:
        conn.execute(
            """INSERT INTO user_state (user_id, domain, data, updated_at) VALUES (%s, %s, %s, now())
               ON CONFLICT (user_id, domain)
               DO UPDATE SET data = EXCLUDED.data, updated_at = now()""",
            (u["id"], domain, json.dumps(payload.data)),   # jsonb takes a JSON string
        )
        conn.commit()
    return {"ok": True}


# Local dev only: serve the static site from the same origin.
# (On Vercel the static files are served by Vercel's edge, not this function.)
if not os.environ.get("VERCEL"):
    from fastapi.staticfiles import StaticFiles

    app.mount("/", StaticFiles(directory=".", html=True), name="static")
