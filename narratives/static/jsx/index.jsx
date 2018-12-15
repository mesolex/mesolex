import React from 'react';
import ReactDOM from 'react-dom';

import SearchFormSet from './components/search-formset';


window.onload = () => {
  const {
    formset_config: formsetConfig,
    formset_data: formsetData,
    formset_errors: formsetErrors,
  } = JSON.parse(document.getElementById('js-init').text);

  ReactDOM.render(
    <SearchFormSet
      formsetData={formsetData}
      formsetErrors={formsetErrors}
      formsetConfig={formsetConfig}
    />,
    document.querySelector('#search-form'),
  );
};