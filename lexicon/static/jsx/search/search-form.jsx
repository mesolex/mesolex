/* global gettext $ */
import React from 'react';
import PropTypes from 'prop-types';
import classnames from 'classnames';
import Octicon from 'react-component-octicons';

/*
  Helper to render the text displayed above the input row.
*/
const humanReadableFilters = ({
  i,
  operator,
  // filterOn,
  filter,
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
  return `${i === 0 ? initOpDict[operator] : opDict[operator]} ${gettext('entrada')} ${filterDict[filter]}`;
};

const SearchForm = ({
  i,
  dataset,
  errors,
  onChangeFieldFrom,
  removeFilter,
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
        filterOn: dataset.filter_on || 'headword',
        filter: dataset.filter || 'begins_with',
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
          <option value="headword">{`${gettext('entrada')}`}</option>
        </select>
        <select
          name={`form-${i}-filter`}
          className="custom-select search-form__select"
          id={`id_form-${i}-filter`}
          value={dataset.filter}
          onChange={onChangeFieldFrom('filter')}
        >
          <option value="begins_with">{`${gettext('empieza con')}`}</option>
          <option value="ends_with">{`${gettext('termina con')}`}</option>
          <option value="contains">{`${gettext('contiene')}`}</option>
          <option value="exactly_equals">{`${gettext('es exactamente igual a')}`}</option>
          <option value="regex">{`${gettext('expresión regular')}`}</option>
        </select>
      </div>
      <div className="form-check">
        <input
          type="checkbox"
          className="form-check-input"
          id={`id_form-${i}-vln`}
          name={`form-${i}-vln`}
          checked={dataset.vln}
          onChange={onChangeFieldFrom('vln', 'checked')}
        />
        <label htmlFor={`id_form-${i}-vln`} className="form-check-label">
          {gettext('Neutraliza la longitud de la vocal')}
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
};

export default SearchForm;
