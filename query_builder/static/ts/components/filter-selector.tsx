import * as React from 'react';

import Form from 'react-bootstrap/Form';

import { SelectProps } from '../types';

declare const gettext: (messageId: string) => string;

interface FilterSelectorProps extends SelectProps {
  controlled: boolean;
  textSearch: boolean;
}

const FilterSelector = React.forwardRef((
  props: FilterSelectorProps,
  ref: React.Ref<HTMLSelectElement>,
) => (
  <Form.Control
    ref={ref}
    as="select"
    className="search-form__filter-selector"
    custom
    onChange={props.onChange}
    value={props.value}
  >
    {props.controlled || props.textSearch ? null : <option value="begins_with">{`${gettext('empieza con')}`}</option>}
    {props.controlled || props.textSearch ? null : <option value="ends_with">{`${gettext('termina con')}`}</option>}
    {props.controlled || props.textSearch ? null : <option value="contains">{`${gettext('contiene secuencia')}`}</option>}
    {props.controlled || props.textSearch ? null : <option value="contains_word">{`${gettext('contiene palabra')}`}</option>}
    {props.textSearch ? null : <option value="exactly_equals">{`${gettext('es exactamente igual a')}`}</option>}
    {props.controlled || props.textSearch ? null : <option value="regex">{`${gettext('expresión regular')}`}</option>}
    {props.textSearch ? <option value="text_search">{`${gettext('coincide con')}`}</option> : null}
  </Form.Control>
));

export default FilterSelector;
