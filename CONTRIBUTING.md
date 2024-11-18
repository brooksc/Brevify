# Contributing to Brevify

Thank you for your interest in contributing to Brevify! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Brevify.git
cd Brevify
```

2. Set up Python environment:
```bash
conda create -n Brevify python=3.8
conda activate Brevify
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Add your YouTube API key to `.env`

4. Start the development server:
```bash
python transcribe.py
```

## Code Style

- Python code follows PEP 8 guidelines
- Use type hints for all function parameters and return values
- Include docstrings for all functions and classes
- JavaScript code follows ESLint Standard configuration
- HTML/CSS follows Tailwind CSS conventions

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with clear commit messages
3. Add tests if applicable
4. Update documentation as needed
5. Submit a pull request with a description of changes

## Project Structure

- `/static` - Frontend assets (HTML, CSS, JavaScript)
- `transcribe.py` - Flask backend server
- Configuration files in root directory
- Documentation in Markdown format

## Testing

- Run Python tests: `python -m pytest`
- ESLint for JavaScript: `npm run lint`
- Manual testing of UI changes

## Questions?

Feel free to open an issue for any questions or concerns.
