import argparse
import importlib
import os
from datetime import datetime

from core import *


def _getYamlModule():
    try:
        return importlib.import_module('yaml')
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            'PyYAML is required. Please install it first: pip install pyyaml'
        )


def _typeStr2Value(typeStr):
    if typeStr in PROJECT_TYPESTR:
        return PROJECT_TYPESTR.index(typeStr)
    return None


def _normalizePathForWindows(path):
    if os.name == 'nt' and isinstance(path, str) and len(path) == 2 and path[1] == ':':
        return path + '\\'
    return path


def buildMigrationManifest(prjMgr, repoPath, destinationRoot=''):
    """Build a migration manifest template."""
    manifest = {
        'version': 1,
        'generated_at': datetime.now().isoformat(timespec='seconds'),
        'repo_path': os.path.abspath(repoPath),
        'destination_root': destinationRoot,
        'backup_before_copy': False,
        'backup_root': '',
        'copy_options': {
            'copy_project': True,
            'copy_event': True,
            'copy_ext': True,
            'copy_temp': False,
            'include_config': True,
            'overwrite': False,
            'keep_type_dir': True,
            'save_cfg_before_backup': True,
        },
        'selected_projects': []
    }

    for item in prjMgr.listProjects():
        manifest['selected_projects'].append({
            'name': item['name'],
            'type': item['typeStr'],
            'copy': False,
        })
    return manifest


def generateManifest(repoPath, outputPath, destinationRoot=''):
    yaml = _getYamlModule()
    prjMgr = ProjectMgr(repoPath)
    manifest = buildMigrationManifest(prjMgr, repoPath, destinationRoot=destinationRoot)
    with open(outputPath, 'w', encoding='utf-8') as file:
        yaml.safe_dump(manifest, file, allow_unicode=True, sort_keys=False)
    print('Manifest generated: {0}'.format(os.path.abspath(outputPath)))


def executeCopy(manifestPath):
    yaml = _getYamlModule()
    with open(manifestPath, 'r', encoding='utf-8') as file:
        manifest = yaml.safe_load(file)

    repoPath = manifest.get('repo_path')
    destinationRoot = _normalizePathForWindows(manifest.get('destination_root'))
    if not repoPath or not destinationRoot:
        raise ValueError('manifest.repo_path and manifest.destination_root are required.')

    selectedProjects = []
    for item in manifest.get('selected_projects', []):
        if item.get('copy', False):
            selectedProjects.append({
                'name': item.get('name'),
                'type': _typeStr2Value(item.get('type'))
            })

    if len(selectedProjects) == 0:
        print('No projects selected. Set selected_projects[*].copy = true in manifest.')
        return

    copyOpt = manifest.get('copy_options', {})
    backupBeforeCopy = manifest.get('backup_before_copy', False)
    backupRoot = _normalizePathForWindows(manifest.get('backup_root'))

    prjMgr = ProjectMgr(repoPath)
    results = prjMgr.copySelectedProjects(
        destinationRoot=destinationRoot,
        selections=selectedProjects,
        copyProject=copyOpt.get('copy_project', True),
        copyEvent=copyOpt.get('copy_event', True),
        copyExt=copyOpt.get('copy_ext', True),
        copyTemp=copyOpt.get('copy_temp', False),
        includeConfig=copyOpt.get('include_config', True),
        overwrite=copyOpt.get('overwrite', False),
        backupBeforeCopy=backupBeforeCopy,
        backupPath=backupRoot,
        saveCfg=copyOpt.get('save_cfg_before_backup', True),
        keepTypeDir=copyOpt.get('keep_type_dir', True),
    )

    print('Copy completed.')
    print('Copied: {0}'.format(len(results['copied'])))
    print('Failed: {0}'.format(len(results['failed'])))
    if len(results['backups']) > 0:
        print('Backups: {0}'.format(len(results['backups'])))

    for failed in results['failed']:
        print('  - {0}: {1}'.format(failed['name'], failed['reason']))


def main():
    parser = argparse.ArgumentParser(description='ProjectKeeper utility')
    subparsers = parser.add_subparsers(dest='command')

    parserManifest = subparsers.add_parser('generate-manifest', help='Generate migration manifest yaml')
    parserManifest.add_argument('--repo', required=True, help='Project repository path')
    parserManifest.add_argument('--output', default='migration_manifest.yaml', help='Manifest output path')
    parserManifest.add_argument('--dest', default='', help='Destination root for copied projects')

    parserCopy = subparsers.add_parser('copy', help='Copy projects using manifest yaml')
    parserCopy.add_argument('--manifest', default='migration_manifest.yaml', help='Manifest path')

    args = parser.parse_args()

    if args.command == 'generate-manifest':
        generateManifest(args.repo, args.output, destinationRoot=args.dest)
    elif args.command == 'copy':
        executeCopy(args.manifest)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
