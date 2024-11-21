# Minnesota DMV Practice Quiz

A Django-based web application that helps users prepare for the Minnesota DMV permit test. Features a comprehensive question bank with both text-based and image-based questions.

## Features

- 40-question practice tests with real DMV questions
- Traffic sign recognition questions with images
- Instant feedback and explanations
- Progress tracking
- Mobile-friendly interface
- Secure user authentication
- Detailed score reports

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- virtualenv (recommended)

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mn-dmv-quiz.git
   cd mn-dmv-quiz
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Load the question bank:
   ```bash
   python manage.py create_full_dmv_quiz
   ```

7. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

8. Run the development server:
   ```bash
   python manage.py runserver
   ```

Visit http://localhost:8000 to access the application.

## Development Setup

For development, you'll need:

1. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

3. Run tests:
   ```bash
   python manage.py test
   ```

## Deployment

For production deployment:

1. Set up environment variables:
   ```bash
   cp .env.example .env.prod
   # Edit .env.prod with production settings
   ```

2. Configure your web server (e.g., nginx, Apache)
3. Set up SSL certificates
4. Configure your database (PostgreSQL recommended)
5. Set up static files serving

See DEPLOYMENT.md for detailed deployment instructions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Acknowledgments

- Minnesota Department of Public Safety
- Driver and Vehicle Services Division (DVS)
- Contributors and maintainers
