import * as React from 'react';
import { useState } from 'react';

import concat from 'lodash-es/concat';
import filter from 'lodash-es/filter';
import find from 'lodash-es/find';
import map from 'lodash-es/map';
import reduce from 'lodash-es/reduce';
import uniqueId from 'lodash-es/uniqueId';

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
): string => gettext(find(globalFilters, ({ field }) => field === key).label || '');

const GlobalFilters = (props: {
  globalExtraFields: Array<ExtraField>;
  globalFilters: { [fieldName: string]: boolean };
  setGlobalFilters: React.Dispatch<React.SetStateAction<{ [fieldName: string]: boolean}>>;
}): JSX.Element => (
  <Form.Group>
    { map(props.globalFilters, (value, key) => (
      <Form.Check
        key={key}
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
  const filterableFields = concat(props.filterableFields, props.elasticsearchFields);

  const [
    formKeySeqState,
    setFormKeySeqState,
  ] = useState(() => map(props.formsetData, () => uniqueId()));

  const [globalFilters, setGlobalFilters] = useState(
    reduce(
      map(
        props.globalExtraFields,
        ({ field }) => ({ [field]: props.formsetGlobalFiltersData[field] || false })
      ),
      (acc, next) => ({ ...acc, ...next }),
      {},
    ),
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
        { map(formKeySeqState, (key, i) => (
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
              (prevState) => filter(prevState, (k) => k !== key),
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
        onAddFilter={(): void => setFormKeySeqState((prevState) => prevState.concat(uniqueId()))}
      />
    </>
  );
};

export default QueryBuilderFormSet;
