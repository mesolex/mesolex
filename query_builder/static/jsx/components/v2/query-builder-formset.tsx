import * as React from 'react';

import * as _ from 'lodash';

import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';

interface QueryBuilderFormSetProps {
  languages: Array<LanguageDefinition>,
}

interface LanguageDefinition {
  code: string,
  label: string,
  [other: string]: any,
}

const FormsetInitForms = (props: {count: number}) => (
  <>
    <input
      name="form-TOTAL_FORMS"
      value={props.count}
      id="id_form-TOTAL_FORMS"
      type="hidden"
    />
    <input
      name="form-INITIAL_FORMS"
      value="0"
      id="id_form-INITIAL_FORMS"
      type="hidden"
    />
    <input
      name="form-MIN_NUM_FORMS"
      value="0"
      id="id_form-MIN_NUM_FORMS"
      type="hidden"
    />
    <input
      name="form-MAX_NUM_FORMS"
      value="1000"
      id="id_form-MAX_NUM_FORMS"
      type="hidden"
    />
  </>
);

const LanguageOptions = (props: {languages: Array<LanguageDefinition>}) => (
  <>
    { _.map(props.languages, ({ label, code }) => (
      <option value={code}>
        { label }
      </option>
    )) }
  </>
);

const QueryBuilderFormSet = (props: QueryBuilderFormSetProps) => (
  <>
    <FormsetInitForms count={1} />

    <Form.Group>
      <Form.Label>
        Diccionario
      </Form.Label>
    </Form.Group>

    <InputGroup>
      <Form.Control as="select" custom>
        <LanguageOptions languages={props.languages} />
      </Form.Control>
    </InputGroup>
  </>
);

export default QueryBuilderFormSet;

/**
 * Essentials of the query builder form:
 *
 * - props include a set of `language` config data
 * - initialized with a set of `formsetData` provided by Django
 * - on mount, creates state that tracks its component forms
 */
