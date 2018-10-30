/* global gettext $ */
import React from 'react';
import PropTypes from 'prop-types';
import classnames from 'classnames';
import Octicon from 'react-component-octicons';

import { isControlled } from '../util';

const humanReadableFilterOn = (filterOn) => {
  switch (filterOn) {
    case 'lemma':
      return gettext('entrada');
    case 'gloss':
      return gettext('glosa');
    case 'root':
      return gettext('raiz');
    case 'category':
      return gettext('campo semántico');
    case 'part_of_speech':
      return gettext('categoría gramatical');
    default:
      return gettext('entrada');
  }
};

/*
  Helper to render the text displayed above the input row.
*/
const humanReadableFilters = ({
  i,
  operator,
  filterOn,
  filter,
  vln,
}) => {
  const initOpDict = {
    and: '',
    and_n: `${gettext('no')}:`,
    or: '',
    or_n: `${gettext('no')}:`,
  };
  const opDict = {
    and: `${gettext('y')}:`,
    or: `${gettext('o')}:`,
    and_n: `${gettext('y no')}:`,
    or_n: `${gettext('o no')}:`,
  };
  const filterDict = {
    begins_with: gettext('empieza con'),
    ends_with: gettext('termina con'),
    contains: gettext('contiene'),
    exactly_equals: gettext('es exactamente igual a'),
    regex: gettext('coincide con expresión regular'),
  };
  return `${i === 0 ? initOpDict[operator] : opDict[operator]} ${humanReadableFilterOn(filterOn)} ${filterDict[filter]}${ vln ? ` (${gettext('NCV')})` : ''}`;
};

/*
  Helper component to generate the special selector used for a controlled
  vocabulary item.

  NOTE: this is basically a stub implementation awaiting more
  parameterization by other types of controlled value.
*/
const ControlledVocabInput = ({
  name,
  className,
  id,
  value,
  onChange,
  languageConfiguration,
}) => (
  <select
    name={name}
    className={className}
    id={id}
    value={value}
    onChange={onChange}
  >
    {
      languageConfiguration.azz.parts_of_speech.map(([pos, readable]) => (
        <option value={pos} key={pos}>{`${gettext(readable)}`}</option>
      ))
    }
  </select>
);

ControlledVocabInput.propTypes = {
  name: PropTypes.string.isRequired,
  className: PropTypes.shape.isRequired,
  id: PropTypes.number.isRequired,
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  languageConfiguration: PropTypes.shape.isRequired,
};

/*
  Helper component describing the selector for the "filter" type (starts with,
  exactly equals, etc).

  If the chosen "filter on" field is a controlled-vocab item (e.g. grammatical
  category), the user should have no choice: this can only be "exactly_equals".
  The prop "controlled" determines what gets rendered here, removing
  irrelevant options, as well as determining the value of the input.
*/
const FilterSelector = ({
  name,
  className,
  id,
  value,
  onChange,
  controlled,
}) => (
  <select
    name={name}
    className={className}
    id={id}
    value={controlled ? 'exactly_equals' : value}
    onChange={onChange}
  >
    {controlled ? null : <option value="begins_with">{`${gettext('empieza con')}`}</option>}
    {controlled ? null : <option value="ends_with">{`${gettext('termina con')}`}</option>}
    {controlled ? null : <option value="contains">{`${gettext('contiene')}`}</option>}
    <option value="exactly_equals">{`${gettext('es exactamente igual a')}`}</option>
    {controlled ? null : <option value="regex">{`${gettext('expresión regular')}`}</option>}
  </select>
);

FilterSelector.propTypes = {
  name: PropTypes.string.isRequired,
  className: PropTypes.shape.isRequired,
  id: PropTypes.number.isRequired,
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  controlled: PropTypes.bool.isRequired,
};

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
