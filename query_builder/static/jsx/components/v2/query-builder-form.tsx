import * as React from 'react';

import Dropdown from 'react-bootstrap/Dropdown';
import DropdownButton from 'react-bootstrap/DropdownButton';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';

declare const gettext: (messageId: string) => string;


const OperatorSelect = () => (
  <Form.Control as="select" custom>
    <option value="and">{gettext('y')}</option>
    <option value="or">{gettext('o')}</option>
    <option value="and_n">{gettext('y no')}</option>
    <option value="or_n">{gettext('o no')}</option>
  </Form.Control>
);

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


const QueryBuilderForm = () => (
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
        <Dropdown.Item as={OperatorSelect}>
          Operator
        </Dropdown.Item>
        <Dropdown.Item as={FieldSelect}>
          Field
        </Dropdown.Item>
        <Dropdown.Item as={FilterSelect}>
          Filter type
        </Dropdown.Item>
      </DropdownButton>

      <Form.Control placeholder="Query string" />
    </InputGroup>
  </Form.Group>
);

export default QueryBuilderForm;
