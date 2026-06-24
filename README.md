# 🎬 CineIndia — AI-Powered Movie Recommendation System

### Foundation Data Science (FDS) Production Project

> CineIndia is a production-grade movie recommendation engine that leverages a multi-algorithm approach to solve the most difficult problems in information retrieval: the Cold Start problem, the long-tail, and personalization at scale.

---

## Badges
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge) ![MySQL](https://img.shields.io/badge/MySQL-003B57?style=for-the-badge&logo=mysql&logoColor=white) ![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white) ![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwindcss&logoColor=white)

---

## Table of Contents
- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Backend Setup](#backend-setup)
  - [Database (MySQL) setup & seed](#database-mysql-setup--seed)
  - [Environment variables](#environment-variables)
  - [Run backend](#run-backend)
- [Frontend Setup](#frontend-setup)
  - [Environment variables](#frontend-environment-variables)
  - [Run frontend](#run-frontend)
- [Testing](#testing)
- [Deployment Notes](#deployment-notes)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Contact](#contact)
- [Screenshots / Demo](#screenshots--demo)

---

## About
CineIndia is an AI-driven movie recommendation system designed to provide personalized suggestions using a blend of algorithms and real-world production considerations such as cold-start handling and long-tail coverage. The repo contains a Python/Flask backend, a Next.js/React frontend, and MySQL for persistence.

---

## Features
- Multi-algorithm recommendation pipeline (collaborative + content-based + heuristics)
- Cold start handling strategies
- Personalization and long-tail recommendations
- Backend REST API (Flask)
- Frontend UI (Next.js + React + Tailwind)
- Database seed scripts and sample data

---

## Tech Stack
- Python (Flask) — backend API
- MySQL — relational storage for users, movies, interactions
- Next.js + React — frontend
- Tailwind CSS — styling
- Optional: Docker for containerization

---

## Architecture Overview
- Frontend (Next.js): UI, client-side calls to backend API.
- Backend (Flask): Recommendation engines, API endpoints, DB access, seeding scripts.
- Database (MySQL): Stores movies, user profiles, interactions, and seed data used for training/recommendations.
- Optional background jobs for offline model refreshes (not included by default).

---

## Prerequisites
- Node.js 18+ and npm / yarn
- Python 3.8+
- MySQL Server (8.x recommended) or compatible service
- Recommended: Git, and the ability to run local services (DB)

---

## Quick Start (developer)
Clone the repo, set up DB, start backend and frontend:

```bash
git clone https://github.com/N-AVTEJ/Movie_recommendation_system.git
cd Movie_recommendation_system
# Backend
cd backend
# follow backend setup below
# Frontend
cd ../frontend
# follow frontend setup below
