# solr setup

mesolex uses django-haystack, a search backend-agnostic framework for
working with search in a fluent and Django-like way within a Django project.

Currently, solr is our choice of search backends for the project, and in
the name of keeping current, we are using the most recent version (as of May 14, 2018),
solr 7. Unfortunately, this doesn't work very well with django-haystack,
and some additional manual setup is required to make everything work.

## Changing `solrconfig.xml`

You will need to make changes to the solr config file `solrconfig.xml`
located in your project's solr core directory. Locally this will be
something like `solr-7.3.0/server/solr/mesolex/conf/solrconfig.xml`; on
a deployment target environment, it will be something like
`/var/solr/data/mesolex/conf/solrconfig.xml`. **NOTE** that when you are
working with the config file on your server, you will want to
do `sudo su - mesolex` to switch to the project user.

To begin with, follow the instructions in the [Lucene Schema Factory Definition](https://lucene.apache.org/solr/guide/6_6/schema-factory-definition-in-solrconfig.html#SchemaFactoryDefinitioninSolrConfig-SwitchingfromManagedSchematoManuallyEditedschema.xml) docs:

1. Remove any `ManagedIndexSchemaFactory` definition, if it exists
2. Add `<schemaFactory class="ClassicIndexSchemaFactory"/>` somewhere in the config

But you will need to take an additional step, namely finding these two blocks
and deleting them altogether:

```
<updateProcessor class="solr.AddSchemaFieldsUpdateProcessorFactory" name="add-schema-fields">
```

And:

```
<updateRequestProcessorChain name="add-unknown-fields-to-the-schema" default="${update.autoCreateFields:true}"
         processor="uuid,remove-blank,field-name-mutating,parse-boolean,parse-long,parse-double,parse-date,add-schema-fields">
  <processor class="solr.LogUpdateProcessorFactory"/>
  <processor class="solr.DistributedUpdateProcessorFactory"/>
  <processor class="solr.RunUpdateProcessorFactory"/>
</updateRequestProcessorChain>
```

Once you've done this, you can generate `schema.xml` and run `rebuild_index`
per the instructions in the mesolex `README.md`, and hopefully everything will
work just fine.

## Checking whether it works

If you are able to rebuild the index, probably everything is working as
you want it to. Nevertheless you might want to make sure. From the same
server as is running solr, you can use `pysolr` to do a quick query
and see if you get back what you expect:

```
>>> import pysolr
>>> solr = pysolr.Solr('http://localhost:8983/solr/mesolex')
>>> result = solr.search('nahua')
>>> result.raw_response
# a big blob of JSON showing good search result data
```

Breathe a sigh of relief: you are now ready to hack on mesolex!
