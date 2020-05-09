import * as React from 'react';
import { useState } from 'react';

import * as _ from 'lodash';
import * as uuid4 from 'uuid/v4';

import Form from 'react-bootstrap/Form';

import QueryBuilderForm from './query-builder-form';

// TODO: figure out how to make this global

interface FormDataset {
  query_string: string, // eslint-disable-line camelcase
  operator: string,
  filter_on: string, // eslint-disable-line camelcase
  filter: string,
  [extraValues: string]: string,
}

interface ControlledVocabField {
  field: string,
  label: string,
}

interface FilterableField {
  field: string,
  label: string,
  terms: Array<string>,
}

interface QueryBuilderFormSetProps {
  formsetData: Array<FormDataset>,
  formsetErrors: Array<{ [fieldName: string]: Array<string> }>,

  // from language:
  controlledVocabFields: Array<ControlledVocabField>,
  extraFieldNames: Array<string>,
  filterableFields: Array<FilterableField>,
  elasticsearchFields: Array<FilterableField>,
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

const constructInitialFormState = (params: {
  formsetData: Array<FormDataset>,
  formsetErrors: Array<{ [formFieldName: string]: Array<string> }>,
  extraFieldNames: Array<string>,
  filterableFields: Array<string>,
  defaultFilter: string,
}): Array<any> => {
  const formDataPairs = _.zip(params.formsetData, params.formsetErrors);

  return _.map(
    formDataPairs,
    ([data, errors]) => ({
      id: uuid4(),

      data: _.defaults(
        data,
        ..._.map(params.extraFieldNames, (fieldName) => ({ [fieldName]: !!data[fieldName] })),
        {
          query_string: '',
          operator: 'and',
          filter_on: params.filterableFields[0][0],
          filter: params.defaultFilter,
        },
        ..._.map(params.extraFieldNames, (fieldName) => ({ [fieldName]: false })),
      ),

      errors,
    }),
  );
};

const QueryBuilderFormSet = (props: QueryBuilderFormSetProps) => {
  const [state] = useState(() => constructInitialFormState({
    formsetData: props.formsetData,
    formsetErrors: props.formsetErrors,
    extraFieldNames: props.extraFieldNames,
    filterableFields: _.concat(
      _.map(props.filterableFields, ({ field }) => field),
      _.map(props.elasticsearchFields, ({ field }) => field),
    ),
    defaultFilter: 'begins_with',
  }));

  return (
    <>
      <FormsetInitForms count={props.formsetData.length || 1} />

      <Form.Group>
        { _.map(state, ({ data }) => <QueryBuilderForm dataset={data} />) }
      </Form.Group>
    </>
  );
};

export default QueryBuilderFormSet;

/**
 * Essentials of the query builder form:
 *
 * - props include a set of `language` config data
 * - initialized with a set of `formsetData` provided by Django
 * - on mount, creates state that tracks its component forms
 */
