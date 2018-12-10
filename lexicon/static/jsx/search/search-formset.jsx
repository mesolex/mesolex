/* global */
import React from 'react';

import QueryBuilderFormset from 'query-builder/components/query-builder-formset';
import Vln from './vln';


export default class SearchFormSet extends QueryBuilderFormset {
  extraFilterComponents = ({ i, uniqueId }) => ([
    <Vln
      i={i}
      config={this.props.formsetConfig}
      dataset={this.state.formsetIndexedDatasets[uniqueId]}
      onChangeFieldFrom={this.onChangeFieldFrom(uniqueId)}
    />,
  ])
}
