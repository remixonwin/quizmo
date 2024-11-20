# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2024-11-20

### Fixed
- Health check endpoint no longer returns 301 redirects in Kubernetes environment
- Added custom security middleware to handle health checks while maintaining SSL security
- Improved health check implementation with proper database and cache connection verification

### Changed
- Consolidated health check endpoint to a single implementation
- Updated SSL redirect behavior to exclude health check endpoint

## [1.0.2] - 2024-11-19

### Added
- Initial release with basic quiz functionality
- User authentication and registration
- Quiz taking and results tracking
- Admin interface for quiz management
