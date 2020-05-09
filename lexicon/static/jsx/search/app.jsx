// import Plyr from 'plyr';

import React from 'react';
import ReactDOM from 'react-dom';

import SearchFormSet from './v2/search-formset.tsx';

// const AUDIO_PLAYER_SELECTOR = 'lexical-entry-audio';

export const initFunction = () => {
  const init = JSON.parse(document.getElementById('js-init').text);
  const {
    // formset_config: formsetConfig,
    formset_data: formsetData,
    // formset_datasets_form_data: formsetDatasetsFormData,
    // formset_global_filters_form_data: formsetGlobalFiltersData,
    formset_errors: formsetErrors,
  } = init.lexicon;
  const { languages } = init;

  ReactDOM.render(
    <SearchFormSet
      formsetName="lexicon"

      formsetData={formsetData}
      formsetErrors={formsetErrors}

      controlledVocabFields={languages.azz.controlled_vocab_fields}
      extraFieldNames={languages.azz.extra_fields}
      filterableFields={languages.azz.filterable_fields}
      elasticsearchFields={languages.azz.filterable_fields}
    />,
    document.querySelector('#lexicon-search-form'),
  );


  // ReactDOM.render(
  //   <SearchFormSet
  //     formsetConfig={formsetConfig}
  //     formsetData={formsetData}
  //     formsetDatasetsFormData={formsetDatasetsFormData}
  //     formsetName="lexicon"
  //     formsetErrors={formsetErrors}
  //     formsetGlobalFiltersData={formsetGlobalFiltersData}
  //     languages={languages}
  //   />,
  //   document.querySelector('#lexicon-search-form'),
  // );

  // Plyr.setup(`.${AUDIO_PLAYER_SELECTOR}`, {
  //   controls: ['play'],
  // });
};
