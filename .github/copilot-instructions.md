# Project Coding Standards

## TypeScript (Next.js/React Frontend)

### Type Safety
- Always define specific types; never use `any` type or type assertions with `as any`
- Enable strict TypeScript configuration with `strict: true` and `noImplicitAny: true`
- Use type inference where appropriate but prefer explicit return types for functions
- Define interfaces for component props and API response types

### Functions
- Use only arrow functions and anonymous function expressions; no function declarations
- Always use `export default functionName` for default exports
- Specify return types for all functions
- Prefer function composition over HOC (Higher Order Components); use HOC only when absolutely necessary

### Control Flow
- Never use `forEach`; use `for...of` for arrays or `for...in` for objects
- Prefer `map`, `filter`, `reduce` for functional array transformations when side effects are not needed

### Code Comments
- Do not add comments unless absolutely necessary; code should be self-explanatory
- Use descriptive variable names that clearly indicate purpose (e.g., `isUserAuthenticated`, `fetchUserData`)
- Add JSDoc comments only for complex business logic or public API functions

### Naming Conventions
- Use PascalCase for component names and interfaces
- Use camelCase for variables, functions, and methods
- Use UPPER_CASE for constants
- Prefix boolean variables with auxiliary verbs: `is`, `has`, `should`, `can`

### Next.js Specific
- Use Server Components by default; only use `use client` when client-side interactivity is required
- Implement proper error boundaries for error handling
- Use Next.js built-in features for routing, data fetching, and image optimization
- Follow Next.js project structure with `app` directory organization

## Python (Microservices)

### PEP-8 Compliance
- Follow PEP-8 style guide strictly for all Python code
- Use 4 spaces per indentation level; no tabs
- Limit lines to 79 characters maximum
- Use lowercase with underscores for function and variable names (snake_case)
- Use CapWords for class names (PascalCase)
- Use two blank lines between top-level function and class definitions
- Use one blank line between method definitions within a class

### Code Organization
- Group imports: standard library, third-party, local imports (separated by blank lines)
- Use absolute imports over relative imports
- Place imports at the top of the file
- Use `__all__` to explicitly define public API in modules

### Type Hints
- Use type hints for all function parameters and return values
- Import `typing` module for complex types
- Use `Optional[T]` for nullable values instead of Union with None
- Use `List[T]`, `Dict[K, V]`, `Set[T]` from typing for container types

### Error Handling
- Use specific exceptions; avoid bare except clauses
- Implement proper logging instead of print statements
- Use context managers for resource management
- Follow EAFP (Easier to Ask for Forgiveness than Permission) principle

### Security
- Never use `eval()` or `exec()` with untrusted input
- Use parameterized queries for all database operations
- Sanitize user input to prevent injection attacks
- Follow principle of least privilege for function permissions
- Use environment variables for sensitive configuration; never hardcode secrets
- Implement proper authentication and authorization using JWT or OAuth2
- Use HTTPS/TLS for all service communications
- Validate all inputs using Pydantic or similar libraries

### Code Quality
- Write self-documenting code with clear, descriptive names
- Keep functions small and focused on a single responsibility
- Use docstrings for modules, classes, and functions following Google or NumpPy style
- Avoid magic numbers; use named constants
- Use `is` and `is not` for comparisons with None, not equality operators
- Follow "explicit is better than implicit" from Zen of Python

### Logging
- Use `logging` module with appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Configure logger at module level: `logger = logging.getLogger(__name__)`
- Include contextual information in log messages
- Avoid print statements for production code

## Problem-Solving Principles

### Avoid Defensive Programming
- Do not add checks for things that should already be guaranteed (e.g., checking if TypeScript is installed, if dependencies exist)
- Trust the development environment and build process; don't clutter code with redundant validation
- Assume valid configuration and proper setup; fail fast if assumptions are violated rather than adding defensive checks everywhere

### Judicious Error Handling
- Add error handling only where failures are expected and can be meaningfully handled
- Let unexpected errors propagate to appropriate boundaries rather than catching everything
- Do not wrap code in try-catch blocks "just in case"; have a specific reason for catching an exception
- Use error boundaries in React/Next.js for UI failures, not try-catch around every render
- In Python, allow unexpected exceptions to bubble up rather than suppressing them with broad except clauses

### Root Cause Analysis
- When fixing bugs, identify and address the root cause rather than adding superficial patches
- Ask "why" five times to trace symptoms to fundamental problems
- If a type error occurs, fix the type definition or data flow instead of adding type assertions
- If a null reference happens, determine why the value is null rather than just adding null checks
- Refactor flawed logic instead of adding compensatory code
- Update documentation, types, or tests to prevent recurrence rather than adding comments explaining workarounds
- Prefer structural fixes: if data is malformed, validate at the source; if API contracts are unclear, clarify the contract
