"""React Error Boundary component for catching render-phase errors.

TODO:
1. Use "use client" directive
2. Import React, Component, ReactNode
3. Define Props interface with children and optional fallback
4. Define State interface with hasError boolean
5. Create ErrorBoundary class component that:
   - Has Props and State generics
   - Constructor sets initial state { hasError: false }
   - Implements getDerivedStateFromError() that returns { hasError: true }
   - Implements componentDidCatch(error, info) that calls shipError() with error details
   - render() returns fallback if hasError, else children
6. Export shipError() async function that:
   - Takes payload with message, source, lineno, colno, stack, url
   - POSTs to process.env.NEXT_PUBLIC_BASE_API_URL + "/monitoring/frontend-error"
   - Includes user_agent from navigator.userAgent
   - Uses fetch (not axiosInstance)
   - Silently catches errors (never throw from error reporting)
   - Has no return value (fire-and-forget)
7. Export default ErrorBoundary

See docs/observability.md for full implementation details.
"""

// TODO: Implement according to docs/observability.md
