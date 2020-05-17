import * as React from 'react';
import { useCallback, useState } from 'react';

import * as _ from 'lodash';

import Dropdown from 'react-bootstrap/Dropdown';
import DropdownButton from 'react-bootstrap/DropdownButton';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';

import FilterSelector from './filter-selector';
import { FilterableField, FormDataset, SelectProps } from '../types';

declare const gettext: (messageId: string) => string;

interface FormProps {
  initialData: FormDataset;
  initialErrors: { [fieldName: string]: Array<string> };
  filterableFields: Array<FilterableField>;
}

interface FieldSelectProps extends SelectProps {
  fields: Array<FilterableField>;
}

const OperatorSelect = React.forwardRef((props: SelectProps, ref: React.Ref<HTMLSelectElement>) => (
  <Form.Control
    ref={ref}
    as="select"
    custom
    onChange={props.onChange}
    value={props.value}
  >
    <option value="and">{gettext('y')}</option>
    <option value="or">{gettext('o')}</option>
    <option value="and_n">{gettext('y no')}</option>
    <option value="or_n">{gettext('o no')}</option>
  </Form.Control>
));

const FieldSelect = React.forwardRef((
  props: FieldSelectProps,
  ref: React.Ref<HTMLSelectElement>,
) => (
  <Form.Control
    ref={ref}
    as="select"
    custom
    onChange={props.onChange}
    value={props.value}
  >
    { _.map(props.fields, ({ field, label }) => <option value={field}>{ label }</option>) }
  </Form.Control>
));

/**
 * TODO: customize the styles to eliminate the borders
 * in the dropdown select inputs
 */
const QueryBuilderForm = (props: FormProps): JSX.Element => {
  const [operator, setOperator] = useState(props.initialData.operator);
  const [filterOn, setFilterOn] = useState(props.initialData.filter_on);
  const [filter, setFilter] = useState(props.initialData.filter);
  const [queryString, setQueryString] = useState(props.initialData.query_string);
  // const [errorState, setErrorState] = useState(props.initialErrors);

  return (
    <Form.Group>
      <InputGroup>
        <DropdownButton
          as={InputGroup.Prepend}
          id="filter-params"
          title="Filter params"
        >
          <Dropdown.Item
            as={OperatorSelect}
            onChange={(event): void => setOperator(event.target.value)}
            value={operator}
          />
          <Dropdown.Item
            as={FieldSelect}
            fields={props.filterableFields}
            onChange={(event): void => setFilterOn(event.target.value)}
            value={filterOn}
          />

          {/* TODO: add control and search determination */}
          <Dropdown.Item
            as={FilterSelector}
            controlled={false}
            onChange={(event): void => setFilter(event.target.value)}
            textSearch={false}
            value={filter}
          />
        </DropdownButton>

        <Form.Control
          placeholder="Query string"
          onChange={(event): void => setQueryString(event.target.value)}
          type="text"
          value={queryString}
        />
      </InputGroup>
    </Form.Group>
  );
};

export default QueryBuilderForm;
