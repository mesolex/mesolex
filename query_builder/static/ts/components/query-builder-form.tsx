import * as React from 'react';
import { useState } from 'react';

import * as _ from 'lodash';

import Button from 'react-bootstrap/Button';
import Dropdown from 'react-bootstrap/Dropdown';
import DropdownButton from 'react-bootstrap/DropdownButton';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';
import Octicon from 'react-component-octicons';

import FilterSelector from './filter-selector';
import {
  ControlledVocabField,
  FilterableField,
  FormDataset,
  SelectProps,
} from '../types';

import { humanReadableFilters } from '../util';

declare const gettext: (messageId: string) => string;

interface FormProps {
  controlledVocabFields: Array<ControlledVocabField>;
  elasticsearchFields: Array<FilterableField>;
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
    { _.map(props.fields, ({ field, label }) => <option value={field}>{ label }</option>) }
  </Form.Control>
));

const isControlled = (
  fieldName: string,
  controlledVocabFields: Array<ControlledVocabField>,
): boolean => _.some(controlledVocabFields, ({ field }) => field === fieldName);

const isTextSearch = (
  fieldName: string,
  elasticsearchFields: Array<FilterableField>,
): boolean => _.some(elasticsearchFields, ({ field }) => field === fieldName);

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
 * Because the values of the items in the dropdown menus that set
 * the filter parameters are not part of the actual form, we need
 * to make those values available via hidden inputs.
 */
const HiddenInputs = ({
  i,
  operator,
  filterOn,
  filter,
}: {
  i: number;
  operator: string;
  filterOn: string;
  filter: string;
}): JSX.Element => (
  <>
    <input type="hidden" name={`form-${i}-operator`} value={operator} />
    <input type="hidden" name={`form-${i}-filter_on`} value={filterOn} />
    <input type="hidden" name={`form-${i}-filter`} value={filter} />
  </>
);

/**
 * TODO: customize the styles to eliminate the borders
 * in the dropdown select inputs
 */
const QueryBuilderForm = (props: FormProps): JSX.Element => {
  const [operator, setOperator] = useState(props.initialData.operator);
  const [filterOn, setFilterOn] = useState(props.initialData.filter_on);
  const [filter, setFilter] = useState(props.initialData.filter);
  const [queryString, setQueryString] = useState(props.initialData.query_string);
  // const [errorState, setErrorState] = useState(props.initialErrors);

  const controlledVocabFieldItems = isControlled(filterOn, props.controlledVocabFields)
    ? _.find(props.controlledVocabFields, ({ field }) => field === filterOn).items
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
          <Dropdown.Item
            as={OperatorSelect}
            onChange={(event): void => setOperator(event.target.value)}
            value={operator}
          />
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
        </DropdownButton>

        {
          isControlled(filterOn, props.controlledVocabFields)
            ? (
              <Form.Control
                as="select"
                custom
                name={`form-${props.index}-query_string`}
                onChange={(event): void => setQueryString(event.target.value)}
                value={_.some(controlledVocabFieldItems, ({ value }) => value === queryString)
                  ? queryString
                  : controlledVocabFieldItems[0].value}
              >
                {_.map(
                  controlledVocabFieldItems,
                  ({ label, value }) => <option value={value}>{ label }</option>,
                )}
              </Form.Control>
            )
            : (
              <Form.Control
                placeholder="Query string"
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
                <Octicon name="x" />
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
      />
    </Form.Group>
  );
};

export default QueryBuilderForm;
