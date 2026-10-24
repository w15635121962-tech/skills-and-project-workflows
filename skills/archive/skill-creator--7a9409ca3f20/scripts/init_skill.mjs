#!/usr/bin/env node

import { access, chmod, mkdir, rm, writeFile } from 'node:fs/promises'
import { constants } from 'node:fs'
import { homedir } from 'node:os'
import { basename, join, resolve } from 'node:path'

const SKILL_NAME = /^[a-z0-9][a-z0-9-]{0,62}[a-z0-9]$|^[a-z0-9]$/
const RESOURCE_NAMES = new Set(['scripts', 'references', 'assets'])

function fail(message) {
  process.stderr.write(`init_skill: ${message}\n`)
  process.exitCode = 1
}

function normalizeName(value) {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/-{2,}/g, '-')
    .replace(/^-|-$/g, '')
}

function titleFromName(name) {
  return name.split('-').map(part => part.charAt(0).toUpperCase() + part.slice(1)).join(' ')
}

function yamlString(value) {
  return JSON.stringify(value)
}

function truncate(value, max) {
  if (value.length <= max) return value
  return `${value.slice(0, max - 1).trimEnd()}…`
}

function parseArgs(argv) {
  const options = {
    path: join(process.env.DSH_HOME ?? join(homedir(), '.dsh'), 'skills'),
    resources: [],
    explicitOnly: false,
  }
  const positional = []
  const valueFlags = new Map([
    ['--path', 'path'],
    ['--resources', 'resourcesText'],
    ['--description', 'description'],
    ['--display-name', 'displayName'],
    ['--short-description', 'shortDescription'],
    ['--default-prompt', 'defaultPrompt'],
    ['--body', 'body'],
  ])

  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index]
    if (argument === '--explicit-only') {
      options.explicitOnly = true
      continue
    }
    const field = valueFlags.get(argument)
    if (field !== undefined) {
      const value = argv[index + 1]
      if (value === undefined || value.startsWith('--')) {
        throw new Error(`${argument} requires a value`)
      }
      options[field] = value
      index += 1
      continue
    }
    if (argument.startsWith('--')) throw new Error(`unknown option ${argument}`)
    positional.push(argument)
  }

  if (positional.length !== 1) {
    throw new Error('usage: init_skill.mjs <skill-name> [--path ROOT] [--description TEXT] [--resources scripts,references,assets]')
  }
  if (options.resourcesText !== undefined) {
    const resources = options.resourcesText.split(',').map(value => value.trim()).filter(Boolean)
    for (const resource of resources) {
      if (!RESOURCE_NAMES.has(resource)) throw new Error(`unsupported resource directory ${JSON.stringify(resource)}`)
    }
    options.resources = [...new Set(resources)]
  }
  return { requestedName: positional[0], options }
}

function skillMarkdown(name, displayName, description, body) {
  const instructions = body?.trim() || 'TODO: Replace this placeholder with concise imperative workflow instructions before validation.'
  return `---\nname: ${name}\ndescription: ${yamlString(description)}\n---\n\n# ${displayName}\n\n${instructions}\n`
}

function openAiYaml(name, displayName, shortDescription, defaultPrompt, explicitOnly) {
  return `interface:\n  display_name: ${yamlString(displayName)}\n  short_description: ${yamlString(shortDescription)}\n  default_prompt: ${yamlString(defaultPrompt)}\npolicy:\n  allow_implicit_invocation: ${explicitOnly ? 'false' : 'true'}\n`
}

async function exists(path) {
  try {
    await access(path, constants.F_OK)
    return true
  } catch {
    return false
  }
}

async function main() {
  let parsed
  try {
    parsed = parseArgs(process.argv.slice(2))
  } catch (error) {
    fail(error instanceof Error ? error.message : String(error))
    return
  }

  const name = normalizeName(parsed.requestedName)
  if (!SKILL_NAME.test(name) || name.length > 64) {
    fail(`skill name ${JSON.stringify(parsed.requestedName)} cannot be normalized to lowercase kebab-case under 64 characters`)
    return
  }

  const { options } = parsed
  const root = resolve(options.path)
  const target = join(root, name)
  if (basename(target) !== name) {
    fail('resolved target does not match the normalized skill name')
    return
  }
  if (await exists(target)) {
    fail(`target already exists: ${target}`)
    return
  }

  const displayName = options.displayName?.trim() || titleFromName(name)
  const description = options.description?.trim() || 'TODO: Describe what this Skill does, when it should trigger, and when it should not trigger.'
  const shortDescription = options.shortDescription?.trim() || truncate(description, 64)
  const defaultPrompt = options.defaultPrompt?.trim() || `Use $${name} to complete the requested workflow.`

  if (description.length > 500) {
    fail('description must be 500 characters or fewer for the Harness catalog')
    return
  }
  if (shortDescription.length < 25 || shortDescription.length > 64) {
    fail('short description must contain 25 to 64 characters')
    return
  }
  if (!defaultPrompt.includes(`$${name}`)) {
    fail(`default prompt must mention $${name}`)
    return
  }

  let created = false
  try {
    await mkdir(root, { recursive: true, mode: 0o700 })
    await mkdir(target, { mode: 0o700 })
    created = true
    await mkdir(join(target, 'agents'), { mode: 0o700 })
    for (const resource of options.resources) await mkdir(join(target, resource), { mode: 0o700 })

    await writeFile(
      join(target, 'SKILL.md'),
      skillMarkdown(name, displayName, description, options.body),
      { encoding: 'utf8', mode: 0o600, flag: 'wx' },
    )
    await writeFile(
      join(target, 'agents', 'openai.yaml'),
      openAiYaml(name, displayName, shortDescription, defaultPrompt, options.explicitOnly),
      { encoding: 'utf8', mode: 0o600, flag: 'wx' },
    )
    await chmod(target, 0o700)
  } catch (error) {
    if (created) await rm(target, { recursive: true, force: true })
    fail(`cannot create skill: ${error instanceof Error ? error.message : String(error)}`)
    return
  }

  process.stdout.write(`Created skill: ${target}\n`)
  process.stdout.write(`Trigger: $${name}\n`)
  process.stdout.write(`Next: edit SKILL.md and run quick_validate.mjs ${JSON.stringify(target)}\n`)
}

await main()
