import * as React from 'react';
import { useState } from 'react';

import * as _ from 'lodash';
import * as uuid4 from 'uuid/v4';

import Form from 'react-bootstrap/Form';

import QueryBuilderForm from './query-builder-form';

import { ControlledVocabField, FilterableField, FormDataset } from '../types';

// TODO: figure out how to make this global

interface QueryBuilderFormSetProps {
  formsetData: Array<FormDataset>;
  formsetErrors: Array<{ [fieldName: string]: Array<string> }>;

  // from language:
  controlledVocabFields: Array<ControlledVocabField>;
  extraFieldNames: Array<string>;
  filterableFields: Array<FilterableField>;
  elasticsearchFields: Array<FilterableField>;
}

/**
 * See https://docs.djangoproject.com/en/3.0/ref/forms/api/#django.forms.Form.errors
 */
interface QueryBuilderErrorIndex {
  [fieldName: string]: Array<string>;
}

interface QueryBuilderFormStateItem {
  id: string;
  data: FormDataset;
  errors: QueryBuilderErrorIndex;
}

const FormsetInitForms = (props: {count: number}): JSX.Element => (
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

const QueryBuilderFormSet = (props: QueryBuilderFormSetProps): JSX.Element => {
  const filterableFields = _.concat(props.filterableFields, props.elasticsearchFields);

  const [
    formKeySeqState,
    setFormKeySeqState,
  ] = useState(() => _.map(props.formsetData, () => uuid4()));

  return (
    <>
      <FormsetInitForms count={props.formsetData.length || 1} />

      <Form.Group>
        { _.map(formKeySeqState, (key, i) => (
          <QueryBuilderForm
            controlledVocabFields={props.controlledVocabFields}
            elasticsearchFields={props.elasticsearchFields}
            index={i}
            initialData={props.formsetData[i]}
            initialErrors={props.formsetErrors[i]}
            key={key}
            filterableFields={filterableFields}
            onDelete={(): void => setFormKeySeqState(
              (prevState) => _.filter(prevState, (k) => k !== key),
            )}
          />
        )) }
      </Form.Group>
    </>
  );
};

export default QueryBuilderFormSet;
