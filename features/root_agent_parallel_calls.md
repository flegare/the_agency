# Feature Brief: Root Agent - Parallel Agent Calls

## Product Owner Request

The current `root_agent` executes calls to other agents serially, which can lead to performance bottlenecks, especially when orchestrating multiple agents. The Product Owner requests that the `root_agent` be re-architected to support parallel execution of agent calls, improving overall efficiency and responsiveness.

## Solution Architect Plan

**Goal:** Modify the `root_agent` to enable concurrent, non-blocking calls to other agents.

1.  **Analyze Current Implementation:** The `root_agent` currently uses `subprocess.run` with `curl` to make agent calls, which is a blocking operation. This confirms the need for an asynchronous approach.
2.  **Technology Selection:**
    *   Replace `curl` with an asynchronous HTTP client. `httpx` is a suitable choice for its modern API and `async`/`await` support.
    *   Utilize Python's `asyncio` library for managing concurrent tasks.
3.  **Core Logic Modification (`root_agent/main.py`):**
    *   **Update `call_agent` endpoint:**
        *   Change the `call_agent` FastAPI endpoint function to `async def`.
        *   Initialize an `httpx.AsyncClient` for making requests.
        *   Modify the logic within `call_agent` to use `httpx.AsyncClient.post` (or `get`, `put`, etc., based on the `method` in the request) instead of `subprocess.run` with `curl`.
        *   For the initial implementation, focus on making a single `call_agent` non-blocking. Future enhancements could involve accepting a list of calls and using `asyncio.gather` for true batch parallel execution.
    *   **Dependency Management:** Add `httpx` to `root_agent/requirements.txt`.
    *   **Error Handling:** Implement `try-except` blocks for `httpx` exceptions to gracefully handle network issues or agent failures.

## Testing Strategy

**Objective:** Verify that the `root_agent` can make non-blocking calls to other agents and that the overall performance is improved.

1.  **Unit Tests (`tests/test_root_agent.py` - new file):**
    *   **Test Non-Blocking Single Call:**
        *   Mock `httpx.AsyncClient` to simulate a delayed response from a target agent.
        *   Verify that the `call_agent` function does not block the main event loop (e.g., by using `asyncio.wait_for` with a short timeout).
    *   **Test Error Handling:**
        *   Mock `httpx.AsyncClient` to raise various exceptions (e.g., `httpx.RequestError`, `httpx.HTTPStatusError`).
        *   Verify that the `call_agent` endpoint returns appropriate HTTP error responses.

2.  **Integration Tests (Manual/Scripted):**
    *   **Setup:**
        *   Ensure all dockerized agents (including `root_agent`) are running.
        *   Identify a simple, quick endpoint on another agent (e.g., `historian_agent/health`).
    *   **Performance Comparison:**
        *   **Baseline (Current Serial):** Manually call the `root_agent`'s `/call_agent` endpoint multiple times in quick succession, targeting different agents. Observe the total time taken.
        *   **New Parallel Implementation:** After implementing the changes, repeat the above test. Expect a noticeable reduction in total execution time for concurrent requests.
    *   **Functionality Test:**
        *   Call various endpoints on different agents via the `root_agent` to ensure all functionalities remain intact.
        *   Verify successful responses and correct data handling.
