import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';

import SearchFormSet from './add-search-form.jsx';

ReactDOM.render(
  <SearchFormSet />,
  document.querySelector('#search-form'),
);
