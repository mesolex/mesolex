import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';

import SearchFormSet from './add-search-form.jsx';


window.onload = () => {
  const {
    csrfToken,
    formset_data,
    formset_errors,
  } = JSON.parse(document.getElementById('js-init').text);

  ReactDOM.render(
    <SearchFormSet
      formsetData={formset_data}
      formsetErrors={formset_errors}
      csrfToken={csrfToken}
    />,
    document.querySelector('#search-form'),
  );
}
