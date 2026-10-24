#!/usr/bin/env node
import { access, mkdir, realpath, writeFile } from 'node:fs/promises'
import { constants } from 'node:fs'
import { homedir } from 'node:os'
import { isAbsolute, join, resolve } from 'node:path'

const NAME = /^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$/
const KINDS = new Set(['skill', 'host', 'ui', 'full'])

function fail(message) {
  console.error(`Error: ${message}`)
  process.exit(1)
}

function parseArgs(argv) {
  const [name, ...rest] = argv
  if (!name || name.startsWith('-')) fail('provide a plugin name')
  const options = { name }
  for (let index = 0; index < rest.length; index += 2) {
    const flag = rest[index]
    const value = rest[index + 1]
    if (!flag?.startsWith('--') || value === undefined || value.startsWith('--')) fail(`invalid option near ${flag ?? '<end>'}`)
    options[flag.slice(2)] = value
  }
  return options
}

function quoteYaml(value) {
  return `'${value.replaceAll("'", "''")}'`
}

function titleCase(value) {
  return value.split('-').map(part => part.charAt(0).toUpperCase() + part.slice(1)).join(' ')
}

async function exists(path) {
  try {
    await access(path, constants.F_OK)
    return true
  } catch {
    return false
  }
}

const options = parseArgs(process.argv.slice(2))
const pluginName = options.name
const kind = options.kind ?? 'skill'
const description = options.description
const skillName = options['skill-name'] ?? pluginName
const displayName = options['display-name'] ?? titleCase(pluginName)
const defaultRoot = join(process.env.DSH_HOME ?? join(homedir(), '.dsh'), 'plugins')
const requestedOutputRoot = resolve(options.output ?? defaultRoot)

if (!NAME.test(pluginName)) fail('plugin name must use lowercase letters, digits, and hyphens and be at most 64 characters')
if (!KINDS.has(kind)) fail(`kind must be one of: ${[...KINDS].join(', ')}`)
if (!description?.trim()) fail('provide --description')
if ((kind === 'skill' || kind === 'full') && !NAME.test(skillName)) fail('skill name must use lowercase letters, digits, and hyphens')
if (!isAbsolute(requestedOutputRoot)) fail('output root must resolve to an absolute path')

await mkdir(requestedOutputRoot, { recursive: true })
const outputRoot = await realpath(requestedOutputRoot)
const pluginRoot = join(outputRoot, pluginName)
if (await exists(pluginRoot)) fail(`target already exists: ${pluginRoot}`)

const packageName = pluginName.startsWith('dsh-') ? pluginName : `dsh-${pluginName}`
const withSkill = kind === 'skill' || kind === 'full'
const withClient = kind === 'ui' || kind === 'full'
const files = ['index.js', 'cordis.patch.yml', ...(withSkill ? ['skills'] : []), ...(withClient ? ['client.js'] : [])]
const manifest = {
  name: packageName,
  version: '0.1.0',
  description,
  type: 'module',
  main: 'index.js',
  exports: {
    '.': './index.js',
    ...(withClient ? { './client': './client.js' } : {}),
    './package.json': './package.json',
  },
  files,
  dsh: {
    bundle: { patch: './cordis.patch.yml' },
    ...(withClient ? { client: { inject: [], platform: 'web', immediately: true } } : {}),
  },
  license: 'UNLICENSED',
}

const patchRows = [
  `    - id: ${pluginName}`,
  `      name: ${packageName}`,
]
if (withSkill) {
  patchRows.push(
    `    - id: ${pluginName}-skills`,
    `      name: '@deepseek-ai/dsh-skill-filesystem'`,
    '      config:',
    `        providerName: ${pluginName}-bundled`,
    '        includeDefaultRoots: false',
    '        customSkillDirs:',
    `          - !!js "process.getBuiltinModule('node:url').fileURLToPath(new URL('node_modules/${packageName}/skills/', baseUrl))"`,
  )
}

const host = `export const name = ${JSON.stringify(`${pluginName}-host`)}\n\nexport function apply(ctx) {\n  ctx.effect(() => () => {}, ${JSON.stringify(`${pluginName}: lifecycle`)})\n}\n`
const client = `window.__ModuleLoader__.load({\n  id: ${JSON.stringify(`${pluginName}-client`)},\n  factory: () => {\n    const module = { exports: {} }\n    const exports = module.exports\n    const name = ${JSON.stringify(`${pluginName}-client`)}\n    const inject = []\n\n    function apply(ctx) {\n      document.documentElement.dataset[${JSON.stringify(pluginName.replaceAll('-', '_'))}] = 'active'\n      ctx.effect(() => () => {\n        delete document.documentElement.dataset[${JSON.stringify(pluginName.replaceAll('-', '_'))}]\n      }, ${JSON.stringify(`${pluginName}: client marker`)})\n    }\n\n    Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' })\n    exports.name = name\n    exports.inject = inject\n    exports.apply = apply\n    return module.exports\n  },\n})\n`

await mkdir(pluginRoot, { recursive: false })
await writeFile(join(pluginRoot, 'package.json'), `${JSON.stringify(manifest, null, 2)}\n`)
await writeFile(join(pluginRoot, 'index.js'), host)
await writeFile(join(pluginRoot, 'cordis.patch.yml'), `- insert:\n${patchRows.join('\n')}\n`)

if (withClient) await writeFile(join(pluginRoot, 'client.js'), client)
if (withSkill) {
  const skillRoot = join(pluginRoot, 'skills', skillName)
  await mkdir(skillRoot, { recursive: true })
  const skill = `---\nname: ${skillName}\ndescription: ${quoteYaml(description)}\n---\n\n# ${displayName}\n\nSCAFFOLD_PLACEHOLDER: Replace this line with concise, task-specific instructions and add only required resources.\n`
  await writeFile(join(skillRoot, 'SKILL.md'), skill)
}

console.log(`Created ${kind} plugin: ${pluginRoot}`)
console.log(`Package: ${packageName}`)
console.log('Next: replace SCAFFOLD_PLACEHOLDER, implement requested behavior, then validate.')
