# Autonomous Code Review Agent

An intelligent, autonomous code review agent powered by LLMs that analyzes pull requests for bugs, security vulnerabilities, performance issues, and provides actionable improvement suggestions.

## Features

- **Intelligent Code Analysis**: Leverages advanced LLMs to understand code context and intent
- **Bug Detection**: Identifies potential bugs, logic errors, and code smells
- **Security Scanning**: Detects security vulnerabilities and best practice violations
- **Performance Analysis**: Identifies performance bottlenecks and optimization opportunities
- **Code Quality Metrics**: Analyzes code complexity, maintainability, and readability
- **Real-time Updates**: Uses WebSocket for real-time communication and status updates
- **GitHub Integration**: Seamlessly integrates with GitHub API for PR analysis
- **Health Checks**: Built-in health check endpoints for monitoring
- **Containerized**: Production-ready Docker setup with multi-worker support

## Architecture

The application is built with:
- **FastAPI**: High-performance async web framework
- **Uvicorn**: ASGI server with multi-worker support
- **PyGithub**: GitHub API client for PR interactions
- **Transformers**: For NLP and code understanding
- **aiohttp**: Async HTTP client for external API calls
- **WebSocket**: Real-time communication with clients

## Installation

### Prerequisites
- Python 3.11+
- Docker (optional, for containerized deployment)
- GitHub Personal Access Token

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/Neuro-kiran/code-review-agent.git
cd code-review-agent
```

2. Create virtual environment:
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
# Edit .env with your GitHub token and other settings
```

5. Run the application:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker Deployment

### Build Image
```bash
docker build -t code-review-agent:latest .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e GITHUB_TOKEN="your_token_here" \
  -e LOG_LEVEL="INFO" \
  code-review-agent:latest
```

### Docker Compose
```bash
docker-compose up -d
```

## API Endpoints

### Health Check
```http
GET /health
```
Returns application health status.

### Code Review Analysis
```http
POST /analyze
```
Request body:
```json
{
  "code": "python code to review",
  "language": "python",
  "context": "optional context"
}
```

### GitHub PR Review
```http
POST /review-pr
```
Request body:
```json
{
  "repo_url": "https://github.com/user/repo",
  "pr_number": 42
}
```

### WebSocket Connection
```
WS /ws
```
Establish WebSocket connection for real-time updates.

## Configuration

Environment variables:

```env
# GitHub Configuration
GITHUB_TOKEN=your_github_token
GITHUB_API_BASE=https://api.github.com

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# AI/ML Configuration
MODEL_NAME=gpt-3.5-turbo
MODEL_TIMEOUT=30
MAX_TOKENS=2000
```

## Performance Optimization

- Async/await throughout for non-blocking I/O
- Connection pooling for database and API calls
- Caching strategies for repeated analyses
- Multi-worker Uvicorn setup for throughput
- Batch processing for multiple PRs

## Monitoring & Logging

The application includes:
- Structured logging with Structlog
- Loki integration for log aggregation
- Prometheus metrics (health check endpoint)
- Request/response logging
- Error tracking and reporting

## Security

- Non-root user execution in Docker
- Secure credential handling via environment variables
- Input validation and sanitization
- HTTPS support ready
- Regular dependency updates
- Security scanning in CI/CD

## Development

### Running Tests
```bash
pytest tests/ -v --cov=src
```

### Code Formatting
```bash
black src/
flake8 src/
pylint src/
```

### Type Checking
```bash
mypy src/
```

## Troubleshooting

### Connection Issues
- Verify GitHub token has appropriate permissions
- Check network connectivity to GitHub API
- Review logs for detailed error messages

### Performance Issues
- Increase worker count in production
- Enable caching for repeated analyses
- Monitor CPU and memory usage

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/Neuro-kiran/code-review-agent/issues
- Email: support@example.com

## Roadmap

- [ ] Multi-language support
- [ ] Custom rule configuration
- [ ] Integration with more VCS platforms
- [ ] Advanced ML model fine-tuning
- [ ] Web UI dashboard
- [ ] CLI tool for local analysis

## Author

Kiran Marne (Neuro-kiran)

## Acknowledgments

- FastAPI framework and community
- GitHub for excellent API documentation
- Hugging Face for transformer models
