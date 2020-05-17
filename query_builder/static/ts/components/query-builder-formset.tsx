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


// TODO: correct "Any" type here
// const constructInitialFormState = (params: {
//   formsetData: Array<FormDataset>;
//   formsetErrors: Array<QueryBuilderErrorIndex>;
//   extraFieldNames: Array<string>;
//   filterableFields: Array<string>;
//   defaultFilter: string;
// }): Array<QueryBuilderFormStateItem> => {
//   const formDataPairs = _.zip(params.formsetData, params.formsetErrors);

//   return _.map(
//     formDataPairs,
//     ([data, errors]) => ({
//       id: uuid4(),

//       data: _.defaults(
//         data,
//         ..._.map(params.extraFieldNames, (fieldName) => ({ [fieldName]: !!data[fieldName] })),
//         {
//           query_string: '', // eslint-disable-line @typescript-eslint/camelcase
//           operator: 'and',
//           // eslint-disable-next-line @typescript-eslint/camelcase
//           filter_on: params.filterableFields[0][0],
//           filter: params.defaultFilter,
//         },
//         ..._.map(params.extraFieldNames, (fieldName) => ({ [fieldName]: false })),
//       ),

//       errors,
//     }),
//   );
// };

const QueryBuilderFormSet = (props: QueryBuilderFormSetProps): JSX.Element => {
  const filterableFields = _.concat(props.filterableFields, props.elasticsearchFields);

  const [formKeySeqState] = useState(() => _.map(props.formsetData, () => uuid4()));

  return (
    <>
      <FormsetInitForms count={props.formsetData.length || 1} />

      <Form.Group>
        { _.map(formKeySeqState, (key, i) => (
          <QueryBuilderForm
            controlledVocabFields={props.controlledVocabFields}
            initialData={props.formsetData[i]}
            initialErrors={props.formsetErrors[i]}
            key={key}
            filterableFields={filterableFields}
          />
        )) }
      </Form.Group>
    </>
  );
};

export default QueryBuilderFormSet;
