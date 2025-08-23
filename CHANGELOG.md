Here’s a **CHANGELOG.md** file for your **AgentToolProtocol** project, following best practices for versioning and release notes. This will help users track updates, bug fixes, and new features.

---

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- **More Examples**: Add additional examples for advanced use cases.

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