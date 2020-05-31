import * as React from 'react';
import { useState } from 'react';

import * as _ from 'lodash';
import * as uuid4 from 'uuid/v4';

import Form from 'react-bootstrap/Form';

import QueryBuilderForm from './query-builder-form';

import AddRemoveForms from './add-remove-forms';
import {
  ControlledVocabField,
  ExtraField,
  FilterableField,
  FormDataset,
} from '../types';

declare const gettext: (messageId: string) => string;

interface QueryBuilderFormSetProps {
  formsetData: Array<FormDataset>;
  formsetErrors: Array<{ [fieldName: string]: Array<string> }>;
  formsetName: string;

  // from language:
  controlledVocabFields: Array<ControlledVocabField>;
  extraFields: Array<ExtraField>;
  filterableFields: Array<FilterableField>;
  elasticsearchFields: Array<FilterableField>;

  // from app initialization:
  formsetGlobalFiltersData: { [field: string]: boolean };
  globalExtraFields: Array<ExtraField>;
}

const FormsetInitForms = (props: {
  count: number;
  initialCount: number;
}): JSX.Element => (
  <>
    <input
      name="form-TOTAL_FORMS"
      value={props.count}
      id="id_form-TOTAL_FORMS"
      type="hidden"
    />
    <input
      name="form-INITIAL_FORMS"
      value={props.initialCount}
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

const makeDefaultInitialData = (filterableFields: Array<FilterableField>): FormDataset => ({
  query_string: '',
  operator: 'and',
  filter_on: filterableFields[0].field,
  filter: 'begins_with',
});

const labelForGlobalFilter = (
  globalFilters: Array<ExtraField>,
  key: string,
): string => gettext(_.find(globalFilters, ({ field }) => field === key).label || '');

const GlobalFilters = (props: {
  globalExtraFields: Array<ExtraField>;
  globalFilters: { [fieldName: string]: boolean };
  setGlobalFilters: React.Dispatch<React.SetStateAction<{ [fieldName: string]: boolean}>>;
}): JSX.Element => (
  <Form.Group>
    { _.map(props.globalFilters, (value, key) => (
      <Form.Check
        checked={value}
        label={labelForGlobalFilter(props.globalExtraFields, key)}
        name={key}
        onChange={(event): void => {
          props.setGlobalFilters((prevGlobalFilters) => ({
            ...prevGlobalFilters,
            [key]: event.target.checked,
          }));
        }}
      />
    ))}
  </Form.Group>
);

const QueryBuilderFormSet = (props: QueryBuilderFormSetProps): JSX.Element => {
  const filterableFields = _.concat(props.filterableFields, props.elasticsearchFields);

  const [
    formKeySeqState,
    setFormKeySeqState,
  ] = useState(() => _.map(props.formsetData, () => uuid4()));

  const [globalFilters, setGlobalFilters] = useState(
    _.chain(props.globalExtraFields)
      .map(({ field }) => ({ [field]: props.formsetGlobalFiltersData[field] || false }))
      .reduce((acc, next) => ({ ...acc, ...next }), {})
      .value(),
  );

  return (
    <>
      <input
        type="hidden"
        name="dataset"
        value={props.formsetName}
      />

      <FormsetInitForms
        count={formKeySeqState.length || 1}
        initialCount={props.formsetData.length || 1}
      />

      <Form.Group>
        { _.map(formKeySeqState, (key, i) => (
          <QueryBuilderForm
            controlledVocabFields={props.controlledVocabFields}
            elasticsearchFields={props.elasticsearchFields}
            extraFields={props.extraFields}
            index={i}
            initialData={props.formsetData[i] || makeDefaultInitialData(filterableFields)}
            initialErrors={props.formsetErrors[i] || {}}
            key={key}
            filterableFields={filterableFields}
            onDelete={(): void => setFormKeySeqState(
              (prevState) => _.filter(prevState, (k) => k !== key),
            )}
          />
        )) }
      </Form.Group>

      <GlobalFilters
        globalExtraFields={props.globalExtraFields}
        globalFilters={globalFilters}
        setGlobalFilters={setGlobalFilters}
      />

      <AddRemoveForms
        onAddFilter={(): void => setFormKeySeqState((prevState) => prevState.concat(uuid4()))}
      />
    </>
  );
};

export default QueryBuilderFormSet;
