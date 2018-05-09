# mesolex

TODO: add some documentation.

## solr setup

Install solr:

```
$ curl -L -O http://apache.claz.org/lucene/solr/7.3.0/solr-7.3.0.tgz
$ tar zxf solr-7.3.0.tgz
```

Create the `mesolex` core:

```
cd solr-7.3.0
bin/solr create_core -c mesolex
```

Once you've set up the `mesolex` core, build the solr schema:

```
$ ./manage.py build_solr_schema > solr-7.3.0/server/solr/mesolex/conf/schema.xml
```

Rebuild the search index:

```
$ ./manage.py rebuild_index
```
