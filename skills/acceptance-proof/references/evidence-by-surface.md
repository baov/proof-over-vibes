# Evidence by surface

What to capture, and what to assert, for each kind of surface. The skill names no driving tool: use whichever the agent has. If none can drive the surface, apply the degraded mode in `SKILL.md`.

Whatever the surface, a piece of evidence is a file plus one sentence "expected X, observed Y". The observed value is read from the surface (text, state, output), never estimated from how an image looks.

| Surface | Evidence | Assertion read from |
|---|---|---|
| Web page | Full-resolution screenshot of the viewport (or the region) after each step that carries an expectation | The visible text, the value of a field, the presence or absence of an element, read from the page itself |
| Mobile app | Screenshot of the device or simulator screen after the step | The text and state of the on-screen element |
| Desktop app | Screenshot of the window | The text and state of the element, read from the window |
| CLI | The command, its exit code and its output, saved as a text file | The exit code, and the lines of output that matter |
| API | The request (method, address, relevant headers, body) and the response (status, body), saved as a text file | The status and the fields of the body that the criterion names |

## Rules for every surface

- **Capture the starting state** before the first action, so the evidence shows a change.
- **One capture per expectation**, named `NN-<criterion>-<step>.<ext>`: the number gives the order, the criterion and the step make the file findable from the report.
- **Keep the captures with the report.** If the tool that drives the surface saves a capture elsewhere, copy it into the evidence folder beside the report and cite the copy, not the original.
- **Capture the failure as it is.** A DISPROVEN criterion keeps the screenshot or output of the actual state; do not retake it until it looks right.
- **Wait for the state to settle, then capture.** Read the observed value once the surface has stopped changing (a loading text, a spinner, an animation). If a capture caught a transient state, keep it, retake after the state settled, and say so in the raw log. This never applies to a failure: a failing state is not retaken to look right.
- **Keep secrets out.** Test accounts and test data only; blur or leave out anything that identifies a real person.
- **Time and randomness**: when the criterion depends on a value that changes (a date, an identifier), assert on its shape or on a value the run controls.
