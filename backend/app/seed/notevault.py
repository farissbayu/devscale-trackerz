"""NoteVault: one product, sixteen weekly milestones.

NoteVault is the capstone built across the whole curriculum: a self-hosted personal
document assistant that is local-first, always cites its sources, and can act on
documents through tools — not just answer questions.

Every week's build session advances the same product using only that week's material.
Each brief keeps the same structure: GOAL, numbered BUILD steps, a DONE WHEN checklist,
and an optional STRETCH goal. Later milestones may replace earlier stubs; that is the
point — the codebase evolves like a real product.
"""

MILESTONE_OBJECTIVES: list[str] = [
    "Advance NoteVault according to this week's milestone brief.",
    "Check it against the DONE WHEN list before marking the session completed.",
    "Use NoteVault yourself and write down one friction point.",
]

NOTEVAULT_MILESTONES: dict[int, dict[str, str]] = {
    1: {
        "name": "Scaffold & First LLM Call",
        "description": (
            "GOAL\n"
            "NoteVault is a personal document assistant. This week it is only a seed: a repo, a\n"
            "config, and a Python client that can talk to an LLM. Everything later grows from here.\n\n"
            "BUILD\n"
            "1. Create the notevault/ project with a clean layout: llm.py (client), config from\n"
            "   environment variables, .env.example, .gitignore.\n"
            "2. Implement ask(prompt) that sends a chat completion with a system prompt describing\n"
            "   NoteVault's role: 'an assistant over the user's own documents'.\n"
            "3. Print the answer and the token usage from the response.\n"
            "4. Wrap errors: missing API key and network failure must print readable messages.\n"
            "5. Add notes.md and write the one-sentence product definition: 'local, cited, acting\n"
            "   assistant over my documents'.\n\n"
            "DONE WHEN\n"
            "- `python -m notevault ask \"What are you?\"` returns an in-character answer plus tokens.\n"
            "- Removing the API key gives a clean error, not a traceback.\n"
            "- The repo has no hardcoded secrets.\n\n"
            "STRETCH\n"
            "Add --temperature and --system flags to compare two answers side by side."
        ),
        "deliverable": "A runnable CLI seed of NoteVault with config, LLM client, and the product definition.",
    },
    2: {
        "name": "Prompts & the First Tool",
        "description": (
            "GOAL\n"
            "Give NoteVault its first capability: the model tags text snippets with topics through a\n"
            "tool call. This tagging becomes document organization in later weeks.\n\n"
            "BUILD\n"
            "1. Create prompts.py with template constants: TAGGER_SYSTEM and ASK_SYSTEM — compose,\n"
            "   never concatenate inline.\n"
            "2. Define the tag_snippet tool schema: text (string), returns tags (list of short labels).\n"
            "3. Persist snippets in snippets.json (a deliberate stub — the database replaces it in W3):\n"
            "   id, text, tags, created_at.\n"
            "4. Implement the tool-call cycle: model requests the call → validate args → execute →\n"
            "   return the result to the model → print its final answer.\n"
            "5. Log one case where the model tried to answer without calling the tool.\n\n"
            "DONE WHEN\n"
            "- `python -m notevault tag \"some text\"` stores the snippet with model-chosen tags.\n"
            "- Re-running tag on the same text appends a new snippet, not a crash.\n"
            "- The skipped-tool case is written down with your hypothesis why.\n\n"
            "STRETCH\n"
            "Add a suggest_tags tool that proposes tags for an existing snippet before saving."
        ),
        "deliverable": "A tagging flow with tool calling, persisted to snippets.json, plus one logged model quirk.",
    },
    3: {
        "name": "Real Database & CRUD API",
        "description": (
            "GOAL\n"
            "Replace the JSON stub with a real FastAPI + SQLModel backend. NoteVault gains its\n"
            "permanent shape: app/, models, routers, settings.\n\n"
            "BUILD\n"
            "1. Scaffold FastAPI with app/settings.py reading DATABASE_URL from the environment.\n"
            "2. Define Document (id, title, content, created_at, updated_at) and Tag (id, name,\n"
            "   document_id) with SQLModel; replace snippets.json with these tables.\n"
            "3. Implement POST/GET/PUT/DELETE for /documents and GET /documents/{id}/tags.\n"
            "4. Wire the W2 tagging flow as POST /documents/{id}/tag — the tool cycle now writes tags\n"
            "   into the database.\n"
            "5. Write a small script that imports snippets.json into the new tables.\n\n"
            "DONE WHEN\n"
            "- All document routes work and data survives a server restart.\n"
            "- Tagging through the API persists tags relationally.\n"
            "- The import script migrated your old snippets successfully.\n\n"
            "STRETCH\n"
            "Add GET /documents?tag=… filtering using a SQL join."
        ),
        "deliverable": "NoteVault as a FastAPI service with relational documents, tags, and the imported stub data.",
    },
    4: {
        "name": "Migrations, Cache & Background Work",
        "description": (
            "GOAL\n"
            "Harden the backend the way week 4 teaches: versioned schema, cached reads, and work\n"
            "that leaves the request cycle.\n\n"
            "BUILD\n"
            "1. Initialize Alembic against NoteVault's metadata; generate the baseline migration.\n"
            "2. Add documents.summary (nullable text) via a second migration; verify up and down.\n"
            "3. Cache GET /documents in Redis with a short TTL and log cache hits.\n"
            "4. Add a background task triggered on document create: count words and flag documents\n"
            "   over 500 words as 'long' in the summary field placeholder.\n"
            "5. Write a run.sh that starts API, worker dependencies, and Redis with one command.\n\n"
            "DONE WHEN\n"
            "- `alembic upgrade head` and `downgrade -1` both succeed on the NoteVault schema.\n"
            "- A repeated GET /documents visibly hits the cache.\n"
            "- Creating a document schedules background work without slowing the response.\n\n"
            "STRETCH\n"
            "Invalidate the documents cache automatically on any write."
        ),
        "deliverable": "Versioned NoteVault schema, cached document list, and background document statistics.",
    },
    5: {
        "name": "The NoteVault Agent",
        "description": (
            "GOAL\n"
            "NoteVault stops being endpoints and becomes an agent: a loop that decides which tools\n"
            "to run over your documents. This is the product's core mechanic.\n\n"
            "BUILD\n"
            "1. Implement two agent tools: search_documents(query) — keyword search over titles and\n"
            "   content — and tag_document(document_id).\n"
            "2. Build the agent loop with the OpenAI Agents SDK (or the W2 pattern): decide → call →\n"
            "   observe → repeat until final answer; cap iterations at 5.\n"
            "3. Expose POST /agent/run returning the answer plus a trace of tools used.\n"
            "4. Test one multi-step question: 'find my note about X and tag it'.\n"
            "5. Handle a tool failure: retry once, then answer with what it knows.\n\n"
            "DONE WHEN\n"
            "- One curl runs both tools in a single question and the trace proves it.\n"
            "- The iteration cap returns a readable partial answer.\n"
            "- A failing tool degrades gracefully instead of crashing the run.\n\n"
            "STRETCH\n"
            "Add search by tag so the agent can narrow results before reading content."
        ),
        "deliverable": "POST /agent/run answering questions by operating on documents through tools.",
    },
    6: {
        "name": "Sessions & Streaming",
        "description": (
            "GOAL\n"
            "Make conversations with the agent feel real: persistent sessions and streamed answers.\n"
            "The CLI era ends here — NoteVault becomes a service a UI can consume.\n\n"
            "BUILD\n"
            "1. Add Conversation and Message tables; every agent run stores its messages per session.\n"
            "2. Add GET /conversations and GET /conversations/{id}/messages for history.\n"
            "3. Implement POST /conversations/{id}/chat as a streaming endpoint (SSE) that yields\n"
            "   tokens as the agent produces them, then stores the full message.\n"
            "4. Send two turns in one session and confirm the second answer uses the first.\n"
            "5. Verify with curl -N that chunks arrive progressively.\n\n"
            "DONE WHEN\n"
            "- Text arrives progressively, not as one final block.\n"
            "- Reopening a session restores its full history.\n"
            "- The streamed answer is identical in content to a non-streamed run.\n\n"
            "STRETCH\n"
            "Stream tool-call events too, so a client can display 'searching documents…'."
        ),
        "deliverable": "Persisted conversations plus a streaming chat endpoint verified with curl -N.",
    },
    7: {
        "name": "Typed Web Console",
        "description": (
            "GOAL\n"
            "Give NoteVault a real face: a typed React console consuming the API. No logic in\n"
            "components; the API client owns the base URL.\n\n"
            "BUILD\n"
            "1. Create the Vite React TS app with components/ and hooks/ structure and shared types.\n"
            "2. Implement useChat: send a message, append the response, expose loading and error.\n"
            "3. Render the conversation and an input form that disables while streaming.\n"
            "4. Show a dedicated error panel with retry when the API is unreachable.\n"
            "5. Render agent tool traces as subtle chips under the answer ('used search_documents').\n\n"
            "DONE WHEN\n"
            "- `npm run build` passes with zero TS errors and no `any`.\n"
            "- Killing the backend shows the error panel, not a blank screen.\n"
            "- Tool traces are visible in the UI for agent answers.\n\n"
            "STRETCH\n"
            "Render tokens progressively from the W6 streaming endpoint."
        ),
        "deliverable": "A typed NoteVault console with loading, error, and tool-trace rendering.",
    },
    8: {
        "name": "The Real NoteVault App",
        "description": (
            "GOAL\n"
            "Assemble the product shell: session sidebar, streaming chat, document awareness. After\n"
            "this week NoteVault looks like the app you will demo at the end.\n\n"
            "BUILD\n"
            "1. Add the sidebar: list conversations, create new, switch between them.\n"
            "2. Keep scroll pinned to the newest message during streaming.\n"
            "3. Add a document panel listing documents from GET /documents.\n"
            "4. On a dropped stream mid-answer, show the partial text with retry/continue actions.\n"
            "5. Move all server calls into hooks; components stay presentational.\n\n"
            "DONE WHEN\n"
            "- Refresh restores the session list and current conversation from the backend.\n"
            "- Switching sessions swaps history without a page reload.\n"
            "- A dropped stream never leaves the UI stuck.\n\n"
            "STRETCH\n"
            "Rename and delete conversations with a confirmation dialog."
        ),
        "deliverable": "The NoteVault app shell: sidebar, streaming chat, document panel, recovery handling.",
    },
    9: {
        "name": "Documents In: OCR & Embeddings",
        "description": (
            "GOAL\n"
            "The moment NoteVault earns its name: real documents flow in. Upload, extract, chunk,\n"
            "embed — the retrieval foundation.\n\n"
            "BUILD\n"
            "1. Add POST /documents/upload accepting a PDF or image; store the file with an id.\n"
            "2. Extract text (OCR where needed) handling multi-page and empty results.\n"
            "3. Chunk text (~500 chars, 10% overlap) and store chunks linked to the document.\n"
            "4. Embed every chunk with the embeddings API; store vectors next to chunk text.\n"
            "5. Upload three of your own real documents — course notes, a contract, an article.\n\n"
            "DONE WHEN\n"
            "- Your real documents produce chunks and vectors you can count and inspect.\n"
            "- A phrase from page 3 of a document returns the chunk containing it.\n"
            "- An image-only document either OCRs or fails with a clear message.\n\n"
            "STRETCH\n"
            "Deduplicate near-identical chunks before embedding."
        ),
        "deliverable": "An upload-to-vectors pipeline loaded with three of your real documents.",
    },
    10: {
        "name": "Cited Answers & Evaluation",
        "description": (
            "GOAL\n"
            "NoteVault's promise is 'always cited'. Wire retrieval into the agent's answer, make the\n"
            "citations visible, and prove quality with a small evaluation set.\n\n"
            "BUILD\n"
            "1. Embed the user's question; retrieve top-k chunks (start k=3) as agent context.\n"
            "2. Require the answer to reference source chunk ids; render them as links in the UI.\n"
            "3. Write ten real questions about your uploaded documents with expected answers.\n"
            "4. Score each run: hit / partial / miss, and record the table in evals.md.\n"
            "5. Tune one variable (k or chunk size) and record the score change.\n\n"
            "DONE WHEN\n"
            "- Every answer shows where it came from — no uncited claims.\n"
            "- The ten-question table exists with scores before and after tuning.\n"
            "- You start using NoteVault for real questions (the weekly usage log begins).\n\n"
            "STRETCH\n"
            "Add a 'not in your documents' refusal when retrieval confidence is low."
        ),
        "deliverable": "Cited answers in the UI plus a ten-question evaluation table and your usage log.",
    },
    11: {
        "name": "Subagents for Deep Dives",
        "description": (
            "GOAL\n"
            "Teach NoteVault to delegate: a research subagent that digs deep into one document while\n"
            "the main agent orchestrates across many.\n\n"
            "BUILD\n"
            "1. Implement a research subagent: given one document id and a question, read its chunks\n"
            "   thoroughly and return a structured mini-report with citations.\n"
            "2. The main agent delegates to it when a question targets one document deeply.\n"
            "3. Run a comparison question across two documents; the orchestrator should fan out.\n"
            "4. Cap subagent iterations and propagate failures as readable results.\n"
            "5. Log which pattern you used (handoff vs supervisor) and why.\n\n"
            "DONE WHEN\n"
            "- A deep single-document question returns the subagent's cited mini-report.\n"
            "- A cross-document question fans out to two subagents.\n"
            "- A subagent failure surfaces as 'research failed for doc X', not a crash.\n\n"
            "STRETCH\n"
            "Stream subagent progress so the UI shows 'researching document 1 of 2…'."
        ),
        "deliverable": "Delegating research subagents with orchestrated multi-document answers.",
    },
    12: {
        "name": "NoteVault as MCP Server",
        "description": (
            "GOAL\n"
            "Open NoteVault to the outside: its search and summarize become MCP tools that any agent\n"
            "can discover and call — producer and consumer, both by you.\n\n"
            "BUILD\n"
            "1. Expose search_documents and summarize_document as MCP tools with clean schemas.\n"
            "2. Run the MCP server; connect a test client and list discovered tools.\n"
            "3. Call a tool through MCP and verify the result matches the direct API call.\n"
            "4. Connect the NoteVault agent itself as an MCP consumer for at least one tool.\n"
            "5. Add a third tool on the server and confirm discovery needs no client change.\n\n"
            "DONE WHEN\n"
            "- An external client lists and calls NoteVault tools over MCP.\n"
            "- MCP results match direct API results for the same input.\n"
            "- Adding a tool server-side appears in discovery automatically.\n\n"
            "STRETCH\n"
            "Expose the document list as an MCP resource, not only tools."
        ),
        "deliverable": "NoteVault serving its capabilities over MCP, consumed by an external client and its own agent.",
    },
    13: {
        "name": "Guardrails & Permissions",
        "description": (
            "GOAL\n"
            "Documents are private and sometimes sensitive. NoteVault must refuse out-of-scope\n"
            "requests, check its outputs, and respect tool permissions per role.\n\n"
            "BUILD\n"
            "1. Input guardrail: refuse prompts outside document assistance with a clear reason.\n"
            "2. Output guardrail: block answers containing secrets or forbidden patterns before they\n"
            "   reach the user.\n"
            "3. Tag tools with permission levels: read (everyone), write (owner), delete (admin).\n"
            "4. Pass a role with requests; refuse tools the role lacks and log the refusal.\n"
            "5. Write down three adversarial prompts you tried and what NoteVault did.\n\n"
            "DONE WHEN\n"
            "- 'Write a poem about anything' is refused as out of scope.\n"
            "- A non-owner role cannot delete a document; the refusal is logged.\n"
            "- The three adversarial cases and outcomes are documented.\n\n"
            "STRETCH\n"
            "Log every guardrail hit with input, reason, and timestamp for later review."
        ),
        "deliverable": "A guarded NoteVault: scoped refusals, output checks, and permission-aware tools.",
    },
    14: {
        "name": "Tracing & Observability",
        "description": (
            "GOAL\n"
            "Stop debugging blind. Every NoteVault run becomes inspectable: nested spans, latency,\n"
            "and one evaluation attached to a real trace.\n\n"
            "BUILD\n"
            "1. Integrate Langfuse; trace input, model calls, tool runs, and final output per run.\n"
            "2. Run three scenarios: a clean RAG question, a tool failure, a guardrail rejection.\n"
            "3. Attach an evaluation score plus a short quality note to one completed trace.\n"
            "4. Identify the slowest span across the three runs and note its share of latency.\n"
            "5. Use a coding agent to refactor one module from this week's lesson; review its diff.\n\n"
            "DONE WHEN\n"
            "- All three runs are visible in Langfuse with readable names and inputs.\n"
            "- One trace carries your evaluation score.\n"
            "- The slowest span is identified with a number, not a feeling.\n\n"
            "STRETCH\n"
            "Compare two prompt versions for the same question using trace scores."
        ),
        "deliverable": "Traced runs in Langfuse, one evaluation recorded, and the slowest span identified.",
    },
    15: {
        "name": "Deploy & Secure",
        "description": (
            "GOAL\n"
            "NoteVault leaves localhost: a VPS, TLS, services, and authentication. The document\n"
            "assistant becomes a product others can reach.\n\n"
            "BUILD\n"
            "1. Provision the VPS; install dependencies with uv; connect over SSH.\n"
            "2. Run the API as a systemd service; front it with Nginx and a CertBot certificate.\n"
            "3. Build and serve the React frontend in production behind the same domain.\n"
            "4. Add auth: hashed passwords, login issuing a token, and 401s on protected routes.\n"
            "5. Apply W13 permissions to real users: owner vs admin for document actions.\n\n"
            "DONE WHEN\n"
            "- https://your-domain serves NoteVault from the public internet.\n"
            "- Protected routes return 401 without a token and 200 with one.\n"
            "- A reboot leaves the service running.\n\n"
            "STRETCH\n"
            "Rate-limit the login route and add a simple rollback plan."
        ),
        "deliverable": "A live HTTPS NoteVault with authentication and permission-aware actions.",
    },
    16: {
        "name": "Ship, Demo & Reflect",
        "description": (
            "GOAL\n"
            "Finish the product: close remaining gaps, verify on the live URL, and present NoteVault\n"
            "like an engineer — including the failure case.\n\n"
            "BUILD\n"
            "1. Close or explicitly cut every remaining item; record each decision.\n"
            "2. Test critical paths: happy RAG flow, tool failure, guardrail refusal, unauthorized access.\n"
            "3. Verify the deployed build end to end on the live URL, not localhost.\n"
            "4. Write the README: what NoteVault is, how to run it, known limits, and the usage-log\n"
            "   stats from W10 onward.\n"
            "5. Script and record a five-minute demo, rehearsing the failure case out loud.\n\n"
            "DONE WHEN\n"
            "- The live URL works and the README matches reality.\n"
            "- The demo fits five minutes and includes a guardrail or failure path.\n"
            "- The recording exists and the usage log tells you honestly how much you used it.\n\n"
            "STRETCH\n"
            "Write the one-paragraph rollback plan you would follow if the demo fails live."
        ),
        "deliverable": "Deployed NoteVault, its README with real usage stats, and one recorded five-minute demo.",
    },
}
