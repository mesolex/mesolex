import Plyr from 'plyr';

import React from 'react';
import ReactDOM from 'react-dom';

import SearchFormSet from './search-formset';


const AUDIO_PLAYER_SELECTOR = 'lexical-entry-audio';

const initFunction = () => {
  const {
    formset_config: formsetConfig,
    formset_data: formsetData,
    formset_errors: formsetErrors,
  } = JSON.parse(document.getElementById('js-init').text).lexicon;

  ReactDOM.render(
    <SearchFormSet
      formsetName="lexicon"
      formsetData={formsetData}
      formsetErrors={formsetErrors}
      formsetConfig={formsetConfig}
    />,
    document.querySelector('#lexicon-search-form'),
  );

  Plyr.setup(`.${AUDIO_PLAYER_SELECTOR}`);
};

if (window.addEventListener) {
  window.addEventListener('load', initFunction);
} else {
  window.attachEvent('onload', initFunction);
}
