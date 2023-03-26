#!/bin/bash

uvicorn main:app --host 0.0.0.0 --port "$PORT"
