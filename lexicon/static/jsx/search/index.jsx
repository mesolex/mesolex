import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';

import AddSearchForm from './add-search-form.jsx';

ReactDOM.render(
  <AddSearchForm />,
  document.querySelector('#search-form'),
);
