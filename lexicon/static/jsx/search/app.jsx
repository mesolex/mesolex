// import Plyr from 'plyr';

import React from 'react';
import ReactDOM from 'react-dom';

import Plyr from 'plyr';

import QueryBuilderFormset from 'query-builder/components/query-builder-formset';

const AUDIO_PLAYER_SELECTOR = 'lexical-entry-audio';
const LANGUAGE_CODE = 'azz';

export const initFunction = () => {
  const init = JSON.parse(document.getElementById('js-init').text);
  const {
    formset_data: formsetData,
    formset_errors: formsetErrors,
    formset_global_filters_form_data: formsetGlobalFiltersData,
  } = init.lexicon;
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

      globalExtraFields={languages[LANGUAGE_CODE].global_filters}
      formsetGlobalFiltersData={formsetGlobalFiltersData}
    />,
    document.querySelector('#lexicon-search-form'),
  );

  Plyr.setup(`.${AUDIO_PLAYER_SELECTOR}`, {
    controls: ['play'],
  });
};
