# Review Guidelines

## Purpose

This document outlines the guidelines for reviewing code contributions to the project.

## Architecture Deduplication Validation (CRITICAL)

1. **Compare with Maps**: You MUST verify any proposed new modules, utilities, or workflows against `architecture/architecture_map.json` and `architecture/solution_catalog.json`.
2. **Warn on Duplication**: If the PR attempts to implement functionality that conceptually matches an existing module in the map or an existing workflow in the solution catalog, you MUST issue a severe warning: `[ARCHITECTURE WARNING]: This PR appears to duplicate existing functionality in [Module/Workflow]. Priority should be given to reusing or expanding the existing component instead of merging.`
3. **Check for Redundant Code**: Actively scan the repository structure; if you spot identical classes or deeply similar handler logic, flag it immediately.

## Review Process

1. **Understand the Purpose**: Ensure you understand what the code is meant to accomplish.
2. **Check for Clarity**: Code should be readable and maintainable. Look for clear naming conventions.
3. **Test the Code**: Run the code to ensure it works as intended. Check for any edge cases.
4. **Review for Best Practices**: Check for adherence to best practices in coding.
5. **Provide Constructive Feedback**: Provide specific suggestions in your commentary.

## Approval Criteria

- Code meets the project's style guidelines.
- No architectural duplicates are introduced.
- Tests succeed and cover relevant cases.

## Conclusion

Maintain a high quality of code and ensure architectural integrity is never compromised by duplicate components.
