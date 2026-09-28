# Business Listings Dashboard

Internship assignment for Honeybee Digital: a full-stack, data-driven Business Listings Dashboard built with React, FastAPI, and MySQL.

## Project Overview

This project collects, cleans, stores, and visualizes business listing data.

The dashboard provides business counts grouped by:

- City

- Category

- Source

The application follows a simple full-stack architecture:

React frontend → FastAPI backend → MySQL database

## Features

- 600 business listing records

- Data cleaning and validation pipeline

- MySQL database with `listing_master` table

- FastAPI REST APIs

- Bulk listing insertion API

- City-wise business aggregation

- Category-wise business aggregation

- Source-wise business aggregation

- React dashboard

- Recharts-based visualizations

- KPI summary cards

- Responsive dashboard UI

- SQL database dump for easy restoration

## Technology Stack

### Frontend

- React.js

- Vite

- Axios

- Recharts

### Backend

- Python

- FastAPI

- SQLAlchemy

- PyMySQL

### Database

- MySQL 8

## Project Structure

```text

business-listings-dashboard/

│

├── backend/

│   ├── app/

│   │   ├── routes/

│   │   ├── schemas/

│   │   ├── services/

│   │   ├── scraper/

│   │   ├── models/

│   │   ├── [database.py](http://database.py)

│   │   └── [main.py](http://main.py)

│   │

│   ├── tests/

│   ├── requirements.txt

│   └── .env.example

│

├── frontend/

│   ├── src/

│   │   ├── pages/

│   │   ├── services/

│   │   ├── App.jsx

│   │   └── App.css

│   ├── package.json

│   └── .env.example

│

├── database/

│   ├── schema.sql

│   └── business_listings_dump.sql

│

├── data/

│   ├── raw/

│   │   └── listings_raw.csv

│   └── processed/

│       ├── listings_clean.csv

│       └── data_quality_report.json

│

├── .gitignore

└── [README.md](http://README.md)

