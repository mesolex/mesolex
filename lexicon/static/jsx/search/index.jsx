import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';

import SearchFormSet from './search-formset';


window.onload = () => {
  const {
    formset_data: formsetData,
    formset_errors: formsetErrors,
  } = JSON.parse(document.getElementById('js-init').text);

  ReactDOM.render(
    <SearchFormSet
      formsetData={formsetData}
      formsetErrors={formsetErrors}
    />,
    document.querySelector('#search-form'),
  );
};
