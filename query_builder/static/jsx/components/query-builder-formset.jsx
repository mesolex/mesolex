/* global gettext */
import React from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';
import uuid4 from 'uuid/v4';

import { controlledVocabCheck } from '../util';
import QueryBuilderForm from './query-builder-form';


export default class QueryBuilderFormSet extends React.Component {
  static propTypes = {
    formsetName: PropTypes.string,
    formsetConfig: PropTypes.shape({}).isRequired,
    formsetData: PropTypes.shape({}).isRequired,
    formsetGlobalFiltersData: PropTypes.shape({}).isRequired,
    formsetErrors: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  }

  static defaultProps = {
    formsetName: 'default',
  }

  /*
    Upon being initialized with formsetData and formsetErrors
    (which are provided from the rendered template on the basis
    of previously-submitted form data), the constructor will
    build an initial state consisting of:

    - `forms`, a simple list of unique identifiers
    - `formsetIndexedDatasets`, the form data for each form,
      indexed by the unique identifier from `forms`
    - `formsetIndexedErrors`, the errors for each form,
      indexed by the unique identifier from `forms`

    After being consumed, `formsetData` and `formsetErrors` are not used.
  */
  constructor(props) {
    super(props);
    const {
      formsetConfig,
      formsetData,
      formsetGlobalFiltersData,
      formsetErrors,
    } = props;

    /*
      Construct the list of forms by invoking `uuid` n times,
      where n == the initial formset's count or 1.
    */
    const forms = _.times(
      parseInt(formsetData['form-TOTAL_FORMS'], 10) || 1,
      () => uuid4(),
    );
    /*
      Construct a single-key object with the `form` uuid
      as the key, then roll them all up together into one
      big object.
    */
    const formsetIndexedDatasets = _.reduce(
      _.map(
        forms,
        (uniqueId, i) => ({
          [uniqueId]: {
            query_string: formsetData[`form-${i}-query_string`] || '',
            operator: formsetData[`form-${i}-operator`] || 'and',
            filter_on: formsetData[`form-${i}-filter_on`] || (formsetConfig.filterable_fields || [[]])[0][0],
            filter: formsetData[`form-${i}-filter`] || this.defaultFilter,
            vln: !!formsetData[`form-${i}-vln`],
          },
        }),
      ),
      (acc, dataset) => ({ ...acc, ...dataset }),
      {},
    );

    /*
      Construct the set of form errors by the same summing-up
      process as with formsetIndexedDatasets but with simpler
      construction logic (less postprocessing needed).
    */
    const formsetIndexedErrors = _.reduce(
      forms,
      (acc, uniqueId, i) => ({
        ...acc,
        [uniqueId]: formsetErrors[i] || {},
      }),
      {},
    );

    this.state = {
      forms,
      formsetIndexedDatasets,
      formsetIndexedErrors,
      formsetGlobalFiltersData,
    };
  }

  /*
    Check whether the first filterable field is a controlled
    vocab field. This is used to determine whether "exactly equals"
    or "begins with" is used as the default filter.
  */
  get firstIsControlled() {
    return _.includes(
      _.keys(this.props.formsetConfig.controlled_vocab_fields),
      (this.props.formsetConfig.filterable_fields || [[]])[0][0],
    );
  }

  get defaultFilter() {
    return this.firstIsControlled ? 'exactly_equals' : 'begins_with';
  }

  /*
    Higher-order function to create "onChange" functions that
    modify form data.

    At the formset level, an expression like `onChangeFieldFrom(uniqueId)`
    is another higher-order function that can be passed into
    a child search form to allow it to produce onChange functions
    associated with a particular form entry in the formset's
    collection of form data objects.

    The value of `onChangeFieldFrom(uniqueId)` will be used in
    expressions like `onChangeFieldFrom(uniqueId)('field_name', 'foo')`
    to produce an onChange listener that tells the formset to set
    the value of the field `'field_name'` to the value of the event
    target at `'foo'` on the form identified by `uniqueId`.

    A further feature is that if the field-value pair found
    is part of a "controlled vocabulary search" (i.e. if the user
    chooses that value for that field, e.g. "part of speech" for
    the lexical entry field to filter on, then there is only
    a particular set of vocab items they can search on, so
    only "is exactly equal to" is relevant), the `filter`
    value will be automatically set to `'exactly_equals'.`
  */
  onChangeFieldFrom = uniqueId => (field, eKey = 'value') => (e) => {
    this.setState({
      formsetIndexedDatasets: {
        ...this.state.formsetIndexedDatasets,
        [uniqueId]: Object.assign(
          {},
          {
            ...this.state.formsetIndexedDatasets[uniqueId],
            [field]: e.target[eKey],
          },
          (field === 'filter_on' && this.isControlled(e.target[eKey])) ? {
            filter: 'exactly_equals',
          } : {},
        ),
      },
    });
  }

  onChangeGlobalField = (fieldName, eKey = 'value') => ({ target }) => {
    this.setState({
      formsetGlobalFiltersData: {
        ...this.state.formsetGlobalFiltersData,
        [fieldName]: target[eKey],
      },
    });
  }

  isControlled = controlledVocabCheck(this.props.formsetConfig.controlled_vocab_fields)

  removeFilter = uniqueId => () => {
    this.setState({
      forms: _.filter(this.state.forms, form => uniqueId !== form),
      formsetIndexedDatasets: _.omit(this.state.formsetIndexedDatasets, uniqueId),
      formsetIndexedErrors: _.omit(this.state.formsetIndexedErrors, uniqueId),
    });
  }

  addFilter = (e) => {
    e.preventDefault();
    const newUniqueId = uuid4();
    this.setState({
      forms: [...this.state.forms, newUniqueId],
      formsetIndexedDatasets: {
        ...this.state.formsetIndexedDatasets,
        [newUniqueId]: {
          operator: 'and',
          filter_on: (this.props.formsetConfig.filterable_fields || [[]])[0][0],
          filter: this.defaultFilter,
          query_string: '',
        },
      },
      formsetIndexedErrors: {
        ...this.state.formsetIndexedErrors,
        [newUniqueId]: {},
      },
    });
  }

  extraFilterComponents = () => []

  globalFiltersComponents = () => null

  render() {
    const count = this.state.forms.length;
    return (
      <div>
        <input name="form-TOTAL_FORMS" value={count} id="id_form-TOTAL_FORMS" type="hidden" />
        <input name="form-INITIAL_FORMS" value="0" id="id_form-INITIAL_FORMS" type="hidden" />
        <input name="form-MIN_NUM_FORMS" value="0" id="id_form-MIN_NUM_FORMS" type="hidden" />
        <input name="form-MAX_NUM_FORMS" value="1000" id="id_form-MAX_NUM_FORMS" type="hidden" />

        {
          this.state.forms.map((uniqueId, i) => (
            <QueryBuilderForm
              i={i}
              formsetName={this.props.formsetName}
              defaultFilter={this.defaultFilter}
              key={uniqueId}
              config={this.props.formsetConfig}
              dataset={this.state.formsetIndexedDatasets[uniqueId]}
              errors={this.state.formsetIndexedErrors[uniqueId]}
              onChangeFieldFrom={this.onChangeFieldFrom(uniqueId)}
              removeFilter={this.removeFilter(uniqueId)}
              extraFilterComponents={this.extraFilterComponents({ i, uniqueId })}
            />
          ))
        }

        {
          this.globalFiltersComponents({
            data: this.state.formsetGlobalFiltersData,
            onChangeGlobalField: this.onChangeGlobalField,
          })
        }

        <div className="form-group">
          <button type="submit" className="btn btn-success">{`${gettext('Buscar')}`}</button>
          <button className="btn btn-primary float-right" id="add-filter" onClick={this.addFilter}>
            {`${gettext('Agregar filtro')}`}
          </button>
        </div>
      </div>
    );
  }
}
