#!/usr/bin/env python3
"""Restore supplied complete plugin roots and register them with the Codex CLI.

This script never invokes plugin code, hooks, dependency installers, or auth flows.
"""
import json
from pathlib import Path
import shutil
import subprocess
import time

SOURCE = Path('/Users/zc/.codex/skill-imports/20261019-094923/skills-export-20261019/payload')
DEST = Path('/Users/zc/.codex/plugins/import-20261019')
REPORT = Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕/技能与插件安装_20261019')
MARKET = 'import-20261019'
SCOPES = ['codex/.tmp/plugins', 'codex/.tmp/bundled-marketplaces',
          'codex/plugins/cache', 'claude/plugins/marketplaces', 'codex/skills']

def cli(*args):
    p = subprocess.run(['codex', 'plugin', *args], text=True, capture_output=True)
    return {'args': list(args), 'returncode': p.returncode,
            'stdout': p.stdout, 'stderr': p.stderr}

def save(name, data):
    (REPORT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

REPORT.mkdir(parents=True, exist_ok=True)
before = cli('list', '--json')
if before['returncode']:
    save('plugin-before-error.json', before)
    raise SystemExit('Cannot read current native plugin state')
live = json.loads(before['stdout'])['installed']
save('plugins-before.json', live)
installed = {p['name'] for p in live}
roots = {}
for scope in SCOPES:
    for manifest in sorted((SOURCE / scope).rglob('plugin.json')):
        if manifest.parent.name not in ('.codex-plugin', '.claude-plugin'):
            continue
        if any(part in ('fixtures', 'assets') for part in manifest.parts):
            continue
        data = json.loads(manifest.read_text())
        name = data['name']
        root = manifest.parent.parent
        roots.setdefault(name, {})[str(root)] = data

plan = []
for name, sources in sorted(roots.items()):
    if name in installed:
        plan.append({'name': name, 'action': 'preserve-existing',
                     'existing': [p for p in live if p['name'] == name],
                     'supplied_roots': list(sources)})
    else:
        source = Path(next(iter(sources)))
        plan.append({'name': name, 'action': 'install-native',
                     'source': str(source), 'destination': str(DEST / 'plugins' / name)})
save('plugin-import-plan.json', plan)
assert len(roots) == 108, len(roots)
assert sum(p['action'] == 'install-native' for p in plan) == 85

entries = []
adaptations = []
for item in plan:
    if item['action'] != 'install-native':
        continue
    name = item['name']
    source, target = Path(item['source']), Path(item['destination'])
    if not target.exists():
        shutil.copytree(source, target, symlinks=True)
    native = target / '.codex-plugin' / 'plugin.json'
    if not native.exists():
        original = target / '.claude-plugin' / 'plugin.json'
        data = json.loads(original.read_text())
        data.setdefault('version', '0.0.0+import.20261019')
        data['skills'] = './skills/' if (target / 'skills').is_dir() else './'
        # Claude lifecycle events and variable substitution are not Codex hooks.
        # Keep the original hooks/scripts as supplied, with no native event hooks.
        data['hooks'] = {'hooks': {}}
        if (target / '.mcp.json').exists():
            mcp_path = target / '.mcp.json'
            mcp = json.loads(mcp_path.read_text())
            for server in mcp.get('mcpServers', {}).values():
                if isinstance(server, dict):
                    if 'args' in server:
                        server['args'] = [a.replace('${CLAUDE_PLUGIN_ROOT}', '.') if isinstance(a, str) else a
                                          for a in server['args']]
                    if server.get('command'):
                        server.setdefault('cwd', '.')
            # Keep the source MCP config for audit and future Claude use.
            (target / '.mcp.claude-source.json').write_text(mcp_path.read_text())
            mcp_path.write_text(json.dumps(mcp, ensure_ascii=False, indent=2) + '\n')
            data['mcpServers'] = './.mcp.json'
        native.parent.mkdir(parents=True, exist_ok=True)
        native.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        adaptations.append({'name': name, 'adaptation': 'Codex manifest mirror, native skills, no native lifecycle hooks',
                            'mcp_cwd_ported': (target / '.mcp.claude-source.json').exists()})
    entries.append({'name': name, 'source': {'source': 'local', 'path': './plugins/' + name},
                    'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_USE'}})

marketplace = DEST / '.agents' / 'plugins' / 'marketplace.json'
marketplace.parent.mkdir(parents=True, exist_ok=True)
marketplace.write_text(json.dumps({'name': MARKET, 'plugins': entries}, ensure_ascii=False, indent=2) + '\n')
save('plugin-manifest-adaptations.json', adaptations)
registered = cli('marketplace', 'add', str(DEST), '--json')
save('plugin-marketplace-registration.json', registered)
print('Marketplace registration:', registered['returncode'], flush=True)
if registered['returncode']:
    print(registered['stderr'] or registered['stdout'], flush=True)
    raise SystemExit(registered['returncode'])

results = []
for i, entry in enumerate(entries, 1):
    name = entry['name']
    result = cli('add', name + '@' + MARKET, '--json')
    result['name'] = name
    result['timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    results.append(result)
    with (REPORT / 'plugin-install-results.jsonl').open('a') as f:
        f.write(json.dumps(result, ensure_ascii=False) + '\n')
    print('%d/%d %s: %s' % (i, len(entries), name, 'OK' if result['returncode'] == 0 else 'FAILED'), flush=True)
    if result['returncode']:
        print((result['stderr'] or result['stdout'])[:1200], flush=True)

after = cli('list', '--json')
save('plugin-after-cli-result.json', after)
current = json.loads(after['stdout']) if after['returncode'] == 0 else {}
save('plugins-after.json', current)
current_by_name = {p['name']: p for p in current.get('installed', []) if p.get('installed') and p.get('enabled')}
summary = {'supplied_unique_plugin_names': len(roots), 'preserved_existing_supplied_names': len(set(roots) & installed),
           'attempted_native_installs': len(entries), 'successful_add_commands': sum(r['returncode'] == 0 for r in results),
           'failed_add_commands': [r['name'] for r in results if r['returncode']],
           'supplied_installed_and_enabled': sorted(set(roots) & set(current_by_name)),
           'supplied_not_installed_and_enabled': sorted(set(roots) - set(current_by_name)),
           'all_native_installed_count': len(current.get('installed', [])),
           'marketplace': str(DEST)}
save('plugin-install-summary.json', summary)
print('SUMMARY', json.dumps({k:v for k,v in summary.items() if not isinstance(v,list)},ensure_ascii=False), flush=True)
print('Unresolved:', summary['supplied_not_installed_and_enabled'], flush=True)
