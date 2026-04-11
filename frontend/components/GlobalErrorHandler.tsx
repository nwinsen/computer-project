"""Global error handlers for window.onerror and unhandled promise rejections.

TODO:
1. Use "use client" directive
2. Import useEffect from react
3. Import shipError from ErrorBoundary
4. Create default export component GlobalErrorHandler that:
   - Returns null (renders nothing)
   - Has useEffect that:
     - Creates handleError callback for window.onerror events:
       - Extracts message, filename, lineno, colno, error.stack
       - Calls shipError() with those fields + window.location.href
     - Creates handleUnhandledRejection callback for unhandledrejection events:
       - Extracts reason (can be Error or string)
       - Gets message and stack if Error, else stringifies reason
       - Calls shipError() with source="unhandled_promise_rejection"
     - Adds both as event listeners
     - Returns cleanup function that removes both listeners
   - Cleanup dependencies: [] (empty, run once on mount)

See docs/observability.md for full implementation details.
"""

// TODO: Implement according to docs/observability.md
