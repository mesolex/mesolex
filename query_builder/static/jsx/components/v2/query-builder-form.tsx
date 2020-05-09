import * as React from 'react';

import Dropdown from 'react-bootstrap/Dropdown';
import DropdownButton from 'react-bootstrap/DropdownButton';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';

declare const gettext: (messageId: string) => string;

interface FormDataset {
  filter: string,
  filterOn: string,
  operator: string,
  queryString: string,
}

interface FormProps {
  dataset: FormDataset,
}

interface SelectProps {
  onChange: (event: React.FormEvent<HTMLSelectElement>) => void,
  value: string,
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

const FieldSelect = () => (
  <Form.Control as="select" custom>
    <option value="1">Headword</option>
    <option value="2">Gloss</option>
    <option value="3">Root</option>
    <option value="4">Semantic Field</option>
  </Form.Control>
);

const FilterSelect = () => (
  <Form.Control as="select" custom>
    <option value="1">begins with</option>
    <option value="2">ends with</option>
    <option value="3">contains sequence</option>
    <option value="4">contains word</option>
  </Form.Control>
);

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
        <Dropdown.Item as={FieldSelect} />
        <Dropdown.Item as={FilterSelect} />
      </DropdownButton>

      <Form.Control placeholder="Query string" />
    </InputGroup>
  </Form.Group>
);

export default QueryBuilderForm;
