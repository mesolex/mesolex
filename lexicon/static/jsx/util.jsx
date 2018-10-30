/* global gettext */
import _ from 'lodash';

import { CONTROLLED_VOCABULARY_FIELD_INDEX } from './constants';

/*
  Predicate to determine whether the combination of a field-name
  and a value corresponds to a controlled vocabulary item.

  For example. `isControlled('filter_on', 'part_of_speech') === true`
  because "part of speech", as a value of the "filter on" form field,
  does indeed refer to a controlled vocabulary (noun, intransitive verb,
  etc).
*/
export const isControlled = (field, value) => (
  _.includes(_.keys(CONTROLLED_VOCABULARY_FIELD_INDEX), field) &&
  _.includes(CONTROLLED_VOCABULARY_FIELD_INDEX[field], value)
);

/*
  Helper function to more easily display the human-readable
  equivalent of some "filter on" value.

  Used inside humanReadableFilters.
*/
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
    case 'inflectional_type':
      return gettext('inflexión');
    default:
      return gettext('entrada');
  }
};

/*
  Helper to render the text displayed above the input row.
*/
export const humanReadableFilters = ({
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
