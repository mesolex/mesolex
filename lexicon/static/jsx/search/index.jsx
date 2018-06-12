import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';

import SearchFormSet from './add-search-form';


window.onload = () => {
  const {
    csrfToken,
    formset_data: formsetData,
    formset_errors: formsetErrors,
  } = JSON.parse(document.getElementById('js-init').text);

  ReactDOM.render(
    <SearchFormSet
      formsetData={formsetData}
      formsetErrors={formsetErrors}
      csrfToken={csrfToken}
    />,
    document.querySelector('#search-form'),
  );
};
