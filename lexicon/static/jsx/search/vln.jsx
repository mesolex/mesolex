/* global gettext */
import React from 'react';
import PropTypes from 'prop-types';

import { controlledVocabCheck } from 'query-builder/util';


const Vln = ({
  i,
  config,
  dataset,
  onChangeFieldFrom,
}) => {
  const isControlled = controlledVocabCheck(config.controlled_vocab_fields || {});

  return (
    isControlled(dataset.filter_on)
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
  );
};

Vln.propTypes = {
  i: PropTypes.number.isRequired,
  config: PropTypes.shape.isRequired,
  dataset: PropTypes.shape.isRequired,
  onChangeFieldFrom: PropTypes.func.isRequired,
};

export default Vln;
