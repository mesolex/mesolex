/* global gettext */
import React from 'react';
import PropTypes from 'prop-types';

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

export default FilterSelector;
