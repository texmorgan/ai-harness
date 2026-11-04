#!/usr/bin/env node
// doctor.mjs — compare generated bindings to source.
// Run in CI on every PR. Fail if drift.
//
// For each entry in _registry.yaml:
//   1. Render the expected binding.
//   2. Read the actual file on disk.
//   3. Diff. Report.
//
// Exit 1 if any binding is stale.

console.log('doctor.mjs: skeleton. Wire up diff logic.')
console.log('  exit 0 (no-op).')
process.exit(0)
