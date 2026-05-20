# Project Migration

`projectmigrate.py` is used to copy selected projects from one ProjectKeeper repository to a new location.

The migration flow is:

1. Generate a manifest YAML file.
2. Edit the manifest to choose which projects to copy.
3. Configure copy options.
4. Optionally back up each project before copying.
5. Execute the copy task and watch the progress output.

## Prerequisites

- Python environment with `PyYAML` installed:

 ```terminal
 pip install pyyaml
 ```

- A valid ProjectKeeper repository path.
- A writable destination path.

For Windows network destinations, prefer a UNC path such as `\\server\share\ProjectMigration`.

Mapped drive letters such as `Z:\` work only if that drive is mapped in the same terminal session that runs Python.

## Basic Usage

### 1. Generate a manifest

```terminal
python projectmigrate.py generate-manifest --repo "D:\SFTR" --output migration_manifest.yaml --dest "\\server\share\ProjectMigration"
```

This scans the repository and writes a manifest containing all discovered projects with `copy: false` by default.

### 2. Edit the manifest

Open `migration_manifest.yaml` and:

- set `selected_projects[*].copy` to `true` for the projects you want to migrate
- set `destination_root`
- set copy options
- optionally enable backup before copy

### 3. Execute migration

```terminal
python projectmigrate.py copy --manifest migration_manifest.yaml
```

The script prints:

- manifest path
- repository path
- destination path
- selected project count
- per-project progress
- backup progress if enabled
- final copied / failed / backup totals

## Example Manifest

```yaml
version: 1
generated_at: '2026-05-20T10:30:00'
repo_path: 'D:\SFTR'
destination_root: '\\server\share\ProjectMigration'
backup_before_copy: true
backup_root: 'D:\SFTR\PlayerOS\6 Backup\Backup'
copy_options:
 copy_project: true
 copy_event: true
 copy_ext: true
 copy_temp: false
 include_config: true
 overwrite: false
 keep_type_dir: true
 save_cfg_before_backup: true
selected_projects:
 - name: MasterThesis
  type: 2 Project
  copy: true
 - name: RCAMC实验室事务
  type: 3 Work
  copy: true
 - name: MX61001_新时代中特
  type: 1 Course
  copy: false
```

## Manifest Fields

### Top-level fields

- `version`
 	- manifest schema version

- `generated_at`
 	- manifest generation time

- `repo_path`
 	- source ProjectKeeper repository root

- `destination_root`
 	- root directory where copied projects will be written
 	- if `keep_type_dir: true`, project type folders are created under this root

- `backup_before_copy`
 	- whether to run ProjectKeeper backup before migration copy

- `backup_root`
 	- backup destination root
 	- required when `backup_before_copy: true`

### `copy_options`

- `copy_project`
 	- copy common project files and folders
 	- excludes `_Temp`, `_Extension Package`, and `_Event Records`

- `copy_event`
 	- copy `_Event Records`

- `copy_ext`
 	- copy `_Extension Package`

- `copy_temp`
 	- copy `_Temp`

- `include_config`
 	- copy `.projectcfg`
 	- if the project is legacy, `_CacheInfo` is copied instead

- `overwrite`
 	- allow copy into an existing destination project directory
 	- when `false`, an existing destination project folder causes that project to fail

- `keep_type_dir`
 	- preserve project type folders under `destination_root`
 	- examples: `1 Course`, `2 Project`, `3 Work`

- `save_cfg_before_backup`
 	- passed to backup logic before migration copy
 	- useful when backup is enabled

### `selected_projects`

Each entry has:

- `name`
 	- project name

- `type`
 	- project type folder name
 	- use folder names from `SFTR_PROJECT_DIR`, not display names
 	- examples:
  		- `1 Course`
  		- `2 Project`
  		- `3 Work`
  		- `4 Daily Life`
  		- `5 Recreation`
 	- `Other` may appear for projects outside the standard SFTR folders

- `copy`
 	- `true` means this project will be migrated
 	- `false` means ignored

## Destination Layout

If `keep_type_dir: true` and `destination_root` is:

```text
\\server\share\ProjectMigration
```

then a copied project may be written to:

```text
\\server\share\ProjectMigration\2 Project\MasterThesis
```

If `keep_type_dir: false`, the copied project may be written to:

```text
\\server\share\ProjectMigration\MasterThesis
```

## Notes

- Generated manifests now use folder names such as `2 Project` instead of display names such as `Project`.
- Older manifests using display names are still accepted for compatibility.
- If no project has `copy: true`, the script exits without copying anything.
- If a destination path is not reachable, the script raises a clear error before copy starts.
- For network shares, UNC paths are more reliable than mapped drive letters.

## Troubleshooting

### `PyYAML is required`

Install the dependency:

```terminal
pip install pyyaml
```

### `Project not found`

Check:

- `repo_path` points to the correct ProjectKeeper root
- `selected_projects[*].name` matches the real project name
- `selected_projects[*].type` matches the project type folder

### `Destination exists`

Either:

- delete the existing destination project folder first, or
- set `copy_options.overwrite: true`

### Network path not accessible

Prefer:

```text
\\server\share\ProjectMigration
```

instead of:

```text
Z:\
```

unless `Z:` is mapped in the same terminal session.
