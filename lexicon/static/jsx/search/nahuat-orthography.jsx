/* global gettext */
import React from 'react';
import PropTypes from 'prop-types';

import { controlledVocabCheck } from 'query-builder/util';


const NahuatOrthography = ({
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
            id={`id_form-${i}-nahuat_orthography`}
            name={`form-${i}-nahuat_orthography`}
            checked={dataset.nahuat_orthography}
            disabled={dataset.filter === 'regex'}
            onChange={onChangeFieldFrom('nahuat_orthography', 'checked')}
          />
          <label htmlFor={`id_form-${i}-nahuat_orthography`} className="form-check-label">
            {gettext('Ignorar las variantes ortográficas')}
          </label>
        </div>
      )
  );
};

NahuatOrthography.propTypes = {
  i: PropTypes.number.isRequired,
  config: PropTypes.shape({}).isRequired,
  dataset: PropTypes.shape({}).isRequired,
  onChangeFieldFrom: PropTypes.func.isRequired,
};

export default NahuatOrthography;
