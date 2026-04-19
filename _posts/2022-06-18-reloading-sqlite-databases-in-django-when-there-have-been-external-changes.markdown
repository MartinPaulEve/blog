---
title: "Reloading SQLite databases in Django when there have been external changes"
layout: post
image: 
    feature: geek.png
doi: "https://doi.org/10.59348/gh1mh-br368"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2022/06/18/reloading-sqlite-databases-in-django-when-there-have-been-external-changes"
---
My backup application, django-caretaker, has to reload the SQLite database after it has run the import procedure. Basically, we're using an external tool to recreate (delete and replace) the original SQL file on disk. But Django won't always reload this.

There are three "gotchas" for how to handle this. The first is that you need a reload function. Mine is:

    def reload_database(database: str = '') -> None:
        """
        Reload the database
        """
        logger = log.get_logger('cache-clear')
        database: str = database if database else DEFAULT_DB_ALIAS

        connection: BaseDatabaseWrapper | AbstractDatabaseExporter \
            = connections[database]

        connection.close()
        connection.connect()

        cache.clear()

        logger.info('Cleared database cache')

The second problem is Django TestCase classes _run in atomic mode_. Basically, they are simulating all changes in memory for speed purposes. So if you ever replace the database file while running a TestCase, you will have dead data. Inherit from django.test.TransactionTestCase instead.

Finally, Django generally runs SQLite test cases using an _in-memory database_. You cannot delete and externally replace this. You can force your test case to use an on-disk file by specifying the TEST dictionary for a database with a name parameter that points to a file:

        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'TEST': {
                'NAME': BASE_DIR / 'test.sqlite3'
            }
        },

Essentially, if you replace or restore (using .read) the SQLite database underneath Django:

1. Reload the database
2. Ensure you are not operating in transaction.atomic mode
3. Make sure you are not using an in-memory SQLite database







