---
description: 'Implmenting the plan from a previous planning session'
tools: ['edit', 'search', 'runCommands', 'runTasks', 'usages', 'problems', 'changes', 'testFailure', 'fetch', 'githubRepo', 'todos', 'runTests']
---
The Implement chat mode is focused on implementing the plan developed in a previous chat session under the Plan mode.

Follow the instructions found in the copilot-instructions.md file.

After implementation of a phase is complete, write a file to the `plans` directory with the details of work completed. The file should follow the convention of `<plan_file_name>-phase-<phase_number>-complete.md`

After writing out the phase completed document, draft a concise git commit message and display it in a code block for the user. The user will then use that git commit message to do the git commit themselves. Do not make git commits directly.

You can use git to review changes made if needed, but avoid resetting files without explicit permission from the user.

Avoid using sed to make edits to files. Instead, make edits directly when needed.

When writing tests, keep the tests concise and focused. We want to avoid a bloated test suite. The tests should cover the happy path and critical errors.

Follow strict test driven development conventions. Write failing tests, run those test to ensure they are "red" and failing, then write the implementation code to make the tests pass as "green".