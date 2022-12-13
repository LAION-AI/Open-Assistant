#!/usr/bin/env bash

export DATABASE_URI=postgresql://postgres:postgres@localhost:5432/postgres

uvicorn app.main:app --reload
