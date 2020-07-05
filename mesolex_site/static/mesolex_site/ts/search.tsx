import * as React from 'react';
import * as ReactDOM from 'react-dom';

import Plyr from 'plyr';

import QueryBuilderFormset from 'query-builder/components/query-builder-formset';

const AUDIO_PLAYER_SELECTOR = 'lexical-entry-audio';


export const initFunction = (): void => {
  const init = JSON.parse(document.getElementById('js-init').innerText);
  const {
    formset_data: formsetData,
    formset_errors: formsetErrors,
    formset_global_filters_form_data: formsetGlobalFiltersData,
    formset_name: formsetName,
  } = init.search;
  const { languages } = init;

  ReactDOM.render(
    <QueryBuilderFormset
      formsetName={formsetName}

      formsetData={formsetData}
      formsetErrors={formsetErrors}

      controlledVocabFields={languages[formsetName].controlled_vocab_fields}
      extraFields={languages[formsetName].extra_fields}
      filterableFields={languages[formsetName].filterable_fields}
      elasticsearchFields={languages[formsetName].elasticsearch_fields}

      globalExtraFields={languages[formsetName].global_filters}
      formsetGlobalFiltersData={formsetGlobalFiltersData}
    />,
    document.querySelector('#search-form'),
  );

  Plyr.setup(`.${AUDIO_PLAYER_SELECTOR}`, {
    controls: ['play'],
  });
};

window.addEventListener('load', initFunction);
