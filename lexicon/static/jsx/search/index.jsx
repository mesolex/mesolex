import 'babel-polyfill';
import Plyr from 'plyr';

import React from 'react';
import ReactDOM from 'react-dom';

import SearchFormSet from './search-formset';


const AUDIO_PLAYER_SELECTOR = 'lexical-entry-audio';


window.onload = () => {
  const {
    formset_config: formsetConfig,
    formset_data: formsetData,
    formset_errors: formsetErrors,
    language_configuration: languageConfiguration,
  } = JSON.parse(document.getElementById('js-init').text);

  ReactDOM.render(
    <SearchFormSet
      formsetData={formsetData}
      formsetErrors={formsetErrors}
      formsetConfig={formsetConfig}
      languageConfiguration={languageConfiguration}
    />,
    document.querySelector('#search-form'),
  );

  Plyr.setup(`.${AUDIO_PLAYER_SELECTOR}`);
};
