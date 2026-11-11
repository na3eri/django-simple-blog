
<h1 align="center">Ultimate Django 5.2 API Starter</h1>
<h3 align="center">A solid, production-ready starting point for backend/API projects</h3>

<p align="center">
<a href="https://www.python.org"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" width="40" height="40"/></a>
<a href="https://www.djangoproject.com/"><img src="https://user-images.githubusercontent.com/29748439/177030588-a1916efd-384b-439a-9b30-24dd24dd48b6.png" width="60" height="40"/></a>
<a href="https://www.docker.com/"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/docker/docker-original-wordmark.svg" width="40" height="40"/></a>
<a href="https://www.postgresql.org"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original-wordmark.svg" width="40" height="40"/></a>
<a href="https://git-scm.com/"><img src="https://www.vectorlogo.zone/logos/git-scm/git-scm-icon.svg" width="40" height="40"/></a>
</p>

# Guideline
- [Guideline](#guideline)
- [Goal](#goal)
- [Setup](#setup)
- [Features](#features)
- [Configurations](#configurations)
- [Development](#development)
- [Testing](#testing)
- [License](#license)
- [Bugs](#bugs)

# Goal
A complete Django 5.2 API-focused starter that ships with Docker, Nginx, Gunicorn, SSL support, CI/CD, PostgreSQL, DRF, JWT authentication, and production-grade settings.

# Setup
Clone the repository:

```sh
git clone https://github.com/your/repo.git
````

Environment variables for development are included in `docker-compose.yml`. Modify them as needed.

Build the stack:

```sh
docker compose up --build
```

Visit the app at:

```
http://localhost:8000/swagger
```

# Features

<ul>
  <li><strong>Django 5.2 (LTS)</strong></li>
  <p>Latest long-term support version configured for API-first development.</p>

  <li><strong>Git</strong></li>
  <p>Gitignore, base README and optional license included.</p>

  <li><strong>Docker</strong></li>
  <p>Separate dev/prod Dockerfiles, optimized Python image, and dockerignore.</p>

  <li><strong>Docker Compose</strong></li>
  <p>Full dev and prod configurations with PostgreSQL, volumes, and networks.</p>

  <li><strong>Environment Files</strong></li>
  <p>Sample .env files and environment loader.</p>

  <li><strong>DRF + JWT</strong></li>
  <p>Django Rest Framework, CORS, SimpleJWT, and authentication flows.</p>

  <li><strong>Swagger & Redoc</strong></li>
  <p>Auto-generated interactive API documentation.</p>

  <li><strong>CI/CD with GitHub Actions or Gitlab</strong></li>
  <p>Prebuilt workflows for testing and Docker-based deployment.</p>

  <li><strong>Black & Flake8</strong></li>
  <p>Automatic formatting and linting included.</p>

  <li><strong>Preconfigured Settings</strong></li>
  <p>Email, DB, static, media, logging, security, CORS, and more.</p>
</ul>

# Configurations

<ul>
  <li><strong>Static & Media</strong></li>
  <p>STATIC_ROOT, MEDIA_ROOT, and STATICFILES_DIRS included.</p>

  <li><strong>Templates</strong></li>
  <p>Global templates directory for shared HTML (if needed).</p>

  <li><strong>Sitemaps & Robots</strong></li>
  <p>Preconfigured site framework, example robots.txt and sitemap.</p>

  <li><strong>Database</strong></li>
  <p>Production-ready PostgreSQL config with volumes.</p>

  <li><strong>Email</strong></li>
  <p>SMTP configs for dev and prod via environment variables.</p>

  <li><strong>Custom Error Handling</strong></li>
  <p>Custom error handling from the core.</p>

  <li><strong>Cookie Based Authentication</strong></li>
  <p>Sample accounts app and endpoints for custom cookie based authentication.</p>

  <li><strong>Security</strong></li>
  <p>HTTPS redirects, HSTS, secure cookies, proxy headers, CSP, and more.</p>
</ul>

# Development

Run the stack:

```sh
docker compose up --build
```

# Testing

Run all checks:

```sh
docker compose run --rm backend sh -c "black -l 79 && flake8 && pytest"
```


# License

MIT.

# Bugs

Open an issue if you find any bugs or missing features.
