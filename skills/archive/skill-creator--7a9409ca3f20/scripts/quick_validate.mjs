#!/usr/bin/env node

import { readFile, readdir, stat } from 'node:fs/promises'
import { basename, join, resolve } from 'node:path'

const SKILL_NAME = /^[a-z0-9][a-z0-9-]{0,62}[a-z0-9]$|^[a-z0-9]$/
const ALLOWED_FRONTMATTER = new Set(['name', 'description'])
const FORBIDDEN_TOP_LEVEL = /^(readme|changelog|installation[_-]?guide|quick[_-]?reference)(\.|$)/i

function unquote(value) {
  const trimmed = value.trim()
  if (trimmed.startsWith('"')) {
    try {
      const parsed = JSON.parse(trimmed)
      return typeof parsed === 'string' ? parsed : undefined
    } catch {
      return undefined
    }
  }
  if (trimmed.startsWith("'") && trimmed.endsWith("'")) {
    return trimmed.slice(1, -1).replace(/''/g, "'")
  }
  return trimmed
}

function parseFrontmatter(source, errors) {
  const match = source.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/)
  if (match === null) {
    errors.push('SKILL.md must begin with YAML frontmatter enclosed by --- lines')
    return undefined
  }
  const values = new Map()
  for (const [index, line] of match[1].split(/\r?\n/).entries()) {
    if (line.trim() === '' || line.trimStart().startsWith('#')) continue
    const field = line.match(/^([a-zA-Z0-9_-]+):\s*(.*)$/)
    if (field === null) {
      errors.push(`frontmatter line ${index + 2} is not a simple key: value field`)
      continue
    }
    const [, key, raw] = field
    if (values.has(key)) errors.push(`frontmatter field ${key} is duplicated`)
    if (!ALLOWED_FRONTMATTER.has(key)) errors.push(`frontmatter field ${key} is not allowed; keep only name and description`)
    const value = unquote(raw)
    if (value === undefined) errors.push(`frontmatter field ${key} has invalid quoting`)
    else values.set(key, value)
  }
  return { values, body: source.slice(match[0].length) }
}

function yamlField(source, name) {
  const match = source.match(new RegExp(`^\\s*${name}:\\s*(.+)\\s*$`, 'm'))
  return match === null ? undefined : unquote(match[1])
}

async function main() {
  const argument = process.argv[2]
  if (argument === undefined || process.argv.length !== 3) {
    process.stderr.write('usage: quick_validate.mjs <skill-folder>\n')
    process.exitCode = 2
    return
  }

  const folder = resolve(argument)
  const errors = []
  let info
  try {
    info = await stat(folder)
  } catch (error) {
    process.stderr.write(`Validation failed:\n- cannot access ${folder}: ${error instanceof Error ? error.message : String(error)}\n`)
    process.exitCode = 1
    return
  }
  if (!info.isDirectory()) errors.push('target must be a Skill directory')

  let source = ''
  try {
    source = await readFile(join(folder, 'SKILL.md'), 'utf8')
  } catch (error) {
    errors.push(`cannot read SKILL.md: ${error instanceof Error ? error.message : String(error)}`)
  }

  const parsed = source === '' ? undefined : parseFrontmatter(source, errors)
  if (parsed !== undefined) {
    const name = parsed.values.get('name')
    const description = parsed.values.get('description')
    if (name === undefined || name === '') errors.push('frontmatter name is required')
    else {
      if (!SKILL_NAME.test(name) || name.length > 64) errors.push('name must be lowercase kebab-case and at most 64 characters')
      if (basename(folder) !== name) errors.push(`folder name ${JSON.stringify(basename(folder))} must equal skill name ${JSON.stringify(name)}`)
    }
    if (description === undefined || description.trim() === '') errors.push('frontmatter description is required')
    else {
      if (description.length > 500) errors.push('description must be 500 characters or fewer')
      if (/^TODO:|\[TODO/i.test(description)) errors.push('replace the description placeholder')
    }
    if (parsed.body.trim() === '') errors.push('SKILL.md body must contain workflow instructions')
    if (/TODO: Replace this placeholder|\[TODO/i.test(parsed.body)) errors.push('replace every scaffold placeholder in SKILL.md')

    try {
      const uiSource = await readFile(join(folder, 'agents', 'openai.yaml'), 'utf8')
      const displayName = yamlField(uiSource, 'display_name')
      const shortDescription = yamlField(uiSource, 'short_description')
      const defaultPrompt = yamlField(uiSource, 'default_prompt')
      if (displayName === undefined || displayName.trim() === '') errors.push('agents/openai.yaml needs interface.display_name')
      if (shortDescription === undefined || shortDescription.length < 25 || shortDescription.length > 64) {
        errors.push('agents/openai.yaml short_description must contain 25 to 64 characters')
      }
      if (name !== undefined && (defaultPrompt === undefined || !defaultPrompt.includes(`$${name}`))) {
        errors.push(`agents/openai.yaml default_prompt must mention $${name}`)
      }
    } catch (error) {
      if (error?.code !== 'ENOENT') errors.push(`cannot read agents/openai.yaml: ${error instanceof Error ? error.message : String(error)}`)
    }
  }

  try {
    for (const entry of await readdir(folder, { withFileTypes: true })) {
      if (entry.isFile() && FORBIDDEN_TOP_LEVEL.test(entry.name)) {
        errors.push(`remove extraneous top-level file ${entry.name}`)
      }
    }
  } catch {
    // The earlier directory check owns the useful diagnostic.
  }

  if (errors.length > 0) {
    process.stderr.write(`Validation failed:\n${errors.map(error => `- ${error}`).join('\n')}\n`)
    process.exitCode = 1
    return
  }
  process.stdout.write('Skill is valid!\n')
}

await main()
