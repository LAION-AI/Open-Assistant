#!/usr/bin/env bash

export DATABASE_URI=postgresql://fozziethebeat@localhost:5432/ocgpt_backend

uvicorn app.main:app --reload
