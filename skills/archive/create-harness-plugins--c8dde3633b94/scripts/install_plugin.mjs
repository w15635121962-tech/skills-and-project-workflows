#!/usr/bin/env node
import { access } from 'node:fs/promises'
import { constants } from 'node:fs'
import { homedir } from 'node:os'
import { join, resolve } from 'node:path'
import { spawnSync } from 'node:child_process'
import { validatePlugin } from './validate_plugin.mjs'

const args = process.argv.slice(2)
const target = args[0]
let profile = 'web'
for (let index = 1; index < args.length; index += 1) {
  if (args[index] !== '--profile' || !args[index + 1]) {
    console.error(`Unknown option: ${args[index]}`)
    process.exit(2)
  }
  profile = args[index + 1]
  index += 1
}

if (!target) {
  console.error('Usage: install_plugin.mjs <plugin-directory> [--profile web]')
  process.exit(2)
}
if (!/^[a-z0-9][a-z0-9-]*$/.test(profile)) {
  console.error('Profile name must use lowercase letters, digits, and hyphens.')
  process.exit(2)
}

const pluginRoot = resolve(target)
try {
  const result = await validatePlugin(pluginRoot)
  console.log(`Validated ${result.packageName}@${result.version}`)
} catch (error) {
  console.error(error.message)
  process.exit(1)
}

const candidates = [process.env.DSH_BIN, 'dsh', join(homedir(), '.local', 'bin', 'dsh')].filter(Boolean)
let dsh
for (const candidate of candidates) {
  if (candidate === 'dsh') {
    const probe = spawnSync(candidate, ['--version'], { stdio: 'ignore' })
    if (!probe.error && probe.status === 0) { dsh = candidate; break }
    continue
  }
  try {
    await access(candidate, constants.X_OK)
    dsh = candidate
    break
  } catch {}
}
if (!dsh) {
  console.error('Cannot find the dsh executable. Set DSH_BIN and retry.')
  process.exit(1)
}

const installed = spawnSync(dsh, ['plugin', '--profile', profile, 'add', `link:${pluginRoot}`], { stdio: 'inherit' })
if (installed.error) {
  console.error(installed.error.message)
  process.exit(1)
}
if (installed.status !== 0) process.exit(installed.status ?? 1)
console.log(`Installed ${pluginRoot} into profile ${profile}. Restart the client to load Host or UI changes.`)
