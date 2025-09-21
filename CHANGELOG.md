# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## **[0.1.7] - 2025-09-21**

### Added
- **Framework Integrations**:  
  - **Django**: `django_atp` app for seamless integration.  
    - Exposes each registered tool at `/atp/<toolkit_name>/<tool_name>/` (GET for metadata, POST for execution).  
    - Admin-friendly registration via `register_client()`.  
  - **FastAPI**: `fastapi_atp` registry with example endpoints for instant ATP routing.  
  - **Flask**: `flask_atp` registry and lightweight endpoints for quick adoption.
- **ToolKit Client Registration**:  
  - Introduced `register_client(<name>, <ToolKitClient>)` for explicit toolkit registration.
  - Eliminates the need to call `ToolKitClient.start()`.
- **API Marketplace Pattern**: Functions can now be instantly exposed as ATP-compatible HTTP endpoints across frameworks.
- **Cross-Framework Schema Consistency**: Unified protocol so that ChatATP and other ATP clients can call any registered tool without code changes.
- **Documentation Upgrade**:  
  - Added complete integration guides for Django, FastAPI, and Flask.
  - Included ready-to-copy code samples with curl examples.

### Changed
- **Refactored Startup Flow**: Removed mandatory `.start()` call; registration occurs at import time.
- **Cleaner Registry APIs**: Standardized `get_client()` lookup across Django, FastAPI, and Flask registries.
- **Improved Dependency Management**: Added optional extras (`django`, `fastapi`, `flask`) for targeted installs.

### Fixed
- **Endpoint Stability**: Ensured predictable JSON responses for both GET (tool metadata) and POST (execution) calls.
- **Import Order Issues**: Tools registered in app `ready()` now load reliably at server startup.

---

## **[0.1.5] - 2025-08-23**

### Added
- **Enhanced `pyproject.toml`**: Updated metadata, classifiers, and dependencies for better PyPI compatibility.
- **Improved Documentation**: Added detailed request/response flow in the README.
- **Support for Multi-Step Tool Calls**: Clarified how to loop through tool calls from LLMs (OpenAI, Anthropic, Mistral).

### Changed
- **Version Bump**: Updated to `0.1.5`.
- **Dependencies**: Specified minimum versions for `requests` and `websocket-client`.

### Fixed
- **Package Inclusion**: Ensured `atp_sdk` and its submodules are correctly included in the build.

---

## **[0.1.4] - 2025-08-20**

### Added
- **Initial Release**: First stable version of the Agent Tool Protocol SDK.
- **Core Features**:
  - `ToolKitClient` for registering and exposing Python functions as tools.
  - `LLMClient` for connecting to the ATP Agent Server and executing tools.
  - Support for WebSocket and HTTP protocols.
  - OAuth2 and API key authentication.
- **Examples**: Added usage examples for OpenAI, Anthropic, and Mistral AI.

### Changed
- **Project Structure**: Organized the project for better maintainability.

---

## **[Unreleased]**

### Planned
- **Async Support**: Add async/await support for tool execution.
- **Enhanced Error Handling**: Improve error messages and logging.
- **Schema Translation**: Support automatic conversion to/from OpenAI, Anthropic, and MCP tool schemas.
- **CLI Utilities**: Add commands for generating toolkits and scaffolding endpoints.

---

### How to Use This Changelog
- **Added**: New features.
- **Changed**: Changes in existing functionality.
- **Deprecated**: Soon-to-be removed features.
- **Removed**: Features that have been removed.
- **Fixed**: Bug fixes.
- **Security**: Vulnerability fixes.

---

This changelog will be updated with each new release. For more details, check the [GitHub repository](https://github.com/sam-14uel/Agent-Tool-Protocol).
