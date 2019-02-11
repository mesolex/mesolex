/* global gettext */
import React from 'react';

import QueryBuilderFormset from 'query-builder/components/query-builder-formset';
import Vln from './vln';


export default class SearchFormSet extends QueryBuilderFormset {
  globalFiltersComponents = ({ data, onChangeGlobalField }) => (
    <div className="form-group">
      <div className="form-check">
        <input
          type="checkbox"
          className="form-check-input"
          id="id_only_with_sound"
          name="only_with_sound"
          checked={data.only_with_sound}
          onChange={onChangeGlobalField('only_with_sound', 'checked')}
        />
        <label htmlFor="id_only_with_sound" className="form-check-label">
          {gettext('Solo mostrar palabras con sonidos')}
        </label>
      </div>
    </div>
  )

  extraFilterComponents = ({ i, uniqueId }) => ([
    <Vln
      i={i}
      key="vln"
      config={this.props.formsetConfig}
      dataset={this.state.formsetIndexedDatasets[uniqueId]}
      onChangeFieldFrom={this.onChangeFieldFrom(uniqueId)}
    />,
  ])
}
