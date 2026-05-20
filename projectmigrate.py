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
    if typeStr in SFTR_PROJECT_DIR:
        return SFTR_PROJECT_DIR.index(typeStr)
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
        'repo_copy_options': {
            'copy_playeros': False,
        },
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
            'type': item['typeDir'],
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

    copyOpt = manifest.get('copy_options', {})
    repoCopyOpt = manifest.get('repo_copy_options', {})
    backupBeforeCopy = manifest.get('backup_before_copy', False)
    backupRoot = _normalizePathForWindows(manifest.get('backup_root'))
    copiedRepoFolders = []
    failedRepoFolders = []

    if len(selectedProjects) == 0 and (not repoCopyOpt.get('copy_playeros', False)):
        print('No items selected. Set selected_projects[*].copy = true or enable repo_copy_options.copy_playeros.')
        return

    print('Manifest: {0}'.format(os.path.abspath(manifestPath)))
    print('Repo: {0}'.format(os.path.abspath(repoPath)))
    print('Destination: {0}'.format(destinationRoot))
    print('Projects selected: {0}'.format(len(selectedProjects)))
    if repoCopyOpt.get('copy_playeros', False):
        print('Repo folders selected: {0}'.format(SFTR_PLAYEROS_DIR))

    prjMgr = ProjectMgr(repoPath)
    if len(selectedProjects) > 0:
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
            verbose=True,
        )
    else:
        results = {
            'copied': [],
            'failed': [],
            'backups': []
        }

    if repoCopyOpt.get('copy_playeros', False):
        try:
            copiedRepoFolders.append(
                prjMgr.copyRepoFolder(
                    SFTR_PLAYEROS_DIR,
                    destinationRoot,
                    overwrite=copyOpt.get('overwrite', False),
                    verbose=True,
                )
            )
        except Exception as ex:
            failedRepoFolders.append({
                'name': SFTR_PLAYEROS_DIR,
                'reason': str(ex)
            })
            print('[repo] {0}'.format(SFTR_PLAYEROS_DIR))
            print('  ✗ Failed: {0}'.format(ex))

    print('Copy completed.')
    print('Copied: {0}'.format(len(results['copied'])))
    print('Failed: {0}'.format(len(results['failed'])))
    if len(copiedRepoFolders) > 0:
        print('Repo folders copied: {0}'.format(len(copiedRepoFolders)))
    if len(failedRepoFolders) > 0:
        print('Repo folders failed: {0}'.format(len(failedRepoFolders)))
    if len(results['backups']) > 0:
        print('Backups: {0}'.format(len(results['backups'])))

    for failed in results['failed']:
        print('  - {0}: {1}'.format(failed['name'], failed['reason']))
    for failed in failedRepoFolders:
        print('  - repo/{0}: {1}'.format(failed['name'], failed['reason']))


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
