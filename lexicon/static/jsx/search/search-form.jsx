/* global gettext $ */
import React from 'react';
import PropTypes from 'prop-types';
import classnames from 'classnames';
import Octicon from 'react-component-octicons';

import ControlledVocabInput from './controlled-vocab-input';
import FilterSelector from './filter-selector';

import {
  isControlled,
  humanReadableFilters,
} from '../util';


const SearchForm = ({
  i,
  dataset,
  errors,
  onChangeFieldFrom,
  removeFilter,
  languageConfiguration,
}) => (
  <div className="form-group">
    <label
      className="small search-form__filters-label"
      htmlFor={`form-${i}-filters-collapse`}
      onClick={() => $(`#form-${i}-filters-collapse`).collapse('toggle')}
    >
      { humanReadableFilters({
        i,
        operator: dataset.operator || 'and',
        filterOn: dataset.filter_on || 'lemma',
        filter: dataset.filter || 'begins_with',
        vln: (dataset.filter !== 'regex') && dataset.vln,
      }) }
    </label>
    <div className="input-group">
      <div className="input-group-prepend">
        <a
          className="btn btn-outline-primary"
          href={`form-${i}-filters-collapse`}
          id={`form-${i}-filters-link`}
          role="button"
          data-toggle="collapse"
          aria-expanded="false"
          aria-controls={`form-${i}-filters-collapse`}
          onClick={() => $(`#form-${i}-filters-collapse`).collapse('toggle')}
        >
          <Octicon name="gear" />
        </a>
      </div>
      {
        isControlled('filter_on', dataset.filter_on)
        ?
          <ControlledVocabInput
            name={`form-${i}-query_string`}
            className={classnames(
              'custom-select',
              'search-form__select',
              { 'is-invalid': (errors.query_string || []).length },
            )}
            id={`id_form-${i}-query_string`}
            value={dataset.query_string}
            onChange={onChangeFieldFrom('query_string')}
            vocab={dataset.filter_on}
            languageConfiguration={languageConfiguration}
          />
        :
          <input
            name={`form-${i}-query_string`}
            className={classnames(
              'form-control',
              { 'is-invalid': (errors.query_string || []).length },
            )}
            id={`id_form-${i}-query_string`}
            type="text"
            value={dataset.query_string}
            onChange={onChangeFieldFrom('query_string')}
          />
      }
      {
        i > 0 ?
          <div className="input-group-append">
            <button
              type="button"
              className="btn btn-outline-secondary"
              onClick={removeFilter}
            >
              <Octicon name="x" />
            </button>
          </div> :
          null
      }
      {
        (errors.query_string || []).length ?
          errors.query_string.map(error => (
            <div className="invalid-feedback">
              {error}
            </div>
          )) :
          null
      }
    </div>
    <div
      className="collapse input-group mt-2"
      id={`form-${i}-filters-collapse`}
      aria-labelledby={`form-${i}-filters-link`}
    >
      <div className="input-group">
        <select
          name={`form-${i}-operator`}
          className="custom-select search-form__select"
          id={`id_form-${i}-operator`}
          value={dataset.operator}
          onChange={onChangeFieldFrom('operator')}
        >
          <option value="and">{i === 0 ? gettext('si') : gettext('y')}</option>
          {i === 0 ? null : <option value="or">{`${gettext('o')}`}</option>}
          <option value="and_n">{i === 0 ? gettext('no') : gettext('y no')}</option>
          {i === 0 ? null : <option value="or_n">{`${gettext('o no')}`}</option>}
        </select>
        <select
          name={`form-${i}-filter_on`}
          className="custom-select search-form__select"
          id={`id_form-${i}-filter_on`}
          value={dataset.filter_on}
          onChange={onChangeFieldFrom('filter_on')}
        >
          <option value="lemma">{`${gettext('entrada')}`}</option>
          <option value="gloss">{`${gettext('glosa')}`}</option>
          <option value="root">{`${gettext('raiz')}`}</option>
          <option value="category">{`${gettext('campo semántico')}`}</option>
          <option value="part_of_speech">{`${gettext('categoría gramatical')}`}</option>
          <option value="inflectional_type">{`${gettext('inflexión')}`}</option>
        </select>

        <FilterSelector
          name={`form-${i}-filter`}
          className="custom-select search-form__select"
          id={`id_form-${i}-filter`}
          value={dataset.filter}
          onChange={onChangeFieldFrom('filter')}
          controlled={isControlled('filter_on', dataset.filter_on)}
        />
      </div>
      {
        isControlled('filter_on', dataset.filter_on)
        ? null
        : (
          <div className="form-check mt-2">
            <input
              type="checkbox"
              className="form-check-input"
              id={`id_form-${i}-vln`}
              name={`form-${i}-vln`}
              checked={dataset.vln}
              disabled={dataset.filter === 'regex'}
              onChange={onChangeFieldFrom('vln', 'checked')}
            />
            <label htmlFor={`id_form-${i}-vln`} className="form-check-label">
              {gettext('Neutralizar cantidad vocálica')}
            </label>
          </div>
        )
      }
    </div>
  </div>
);

SearchForm.propTypes = {
  i: PropTypes.number.isRequired,
  dataset: PropTypes.shape.isRequired,
  errors: PropTypes.shape.isRequired,
  onChangeFieldFrom: PropTypes.func.isRequired,
  removeFilter: PropTypes.func.isRequired,
  languageConfiguration: PropTypes.shape.isRequired,
};

export default SearchForm;
