#! /usr/bin/env bash

# Database migrations
alembic upgrade head

# Create initial data in DB
python app/init_database.py
