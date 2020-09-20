import * as _ from 'lodash';

import { FilterableField } from './types';

declare const gettext: (messageId: string) => string;

export const humanReadableFilters = ({
  i,
  operator,
  filterOn,
  filter,
  vln,
  nahuatOrthography,
  filterableFields,
}: {
  i: number;
  operator: string;
  filterOn: string;
  filter: string;
  vln?: boolean;
  nahuatOrthography?: boolean;
  filterableFields: Array<FilterableField>;
}): string => {
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
    begins_with: `${gettext('empieza con')}`,
    ends_with: `${gettext('termina con')}`,
    contains: `${gettext('contiene secuencia')}`,
    contains_word: `${gettext('contiene palabra')}`,
    exactly_equals: `${gettext('es exactamente igual a')}`,
    regex: `${gettext('coincide con expresión regular')}`,
    text_search: `${gettext('coincide con')}`,
  };

  const filterableFieldsDict: { [fieldName: string]: string } = _.chain(filterableFields)
    .map(({ field, label }) => [field, gettext(label)])
    .fromPairs()
    .value();

  const modifiers: Array<string> = _.reduce(
    [
      [vln, gettext('NCV')],
      [nahuatOrthography, gettext('flex. ort.')],
    ],
    (acc, [val, repr]) => (val ? acc.concat(repr) : acc),
    [],
  );

  const prefix = i === 0 ? initOpDict[operator] : opDict[operator];
  const filterOnLabel = filterableFieldsDict[filterOn] || gettext('ítem');
  const filterLabel = filterDict[filter];
  const modifiersLabel = modifiers.length ? `(${modifiers.join(', ')})` : '';

  return [prefix, filterOnLabel, filterLabel, modifiersLabel].join(' ');
};
