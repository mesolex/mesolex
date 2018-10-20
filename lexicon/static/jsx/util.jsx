import _ from 'lodash';

import { CONTROLLED_VOCABULARY_FIELD_INDEX } from './constants';

export const isControlled = (field, value) => (
  _.includes(_.keys(CONTROLLED_VOCABULARY_FIELD_INDEX), field) &&
  _.includes(CONTROLLED_VOCABULARY_FIELD_INDEX[field], value)
);
