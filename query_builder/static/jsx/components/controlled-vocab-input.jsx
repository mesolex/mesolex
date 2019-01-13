/* global gettext */
import React from 'react';
import PropTypes from 'prop-types';

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
  vocab,
  vocabItems,
}) => (
  <select
    name={name}
    className={className}
    id={id}
    value={value}
    onChange={onChange}
  >
    {
      (vocabItems[vocab] || []).map(([pos, readable]) => (
        <option value={pos} key={pos}>{`${gettext(readable)}`}</option>
      ))
    }
  </select>
);

ControlledVocabInput.propTypes = {
  name: PropTypes.string.isRequired,
  className: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  vocab: PropTypes.string.isRequired,
  vocabItems: PropTypes.shape({}).isRequired,
};

export default ControlledVocabInput;
