# Restoring an environment from backups

A working Mesolex environment requires a properly populated database and associated [user-uploaded "media" files](https://docs.djangoproject.com/en/3.2/topics/files/).
To get your local environment set up for the first time or to restore an environment to a working state,
you will need to fetch a database dump and media archive from some working environment, copy the
media files into the appropriate location, and restore your database from the dump after a postprocessing step.

To carry out the entire restoration process, you will need to be an authorized developer in the project (i.e. that you can run Ansible
playbooks against a Mesolex deployment). If you are not, ask a developer for a copy of the necessary files
and data.

## Fetching backups

To fetch a backup, use the `backup.yml` Ansible playbook:

```
$ ansible-playbook -i deployment/environments/dev/inventory deployment/playbooks/backup.yml
```

This will place two compressed files into the `./backup/` directory in this format:

- `db_dump-{environment}-{date}.sql.gz` (e.g. `db_dump-mesolex_staging-2021-04-25.sql`)
- `media_archive-{environment}-{date}.tgz` (e.g. `media_archive-mesolex_staging-2021-04-25.tgz`)

## Restoring media backup

To restore a deployment's media from a backup, just perform the following steps:

- Uncompress the media archive.
- Replace your project's `media/` dir with the expanded `media/` dir from the archive.
  - Locally, this will be `mesolex/media/`.
  - On a deployment environment, this will be `/var/www/mesolex/public/media/`.
- If necessary, change ownership of the files:

  ```
  $ sudo chown -R mesolex:mesolex /var/www/mesolex/public/media/
  ```

## Restoring a DB backup

To restore a deployment's database from a backup, perform these steps. (These illustrations will
assume you are restoring to your local deployment and using Docker. **TODO:** more general
instructions and examples for a remote environment!)

- Uncompress the database.
- Replace all references to the source database's name with one appropriate to the environment.
  The source db will have a name in the format `mesolex_{environment}`, e.g. `mesolex_dev` or `mesolex_prod`,
  and it will contain references to that string. These will need to be replaced in a way appropriate to
  the target environment. You can use `sed` (or on a Mac or other BSD system, `gsed`) to do this:

  ```
  $ sed -i 's/mesolex_staging/mesolex_local/g' ./backup/db_dump-mesolex_staging-2021-04-25.sql
  ```
- Drop the database you intend to restore and re-create it an empty state.

  ```sh 
  $ docker-compose stop web # make sure the web server isn't connected to the db
  $ docker-compose run --rm web dropdb mesolex_local
  $ docker-compose run --rm web createdb -E UTF-8 mesolex_local
  ```
- Run the SQL script against your database.

  ```
  $ docker-compose run --rm web psql -d mesolex_local -U mesolex_local -h db -p 5432 < ./backup/db_dump-mesolex_staging-2021-04-25.sql
  ```
