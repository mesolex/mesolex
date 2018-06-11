import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';

import SearchFormSet from './add-search-form.jsx';


window.onload = () => {
  const jsInit = JSON.parse(document.getElementById('js-init').text);

  ReactDOM.render(
    <SearchFormSet csrfToken={jsInit.csrfToken} />,
    document.querySelector('#search-form'),
  );
}
