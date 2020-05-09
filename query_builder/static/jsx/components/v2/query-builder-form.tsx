import * as React from 'react';

import * as _ from 'lodash';

import Dropdown from 'react-bootstrap/Dropdown';
import DropdownButton from 'react-bootstrap/DropdownButton';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';

import FilterSelector from './filter-selector';
import { FilterableField, FormDataset, SelectProps } from './types';

declare const gettext: (messageId: string) => string;

interface FormProps {
  dataset: FormDataset;
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
    value={props.value}
  >
    { _.map(props.fields, ({ field, label }) => <option value={field}>{ label }</option>) }
  </Form.Control>
));

/**
 * TODO: customize the styles to eliminate the borders
 * in the dropdown select inputs
 */

const QueryBuilderForm = (props: FormProps) => (
  <Form.Group>
    <Form.Label>
      (Label of filter input)
    </Form.Label>

    <InputGroup>
      <DropdownButton
        as={InputGroup.Prepend}
        id="filter-params"
        title="Filter params"
      >
        <Dropdown.Item
          as={OperatorSelect}
          onChange={(event) => console.log('Hello world', event)}
          value={props.dataset.operator}
        />

        <Dropdown.Item
          as={FieldSelect}
          fields={props.filterableFields}
          onChange={(event) => console.log('Hello world', event)}
          value={props.dataset.filter_on}
        />

        {/* TODO: add control and search determination */}
        <Dropdown.Item
          as={FilterSelector}
          controlled={false}
          textSearch={false}
          onChange={(event) => console.log('Hello world', event)}
          value={props.dataset.filter}
        />
      </DropdownButton>

      <Form.Control placeholder="Query string" />
    </InputGroup>
  </Form.Group>
);

export default QueryBuilderForm;
