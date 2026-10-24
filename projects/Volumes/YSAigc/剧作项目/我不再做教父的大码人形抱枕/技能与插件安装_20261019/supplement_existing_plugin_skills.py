#!/usr/bin/env python3
"""Add missing supplied skills/resources without overwriting current plugin files."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

REPORT = Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕/技能与插件安装_20261019')
STABLE = Path('/Users/zc/.codex/plugins/import-20261019/supplements')
plan = json.loads((REPORT / 'plugin-import-plan.json').read_text())
live = json.loads(subprocess.run(['codex', 'plugin', 'list', '--json'], capture_output=True, text=True, check=True).stdout)['installed']
byname = {p['name']: p for p in live}

def manifest(root):
    for n in ['.codex-plugin/plugin.json', '.claude-plugin/plugin.json']:
        if (root / n).is_file():
            return json.loads((root / n).read_text())
    return {}

def skillpaths(root):
    value = manifest(root).get('skills', './skills')
    values = value if isinstance(value, list) else [value]
    files = []
    for val in values:
        if not isinstance(val, str):
            continue
        directory = root / val
        if directory.is_file() and directory.name == 'SKILL.md':
            files.append(directory)
        elif directory.is_dir():
            files += [p for p in directory.rglob('SKILL.md')
                      if not any(part in ('fixtures', 'assets', 'templates')
                                 for part in p.relative_to(directory).parts)]
    return sorted(set(files))

def versionkey(root):
    value = manifest(root).get('version', '0')
    return tuple(int(x) for x in re.findall(r'\d+', value))

results = []
for item in plan:
    if item['action'] != 'preserve-existing':
        continue
    name = item['name']
    current = byname[name]
    cache = Path('/Users/zc/.codex/plugins/cache') / current['marketplaceName'] / name / current['version']
    supplied = sorted([Path(p) for p in item['supplied_roots']], key=versionkey, reverse=True)
    newest_supplied = supplied[0]
    expected = {str(p.relative_to(newest_supplied)) for p in skillpaths(newest_supplied)}
    present_before = {str(p.relative_to(cache)) for p in skillpaths(cache)}
    missing_before = expected - present_before
    row = {'name': name, 'current_version': current['version'], 'native_cache': str(cache),
           'selected_supplied_source': str(newest_supplied), 'supplied_version': manifest(newest_supplied).get('version'),
           'expected_supplied_skill_count': len(expected), 'live_skill_count_before': len(present_before),
           'missing_before': sorted(missing_before), 'copied_files': [], 'preserved_existing_conflicts': []}
    if missing_before:
        source = newest_supplied
        current_source_path = current.get('source', {}).get('path')
        if current_source_path:
            current_source = Path(current_source_path)
            current_skills = {str(p.relative_to(current_source)) for p in skillpaths(current_source)}
            if current_source != cache and missing_before.issubset(current_skills):
                source = current_source
        stable = STABLE / name
        if not stable.exists():
            shutil.copytree(source, stable, symlinks=True)
        row['supplement_source'] = str(source)
        row['stable_full_source'] = str(stable)
        for file in source.rglob('*'):
            if not file.is_file():
                continue
            rel = file.relative_to(source)
            destination = cache / rel
            if destination.exists():
                if hashlib.sha256(destination.read_bytes()).digest() != hashlib.sha256(file.read_bytes()).digest():
                    row['preserved_existing_conflicts'].append(str(rel))
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, destination)
            row['copied_files'].append(str(rel))
        # For configured local sources, also preserve additions in the original
        # source so a same-version cache rebuild keeps the restored skills.
        if current_source_path and Path(current_source_path) == cache:
            row['configured_source_is_native_cache'] = True
    present_after = {str(p.relative_to(cache)) for p in skillpaths(cache)}
    row['live_skill_count_after'] = len(present_after)
    row['missing_after'] = sorted(expected - present_after)
    results.append(row)

(REPORT / 'existing-plugin-skill-supplements.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
summary = {'existing_supplied_plugins_audited': len(results),
           'plugins_with_missing_skills_supplemented': sum(bool(r['missing_before']) for r in results),
           'missing_skills_restored': sum(len(r['missing_before']) for r in results),
           'files_added_without_overwrite': sum(len(r['copied_files']) for r in results),
           'remaining_missing_supplied_skill_files': sum(len(r['missing_after']) for r in results),
           'existing_supplied_plugin_skill_files_after': sum(r['live_skill_count_after'] for r in results),
           'note': 'Counts follow each native manifest skills directory, excluding fixture/template/asset SKILL.md examples. External service usability was not tested.'}
(REPORT / 'existing-plugin-skill-supplement-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(summary, ensure_ascii=False, indent=2))
