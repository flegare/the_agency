# Gemini Agents

This repository contains a collection of agents that can be used as tools by the Gemini CLI.

## Overview

The goal of this project is to create a suite of specialized agents that extend the capabilities of the Gemini CLI. Each agent is a small, independent web service that exposes its functionality through an OpenAPI specification. The Gemini CLI can discover and use these agents as tools.

## Agents

- **File Analyzer Agent:** A simple agent that can perform basic analysis on files, such as counting lines.

## Getting Started

To use these agents, you need to have the Gemini CLI installed and configured. You also need to run the agent web services.

1.  Clone this repository.
2.  For each agent, navigate to its directory and install the required dependencies.
3.  Run the agent's web service.
4.  Copy the agent's OpenAPI specification to the `.gemini/tools/` directory.
