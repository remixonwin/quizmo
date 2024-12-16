# ...existing Dockerfile...

# Copy conftest.py to the project root
COPY conftest.py /workspaces/codespaces-django/conftest.py

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxss1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy and run the Playwright setup script
COPY setup_playwright.sh /setup_playwright.sh
RUN chmod +x /setup_playwright.sh
RUN /setup_playwright.sh

# ...existing Dockerfile...