"""The 16-week Devscale AI Product Engineering curriculum, rebuilt from the original lesson list.

The original course numbers 22 topics (with several supplementary sessions inside one week).
They are grouped into 16 study weeks; every week keeps one session per original topic plus a
weekly "Micro Build" that applies the material in a small working app.
"""

Weeks = list[dict]

WEEKS: Weeks = [
    {
        "title": "LLM, AI, and Python Fundamentals",
        "description": "Start from zero: what LLMs and AI development are, then Python fundamentals.",
        "sessions": [
            (
                "Introduction and Learn about the Basic of LLM, AI, and AI Development Concepts",
                "Map the landscape of AI, ML, and LLMs, and the role of an AI product engineer.",
            ),
            (
                "Python - Variables, Data Types, Conditional, Looping, Functions, Arguments, and Outputs",
                "Refresh Python fundamentals used throughout the course: variables, control flow, and functions.",
            ),
            (
                "Basic AI Call and Basic Prompt Strategies",
                "Make a first LLM call and apply basic prompting strategies.",
            ),
        ],
    },
    {
        "title": "Prompt Strategies and Function/Tool Calling",
        "description": "Write reliable prompts and let models call functions with structured arguments.",
        "sessions": [
            (
                "Prompt Strategies and Function/Tool Calling #1",
                "Design clear prompts and understand tool schemas and the tool-calling cycle.",
            ),
            (
                "Function/Tool Calling #2 and Web Dev (Backend - FastAPI)",
                "Handle multi-step tool calls, then start building backends with FastAPI.",
            ),
        ],
    },
    {
        "title": "FastAPI, Database, and SQLModel",
        "description": "Build a structured FastAPI backend backed by a relational database.",
        "sessions": [
            (
                "FastAPI - Basic File Organizations, Settings, Routers and Database, ORM, and SQLModel",
                "Structure a FastAPI project and model relational data with SQLModel.",
            ),
        ],
    },
    {
        "title": "Alembic, Redis, and Background Work",
        "description": "Version the schema, add caching, and run background work.",
        "sessions": [
            (
                "FastAPI - Alembic, SQLModel, and Redis (Dependency Injection and Celery)",
                "Migrate with Alembic, cache with Redis, and run background work with dependency injection.",
            ),
        ],
    },
    {
        "title": "AI Agent Fundamentals and OpenAI Agents SDK",
        "description": "Understand agents as loops of reasoning and tool use, using the Agents SDK.",
        "sessions": [
            (
                "AI Agent Fundamentals and OpenAI Agents SDK",
                "Understand agent loops and explore the OpenAI Agents SDK building blocks.",
            ),
        ],
    },
    {
        "title": "Agent Sessions and Streaming",
        "description": "Persist agent conversations and stream responses to the client.",
        "sessions": [
            ("Agent Sessions and Streaming", "Persist conversation state and stream agent output."),
            ("Supplementary - Basic Streaming FastAPI + ReactJS", "Connect a streaming FastAPI endpoint to a React UI."),
            ("Supplementary - OpenAI SDK Streaming", "Handle streaming events from the OpenAI SDK."),
            ("Supplementary - OpenAI Agents SDK with EventFrame", "Work with event frames from the Agents SDK."),
        ],
    },
    {
        "title": "TypeScript, ReactJS, and AI Agents",
        "description": "Build typed React interfaces and design UI patterns for agent interactions.",
        "sessions": [
            ("TypeScript & ReactJS", "Use types, components, state, and data fetching in React."),
            ("ReactJS for AI Agents", "Design React UI patterns for agent interactions."),
        ],
    },
    {
        "title": "AI Agent Frontend",
        "description": "Assemble an agent-facing frontend and connect it end to end.",
        "sessions": [
            ("Supplementary - AI Agent Setup", "Set up the agent-facing UI shell."),
            ("Supplementary - UI Setup", "Build the app shell and base components."),
            ("Supplementary - AI SDK Setup", "Integrate the AI SDK client."),
            ("Supplementary - UI Parts Setup", "Render structured UI parts from the stream."),
            ("Supplementary - List Sessions", "List, select, and resume agent sessions."),
        ],
    },
    {
        "title": "OCR, Embeddings, and RAG Foundations",
        "description": "Turn documents into searchable vectors and start the RAG pipeline.",
        "sessions": [
            ("OCR and Embeddings", "Extract text from documents and generate embeddings."),
            ("Supplementary - Setup Backend", "Prepare the backend services for the RAG pipeline."),
            ("Supplementary - Setup Router & Worker", "Wire routing and background workers."),
            ("Supplementary - Setup Database Engine", "Configure the database engine for vectors."),
            ("Supplementary - Rag API & Task", "Expose ingestion and retrieval as API tasks."),
        ],
    },
    {
        "title": "RAG Chunking and Evaluation",
        "description": "Chunk documents well and measure whether retrieval works.",
        "sessions": [
            ("Rag Chunking & Simple Evaluation", "Choose chunking strategies and score retrieval quality."),
        ],
    },
    {
        "title": "Subagents and Multiagent Patterns",
        "description": "Delegate focused work and coordinate multiple agents.",
        "sessions": [
            ("Subagents & Multiagent Pattern", "Use subagents and compare handoff, supervisor, and pipeline patterns."),
        ],
    },
    {
        "title": "MCP Server Producer and Consumer",
        "description": "Expose tools through MCP and consume them from an agent.",
        "sessions": [
            ("MCP Server - Producer and Consumer", "Build and consume an MCP tool server."),
        ],
    },
    {
        "title": "Agent Setup Supplementary",
        "description": "Harden the agent setup with supplementary sessions.",
        "sessions": [
            ("Supplementary - Agent Setup", "Harden agent configuration for real workflows."),
            ("Supplementary - Agent Endpoint", "Expose a hardened agent through an API endpoint."),
        ],
    },
    {
        "title": "Guardrails and Agent Permissions",
        "description": "Constrain agent behavior and scope tools by permissions.",
        "sessions": [
            ("Guardrails & Agent Permission", "Define guardrails and scope agent tools by permissions."),
        ],
    },
    {
        "title": "Observability, Langfuse, and Coding Agents",
        "description": "Trace agent runs and work effectively with coding agents.",
        "sessions": [
            ("Tracing, Observe, and Langfuse", "Trace agent runs and send traces to Langfuse."),
            (
                "Agno Glimpse, Introductory, My working pipeline today with Coding Agent",
                "Explore Agno Glimpse and a real coding agent pipeline.",
            ),
        ],
    },
    {
        "title": "Deployment, Auth, and Final Assignment",
        "description": "Deploy to a VPS, secure it, and run the final assignment.",
        "sessions": [
            ("Supplementary - Setup VPS & SSH", "Provision a VPS and connect over SSH."),
            ("Supplementary - Setup UV", "Manage Python dependencies with uv on the server."),
            ("Supplementary - Setup Services", "Run the API as a systemd service."),
            ("Supplementary - Nginx CertBot", "Serve through Nginx with TLS certificates."),
            ("Supplementary - Deploy Frontend", "Build and serve the frontend in production."),
            ("Final Assignment Briefs", "Clarify the scope, requirements, and evaluation of the final assignment."),
            ("Supplementary - Auth", "Add authentication to the deployed app."),
            ("Supplementary - Hash Password", "Hash passwords safely."),
            ("Supplementary - Auth Login", "Implement login and token checks."),
            ("Supplementary - Authorization Concept", "Scope access with roles and permissions."),
        ],
    },
]

ESTIMATED_DURATION_MINUTES = 90
