#!/usr/bin/env bash

export ALLOW_ANY_API_KEY=True

uvicorn app.main:app --reload
