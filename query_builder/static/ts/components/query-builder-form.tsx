import * as React from 'react';
import { useState } from 'react';

import find from 'lodash-es/find';
import includes from 'lodash-es/includes';
import isEmpty from 'lodash-es/isEmpty';
import map from 'lodash-es/map';
import reduce from 'lodash-es/reduce';
import some from 'lodash-es/some';

import Button from 'react-bootstrap/Button';
import Dropdown from 'react-bootstrap/Dropdown';
import DropdownButton from 'react-bootstrap/DropdownButton';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';

import FilterSelector from './filter-selector';
import {
  ControlledVocabField,
  ExtraField,
  FilterableField,
  FormDataset,
  SelectProps,
} from '../types';

import { humanReadableFilters } from '../util';

declare const gettext: (messageId: string) => string;

interface FormProps {
  controlledVocabFields: Array<ControlledVocabField>;
  elasticsearchFields: Array<FilterableField>;
  extraFields: Array<ExtraField>;
  index: number;
  initialData: FormDataset;
  initialErrors: { [fieldName: string]: Array<string> };
  filterableFields: Array<FilterableField>;
  onDelete: () => void;
}

interface FieldSelectProps extends SelectProps {
  fields: Array<FilterableField>;
}

const OperatorSelect = React.forwardRef((props: SelectProps, ref: React.Ref<HTMLSelectElement>) => (
  <Form.Control
    ref={ref}
    as="select"
    className="search-form__filter-selector"
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
    className="search-form__filter-selector"
    custom
    onChange={props.onChange}
    value={props.value}
  >
    {
      map(
        props.fields,
        ({ field, label }) => <option value={field} key={field}>{ gettext(label) }</option>,
      )
    }
  </Form.Control>
));

/**
 * TODO: merge these two functions.
 */
const isControlled = (
  fieldName: string,
  controlledVocabFields: Array<ControlledVocabField>,
): boolean => some(controlledVocabFields, ({ field }) => field === fieldName);

const isTextSearch = (
  fieldName: string,
  elasticsearchFields: Array<FilterableField>,
): boolean => some(elasticsearchFields, ({ field }) => field === fieldName);

/**
 * When "filter on" changes, it may be necessary to set the value of
 * certain other fields. If the "filter on" has become a controlled vocab
 * field, the "filter" value can only be "is exactly"; if it has
 * become a text search field, it can only be "matches"; etc.
 */
const propagateFilterOnConditions = (
  filterOn: string,
  controlledVocabFields: Array<ControlledVocabField>,
  elasticsearchFields: Array<FilterableField>,
  setFilter: React.Dispatch<React.SetStateAction<string>>,
): void => {
  if (isControlled(filterOn, controlledVocabFields)) {
    setFilter('exactly_equals');
  }

  if (isTextSearch(filterOn, elasticsearchFields)) {
    setFilter('text_search');
  }
};

/**
 * Certain extra fields cannot be activated if certain values
 * are present in the form. For example, "neutralize vowel length"
 * cannot be active if the filter is in regular expression mode.
 *
 * This simple function returns `true` if any of the contraints
 * apply. Otherwise it returns `false`.
 */
const applyConstraints = ({
  filter,
  extraFields,
  extraFieldKey,
}: {
  filter: string;
  extraFields: Array<ExtraField>;
  extraFieldKey: string;
}): boolean => {
  const config = find(extraFields, ({ field }) => field === extraFieldKey);

  if (isEmpty(config)) {
    return false;
  }

  const { constraints } = config;

  if (includes(constraints, 'no_regex') && filter === 'regex') {
    return true;
  }

  return false;
};

/**
 * Because the values of the items in the dropdown menus that set
 * the filter parameters are not part of the actual form, we need
 * to make those values available via hidden inputs.
 */
const HiddenInputs = ({
  i,
  operator,
  filterOn,
  filter,
  extra,
}: {
  i: number;
  operator: string;
  filterOn: string;
  filter: string;
  extra: { [extraFieldName: string]: boolean };
}): JSX.Element => (
  <>
    <input type="hidden" name={`form-${i}-operator`} value={operator} />
    <input type="hidden" name={`form-${i}-filter_on`} value={filterOn} />
    <input type="hidden" name={`form-${i}-filter`} value={filter} />

    {
      map(extra, (value, fieldName) => (
        <input
          key={fieldName}
          type="checkbox"
          checked={value}
          name={`form-${i}-${fieldName}`}
          style={{ display: 'none' }}
          readOnly
        />
      ))
    }
  </>
);

const labelForExtraField = (
  extraFields: Array<ExtraField>,
  key: string,
): string => gettext(find(extraFields, ({ field }) => field === key).label || '');

const QueryBuilderForm = (props: FormProps): JSX.Element => {
  const [operator, setOperator] = useState(props.initialData.operator);
  const [filterOn, setFilterOn] = useState(props.initialData.filter_on);
  const [filter, setFilter] = useState(props.initialData.filter);
  const [queryString, setQueryString] = useState(props.initialData.query_string);

  /**
   * "Extra" fields are boolean-typed values that determine various filters
   * to be applied to the search, e.g. vowel length neutralization or
   * flexible orthography.
   *
   * TODO: figure out how to get `value` to typecheck better here!
   */
  const [extra, setExtra] = useState(
    reduce(
      map(
        props.extraFields,
        ({ field }) => ({ [field]: props.initialData[field] || false }),
      ),
      (acc, next) => ({ ...acc, ...next }),
      {},
    ),
  );
  // const [errorState, setErrorState] = useState(props.initialErrors);

  const controlledVocabFieldItems = isControlled(filterOn, props.controlledVocabFields)
    ? find(props.controlledVocabFields, ({ field }) => field === filterOn).items
    : [];

  return (
    <Form.Group>
      <InputGroup>
        <DropdownButton
          as={InputGroup.Prepend}
          variant="outline-primary"
          id="filter-params"
          title={humanReadableFilters({
            i: props.index,
            operator,
            filterOn,
            filter,
            filterableFields: props.filterableFields,
          })}
        >
          {
            props.index !== 0
              ? (
                <Dropdown.Item
                  as={OperatorSelect}
                  onChange={(event): void => setOperator(event.target.value)}
                  value={operator}
                />
              )
              : null
          }

          <Dropdown.Item
            as={FieldSelect}
            fields={props.filterableFields}
            onChange={(event): void => {
              setFilterOn(event.target.value);
              propagateFilterOnConditions(
                event.target.value,
                props.controlledVocabFields,
                props.elasticsearchFields,
                setFilter,
              );
            }}
            value={filterOn}
          />

          {/* TODO: add control and search determination */}
          <Dropdown.Item
            as={FilterSelector}
            controlled={isControlled(filterOn, props.controlledVocabFields)}
            onChange={(event): void => setFilter(event.target.value)}
            textSearch={isTextSearch(filterOn, props.elasticsearchFields)}
            value={filter}
          />

          { map(extra, (value, key) => (
            <Dropdown.Item
              key={key}
              as={Form.Check}
              checked={value}
              disabled={applyConstraints({
                filter,
                extraFields: props.extraFields,
                extraFieldKey: key,
              })}
              label={labelForExtraField(props.extraFields, key)}
              onChange={(event): void => {
                setExtra((prevExtra) => ({
                  ...prevExtra,
                  [key]: event.target.checked,
                }));
              }}
            />
          ))}
        </DropdownButton>

        {
          isControlled(filterOn, props.controlledVocabFields)
            ? (
              <Form.Control
                as="select"
                custom
                name={`form-${props.index}-query_string`}
                onChange={(event): void => setQueryString(event.target.value)}
                value={some(controlledVocabFieldItems, ({ value }) => value === queryString)
                  ? queryString
                  : controlledVocabFieldItems[0].value}
              >
                {map(
                  controlledVocabFieldItems,
                  ({ label, value }) => (
                    <option key={label} value={value}>{ gettext(label) }</option>
                  ),
                )}
              </Form.Control>
            )
            : (
              <Form.Control
                placeholder={gettext('Ingrese la consulta aquí')}
                name={`form-${props.index}-query_string`}
                onChange={(event): void => setQueryString(event.target.value)}
                type="text"
                value={queryString}
              />
            )
        }

        {
          props.index !== 0 && (
            <InputGroup.Append>
              <Button
                onClick={props.onDelete}
                variant="outline-secondary"
              >
                <span aria-hidden="true">&times;</span>
              </Button>
            </InputGroup.Append>
          )
        }
      </InputGroup>

      <HiddenInputs
        i={props.index}
        filter={filter}
        filterOn={filterOn}
        operator={operator}
        extra={extra}
      />
    </Form.Group>
  );
};

export default QueryBuilderForm;
