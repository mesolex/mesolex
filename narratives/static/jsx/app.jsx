import React from 'react';
import ReactDOM from 'react-dom';

import QueryBuilderFormset from 'query-builder/components/query-builder-formset';

const LANGUAGE_CODE = 'narratives';

export const initFunction = () => {
  const init = JSON.parse(document.getElementById('js-init').text);
  const {
    formset_data: formsetData,
    formset_global_filters_form_data: formsetGlobalFiltersData,
    formset_errors: formsetErrors,
  } = init.narratives;
  const { languages } = init;

  ReactDOM.render(
    <QueryBuilderFormset
      formsetName={LANGUAGE_CODE}

      formsetData={formsetData}
      formsetErrors={formsetErrors}

      controlledVocabFields={languages[LANGUAGE_CODE].controlled_vocab_fields}
      extraFields={languages[LANGUAGE_CODE].extra_fields}
      filterableFields={languages[LANGUAGE_CODE].filterable_fields}
      elasticsearchFields={languages[LANGUAGE_CODE].elasticsearch_fields}

      formsetGlobalFiltersData={formsetGlobalFiltersData}
    />,
    document.querySelector('#narrative-search-form'),
  );
};
