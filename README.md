# 🪐 ASTROPARAMITA JYOTISH Transit Engine API

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Astroparamita JYOTISH API** is a professional-grade microservice designed for Vedic astrology calculations and real-time transit analysis. Built with **Clean Architecture** principles, it leverages the precision of the Swiss Ephemeris to provide detailed insights into planetary positions, house scores, and astrological periods.

---

## ✨ Key Features

- 🔭 **Precision Calculations**: Powered by `pyswisseph` (Swiss Ephemeris) for high astronomical accuracy.
- 📊 **Deep Transit Analysis**: Automated scoring for houses, planet aspects, Sade-Sati detection, and Vimshottari Dasha periods.
- 🚀 **High Performance**: Optimized core logic with an average request processing time of **< 20ms**.
- 🐳 **Production Ready**: Fully containerized with Docker, featuring centralized logging and health monitoring.
- 🛡️ **Robust Validation**: Strict data schema enforcement using Pydantic v2.


## 📖 Interactive API Documentation

Once the service is running, you can access the interactive documentation at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
---

## 🛠 Reliability & Production Standards

- **Error Handling**: Graceful error management with clear HTTP exception responses and detailed internal traceback logging.
- **Logging Strategy**: Structured logging implemented via `FileHandler` and `StreamHandler` for both persistence and real-time container monitoring.
- **Continuous Integration**: Automated testing pipeline via GitHub Actions ensures every commit passes unit and integration benchmarks.
- **Environment Management**: Secure configuration handling using `.env` templates and Pydantic settings.
---


## 🛠 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous Python Web Framework)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **Astronomy Core**: [Swiss Ephemeris](https://github.com/astrorama/pyswisseph)
- **DevOps**: Docker, GitHub Actions (CI), Makefile
- **Testing**: Pytest (Unit & Integration)

---

## 🏗 System Architecture

The project follows a modular structure to ensure maintainability and scalability:

- **`app/api.py`**: API layer, request routing, and middleware configuration.
- **`app/schemas.py`**: Pydantic data models and strict validation rules.
- **`app/transit_service.py`**: Service layer orchestrating the flow between API and core logic.
- **`core.py`**: Main astronomical engine interface.
- **`core_files/`**: Pure business logic and Vedic calculations (framework-independent).
- **`tests/`**: Multi-layered testing suite covering both API endpoints and core logic.



---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ or Docker installed.

### Using Docker (Recommended)
Spin up the service in seconds:
```bash
make docker-build
make docker-run