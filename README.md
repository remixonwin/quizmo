# Minnesota DMV Quiz - Automated Deployment

A robust PowerShell-based deployment automation solution for the Minnesota DMV Practice Quiz web application on DigitalOcean App Platform.

## Features

### Deployment Automation
- One-click deployment to DigitalOcean App Platform
- Automated tool installation and verification
- Environment configuration management
- Database setup and migration
- SSL/TLS configuration
- Domain management
- Monitoring and alerting setup
- Backup configuration
- Error tracking integration

### Validation & Verification
- Pre-deployment requirement validation
- Tool version compatibility checks
- Environment variable verification
- Post-deployment health monitoring
- Endpoint availability testing
- Performance metrics collection
- Resource usage monitoring

### Security Features
- Secure credential management
- SSL/TLS enforcement
- Environment-specific configurations
- Secure database setup
- Automated secret generation
- Access control implementation

### Monitoring & Logging
- Comprehensive logging system
- Performance metrics tracking
- Resource usage monitoring
- Error tracking and alerting
- Deployment state tracking
- Log rotation and management

## Prerequisites

- Windows PowerShell 5.1 or later
- Administrator privileges
- DigitalOcean account with API access
- Registered domain name
- Git
- Python 3.8+

## Quick Start

1. Clone the repository:
```powershell
git clone https://github.com/yourusername/mn-dmv-quiz-deploy.git
cd mn-dmv-quiz-deploy
```

2. Configure deployment settings:
```powershell
Copy-Item config.example.json config.json
# Edit config.json with your settings
```

3. Run the deployment:
```powershell
.\deploy_to_do.ps1
```

For advanced deployment options:
```powershell
# Deploy with validation override
.\deploy_to_do.ps1 -Force

# Deploy with custom configuration
.\deploy_to_do.ps1 -ConfigPath "path/to/config.json"
```

## Configuration

### Required Configuration
```json
{
    "DO_API_TOKEN": "your_digitalocean_api_token",
    "DOMAIN_NAME": "your.domain.name",
    "APP_NAME": "mn-dmv-quiz",
    "REGION": "nyc",
    "ENVIRONMENT": "production"
}
```

### Environment-Specific Configuration
Create environment-specific configs:
- `config.production.json`
- `config.staging.json`
- `config.development.json`

## Deployment Process

1. **Pre-deployment Validation**
   - Tool version verification
   - Required file checks
   - Environment validation
   - Authentication verification
   - Database connection testing
   - SSL configuration validation

2. **Deployment Steps**
   - Tool installation
   - Environment setup
   - App specification creation
   - Application deployment
   - Domain configuration
   - Monitoring setup
   - Backup configuration
   - Error tracking setup

3. **Post-deployment Verification**
   - Endpoint health checks
   - Content validation
   - Performance monitoring
   - Resource usage verification
   - Database connectivity testing

## Monitoring & Maintenance

### Logs
- Deployment logs: `logs/deployment.log`
- Error logs: `logs/deployment_error.log`
- Debug logs: `logs/deployment_debug.log`
- Metrics logs: `logs/deployment_metrics.log`

### Metrics
- CPU usage monitoring
- Memory utilization tracking
- Disk usage monitoring
- Response time tracking
- Error rate monitoring

## Troubleshooting

### Common Issues

1. **Validation Failures**
   ```powershell
   # Override validation
   .\deploy_to_do.ps1 -Force
   ```

2. **Permission Issues**
   - Run PowerShell as Administrator
   - Verify DigitalOcean API token permissions

3. **Deployment Failures**
   - Check `logs/deployment_error.log`
   - Verify configuration settings
   - Ensure sufficient DigitalOcean resources

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PowerShell best practices
- Add comprehensive logging
- Include validation checks
- Write clear documentation
- Add error handling
- Include rollback procedures

## Security Considerations

- Store API tokens securely
- Use environment-specific configs
- Implement proper access controls
- Follow security best practices
- Regular security updates
- Audit logging enabled

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Acknowledgments

- DigitalOcean App Platform
- PowerShell Community
- Minnesota DMV
- Open Source Contributors
