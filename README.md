# ProjectKeeper

**Note: This project is still under development**

以项目为组织的类Git文件备份软件，适用于日常工作备份。
A git-like software that helps organize and back up files in projects. Your reliable solution for everyday use.

## Note

- If you meet with problem when executing `projectkeeper.py` and try to backup files in vscode terminal:

    ```terminal
    'attrib' 不是内部或外部命令，也不是可运行的程序
    或批处理文件。
    ```

    Just run it in powershell outside vscode.

- json.load的encoding参数在python3.9中弃用

- Use opencv conda env.

## Migration / Copy selected projects

You can now generate a yaml manifest, edit selection and copy options, then execute copy.

1. Generate manifest:

    ```terminal
    python projectmigrate.py generate-manifest --repo "D:\\SFTR" --output migration_manifest.yaml --dest "E:\\MigrationTarget"
    ```

2. Edit `migration_manifest.yaml`:
   - set `selected_projects[*].copy: true` for projects you want to migrate
   - configure `copy_options` (`copy_project`, `copy_event`, `copy_ext`, ...)
   - optional: `backup_before_copy: true` and set `backup_root`

3. Run copy:

    ```terminal
    python projectmigrate.py copy --manifest migration_manifest.yaml
    ```
