# Sourced by the harness scripts: resolves the Maven command.
# Order: $MVN_CMD, `mvn` on the PATH, then a Maven distribution under ~/.m2/wrapper/dists.
resolve_mvn() {
  if [ -n "${MVN_CMD:-}" ]; then echo "$MVN_CMD"; return 0; fi
  if command -v mvn >/dev/null 2>&1; then command -v mvn; return 0; fi
  local found
  found=$(ls -d "$HOME"/.m2/wrapper/dists/*/*/apache-maven-*/bin/mvn 2>/dev/null | sort | tail -n 1)
  if [ -n "$found" ]; then echo "$found"; return 0; fi
  return 1
}
