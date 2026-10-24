#!/usr/bin/env node
import { readFile, readdir, stat } from 'node:fs/promises'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { basename, dirname, join, resolve } from 'node:path'

const NAME = /^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$/

async function isFile(path) {
  try { return (await stat(path)).isFile() } catch { return false }
}

async function checkJavaScript(path, errors) {
  const result = spawnSync(process.execPath, ['--check', path], { encoding: 'utf8' })
  if (result.status !== 0) errors.push(`${basename(path)} failed syntax check: ${(result.stderr || result.stdout).trim()}`)
}

function parseFrontmatter(text) {
  const match = text.match(/^---\n([\s\S]*?)\n---(?:\n|$)/)
  if (!match) return undefined
  const values = {}
  for (const line of match[1].split('\n')) {
    const pair = line.match(/^([a-zA-Z0-9_-]+):\s*(.*)$/)
    if (!pair) continue
    values[pair[1]] = pair[2].replace(/^['"]|['"]$/g, '')
  }
  return values
}

export async function validatePlugin(inputPath) {
  const root = resolve(inputPath)
  const errors = []
  const manifestPath = join(root, 'package.json')
  let manifest
  try {
    manifest = JSON.parse(await readFile(manifestPath, 'utf8'))
  } catch (error) {
    errors.push(`package.json is missing or invalid: ${error.message}`)
  }

  if (manifest) {
    if (typeof manifest.name !== 'string' || !NAME.test(manifest.name.replace(/^@[^/]+\//, ''))) errors.push('package name is missing or invalid')
    if (typeof manifest.version !== 'string' || !/^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$/.test(manifest.version)) errors.push('version must be valid semver')
    if (manifest.type !== 'module') errors.push('package type must be module')
    const main = typeof manifest.main === 'string' ? manifest.main : 'index.js'
    if (!await isFile(join(root, main))) errors.push(`main entry is missing: ${main}`)
    else await checkJavaScript(join(root, main), errors)

    const patch = manifest.dsh?.bundle?.patch
    if (typeof patch !== 'string') errors.push('manifest must declare dsh.bundle.patch')
    else if (!await isFile(join(root, patch))) errors.push(`bundle patch is missing: ${patch}`)
    else {
      const patchText = await readFile(join(root, patch), 'utf8')
      if (!patchText.includes('- insert:')) errors.push('bundle patch must contain an insert operation')
      if (patchText.includes('SCAFFOLD_PLACEHOLDER')) errors.push('bundle patch contains an unresolved scaffold placeholder')
      if (manifest.files?.includes('skills') && !patchText.includes(`node_modules/${manifest.name}/skills/`)) {
        errors.push(`bundle patch must resolve bundled skills through node_modules/${manifest.name}/skills/`)
      }
    }

    if (manifest.dsh?.client) {
      const client = manifest.exports?.['./client']
      if (typeof client !== 'string' || !await isFile(join(root, client))) errors.push('dsh.client requires an exported ./client file')
      else await checkJavaScript(join(root, client), errors)
      if (manifest.dsh.client.platform !== 'web') errors.push('client platform must be web')
      if (!Array.isArray(manifest.dsh.client.inject)) errors.push('client inject must be an array')
    }
  }

  const skillsRoot = join(root, 'skills')
  let skillCount = 0
  try {
    for (const entry of await readdir(skillsRoot, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue
      const skillPath = join(skillsRoot, entry.name, 'SKILL.md')
      if (!await isFile(skillPath)) {
        errors.push(`skill directory is missing SKILL.md: ${entry.name}`)
        continue
      }
      skillCount += 1
      const text = await readFile(skillPath, 'utf8')
      const frontmatter = parseFrontmatter(text)
      if (!frontmatter) errors.push(`invalid frontmatter: skills/${entry.name}/SKILL.md`)
      else {
        if (frontmatter.name !== entry.name) errors.push(`skill name must match its directory: ${entry.name}`)
        if (!NAME.test(frontmatter.name ?? '')) errors.push(`invalid skill name: ${frontmatter.name ?? '<missing>'}`)
        if (!(frontmatter.description ?? '').trim()) errors.push(`skill description is missing: ${entry.name}`)
      }
      if (/^(?:SCAFFOLD_PLACEHOLDER|TODO):/m.test(text)) errors.push(`skill contains an unresolved placeholder: ${entry.name}`)
    }
  } catch (error) {
    if (error.code !== 'ENOENT') errors.push(`cannot inspect skills: ${error.message}`)
  }

  if (errors.length > 0) {
    const error = new Error(errors.map(item => `- ${item}`).join('\n'))
    error.validationErrors = errors
    throw error
  }
  return { root, packageName: manifest.name, version: manifest.version, skillCount, hasClient: Boolean(manifest.dsh?.client) }
}

const invokedDirectly = process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)
if (invokedDirectly) {
  const target = process.argv[2]
  if (!target) {
    console.error('Usage: validate_plugin.mjs <plugin-directory>')
    process.exit(2)
  }
  try {
    const result = await validatePlugin(target)
    console.log(JSON.stringify(result, null, 2))
    console.log('Plugin is valid!')
  } catch (error) {
    console.error(error.message)
    process.exit(1)
  }
}
