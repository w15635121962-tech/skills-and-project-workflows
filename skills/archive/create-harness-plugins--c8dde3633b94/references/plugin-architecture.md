# DeepSeek Harness plugin architecture

## Contents

1. Conceptual model
2. Bundle contract
3. Supported shapes
4. Installation lifecycle
5. Validation and safety

## 1. Conceptual model

Follow the same capability split used by Codex plugins:

```text
Plugin
├── Skills: repeatable instructions and resources
├── Host or MCP capabilities: controlled tools and integrations
└── UI: optional interactive surfaces
```

Start with the smallest shape. Use a Skill when existing model tools are enough. Add Host behavior only for runtime services or tools. Add UI only when the user must inspect, edit, compare, confirm, or navigate structured state.

Harness represents an installable plugin as a Node package whose `package.json` declares a DSH bundle patch. The patch is composed into a profile and mounts Cordis entries. A package can also declare a browser client entry and can register bundled Skill roots.

## 2. Bundle contract

Minimal package:

```text
plugin-name/
├── package.json
├── cordis.patch.yml
└── index.js
```

Required manifest fragment:

```json
{
  "name": "dsh-example",
  "version": "0.1.0",
  "type": "module",
  "main": "index.js",
  "dsh": {
    "bundle": {
      "patch": "./cordis.patch.yml"
    }
  }
}
```

`dsh plugin --profile web add <package>` installs the dependency and reconciles packages with a `dsh.bundle.patch` declaration into `dsh.profile.bundles`. The patch owns the runtime entries; merely adding files to a directory does not activate them.

## 3. Supported shapes

### Skill-only

Add `skills/<skill-name>/SKILL.md` and mount an isolated filesystem provider:

```yaml
- insert:
    - id: example-skills
      name: '@deepseek-ai/dsh-skill-filesystem'
      config:
        providerName: example-bundled
        includeDefaultRoots: false
        customSkillDirs:
          - !!js "process.getBuiltinModule('node:url').fileURLToPath(new URL('skills/', baseUrl))"
```

Use this for repeatable workflows that can rely on existing Harness tools.

### Host

Mount the package entry from the patch:

```yaml
- insert:
    - id: example
      name: dsh-example
```

Export an ESM `apply(ctx, config)` function from `index.js`. Register lifecycle cleanup with Cordis rather than leaving processes, watchers, or timers unmanaged.

### UI

Mount a Host marker and declare `dsh.client` in `package.json`. Export a browser bundle as `client.js`. Keep UI optional and preserve a useful headless result whenever the plugin also exposes tools.

### Full

Combine a mounted Host entry, bundled Skill provider, and client entry. The Skill explains when and how to use the capability; Host code owns runtime behavior; UI owns human interaction. Keep the three responsibilities separate.

### MCP-backed

Treat MCP as a Host capability. Add it only after the user identifies the server, transport, executable or URL, schemas, authentication, and trust boundary. Never invent or silently start an MCP server.

## 4. Installation lifecycle

Personal source root:

```text
${DSH_HOME:-~/.dsh}/plugins/<plugin-name>
```

Install a local checkout:

```bash
dsh plugin --profile web add link:/absolute/path/to/plugin
```

Inspect:

```bash
dsh plugin --profile web list --depth 0
dsh --profile web --dump-config
```

Remove only on explicit request:

```bash
dsh plugin --profile web remove <package-name>
```

Skill files under watched user or project roots can refresh without a restart. New bundles, Host code, and browser client code require a client restart unless a configured HMR chain proves the update was loaded.

## 5. Validation and safety

- Validate identifiers, manifests, entry files, bundle patches, and every bundled Skill.
- Refuse collisions by default; update only with explicit authorization.
- Keep install and publish separate from scaffold and review.
- Treat `cordis.patch.yml`, package lifecycle scripts, Host code, browser code, and MCP commands as executable.
- Do not add credentials to manifests, source, examples, or logs.
- Preserve unrelated profile dependencies and bundle order.
- Static validation is not live verification. Confirm the installed profile and Loader tree after installation.
