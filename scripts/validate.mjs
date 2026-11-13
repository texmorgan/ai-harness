#!/usr/bin/env node
// validate.mjs — lint skill, power, and steering files
//
// Checks:
// - Every skill in _registry.yaml has a SKILL.md
// - Every power in _index.yaml has a .md file
// - Every steering doc in _index.yaml exists
// - No skill references a non-existent convention
// - No power composes a non-existent skill

import { existsSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ROOT = join(__dirname, '..')

console.log('validate.mjs: skeleton. Wire up checks.')
console.log('  exit 0 (no-op).')
process.exit(0)
