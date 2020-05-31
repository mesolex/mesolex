// import Plyr from 'plyr';

import React from 'react';
import ReactDOM from 'react-dom';

import Plyr from 'plyr';

import SearchFormSet from './v2/search-formset.tsx';

const AUDIO_PLAYER_SELECTOR = 'lexical-entry-audio';
const LANGUAGE_CODE = 'azz';

export const initFunction = () => {
  const init = JSON.parse(document.getElementById('js-init').text);
  const {
    // formset_config: formsetConfig,
    formset_data: formsetData,
    // formset_datasets_form_data: formsetDatasetsFormData,
    formset_global_filters_form_data: formsetGlobalFiltersData,
    formset_errors: formsetErrors,
  } = init.lexicon;
  const { languages } = init;

  ReactDOM.render(
    <SearchFormSet
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
