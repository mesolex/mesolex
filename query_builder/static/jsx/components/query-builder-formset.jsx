/* global gettext */
import React from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';
import uuid4 from 'uuid/v4';

import {
  controlledVocabCheck,
  makeControlledVocabFields,
  makeFilterableFields,
} from '../util';
import QueryBuilderForm from './query-builder-form';


export default class QueryBuilderFormSet extends React.Component {
  static propTypes = {
    formsetName: PropTypes.string,
    formsetConfig: PropTypes.shape({
      controlled_vocab_fields: PropTypes.object,
      filterable_fields: PropTypes.array,
      text_search_fields: PropTypes.arrayOf(PropTypes.string),
    }).isRequired,
    formsetData: PropTypes.arrayOf(PropTypes.shape({
      query_string: PropTypes.string,
      operator: PropTypes.string,
      filter_on: PropTypes.string,
      filter: PropTypes.string,
      vln: PropTypes.bool,
    })).isRequired,
    formsetDatasetsFormData: PropTypes.shape({
      datasets: PropTypes.arrayOf(PropTypes.any),
    }),
    formsetGlobalFiltersData: PropTypes.shape({}).isRequired,
    formsetErrors: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
    extraFieldNames: PropTypes.arrayOf(PropTypes.string),
    languages: PropTypes.shape(),
  }

  static defaultProps = {
    formsetName: 'default',
    formsetDatasetsFormData: {},
    extraFieldNames: [],
    languages: {},
  }

  /**
   * Upon being initialized with `formsetData` and `formsetErrors`,
   * which are provided from the rendered template on the basis
   * of previously-submitted form data, the constructor will
   * build an initial state consisting of:
   *
   * - `forms`, a simple list of unique identifiers
   * - `formsetIndexedDatasets`, the form data for each form,
   *   indexed by the unique identifier from `forms`
   * - `formsetIndexedErrors`, the errors for each form,
   *   indexed by the unique identifier from `forms`
   * - `formsetGlobalFiltersData`, the form data for filters
   *   applied to the formset as a whole, as determined
   *   by the value of `globalFiltersComponents`
   *
   * After being consumed, `formsetData` and `formsetErrors` are not used.
   */
  constructor(props) {
    super(props);
    const {
      formsetData,
      formsetDatasetsFormData,
      formsetGlobalFiltersData,
      formsetErrors,
      extraFieldNames,
    } = props;

    /*
      Construct the list of forms by invoking `uuid` n times,
      where n == the initial formset's count or 1.
    */
    const forms = _.times(
      formsetData.length || 1,
      uuid4,
    );

    /*
      Construct a single-key object with the `form` uuid
      as the key, then roll them all up together into one
      big object.
    */
    const formsetIndexedDatasets = _.reduce(
      _.map(
        forms,
        (uniqueId, i) => {
          const dataset = formsetData[i] || {};

          return {
            [uniqueId]: _.defaults(
              dataset,
              ..._.map(extraFieldNames, (fieldName) => ({ [fieldName]: !!dataset[fieldName] })),
              {
                query_string: '',
                operator: 'and',
                filter_on: (this.filterableFields || [[]])[0][0],
                filter: this.defaultFilter,
              },
              ..._.map(extraFieldNames, (fieldName) => ({ [fieldName]: false })),
            ),
          };
        },
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
      formsetDatasetsFormData,
      formsetIndexedDatasets,
      formsetIndexedErrors,
      formsetGlobalFiltersData,
    };
  }

  get hasLanguageConfig() {
    return !_.isEmpty(this.props.languages);
  }

  get selectedLanguageConfig() {
    return (
      !_.isEmpty(this.state)
      && this.props.languages[this.state.formsetDatasetsFormData.dataset]
    ) || _.chain(this.props.languages).toArray().head().value();
  }

  get filterableFields() {
    if (this.hasLanguageConfig) {
      return makeFilterableFields(
        this.selectedLanguageConfig.filterable_fields,
        this.selectedLanguageConfig.elasticsearch_fields,
      );
    }

    return this.props.formsetConfig.filterable_fields;
  }

  get controlledVocabFields() {
    if (this.hasLanguageConfig) {
      return makeControlledVocabFields(this.selectedLanguageConfig.controlled_vocab_fields);
    }

    return this.props.formsetConfig.controlled_vocab_fields;
  }

  get textSearchFields() {
    if (this.hasLanguageConfig) {
      return _.map(this.selectedLanguageConfig.elasticsearch_fields, ({ field }) => field);
    }

    return this.props.formsetConfig.text_search_fields;
  }

  get languageChoices() {
    if (this.hasLanguageConfig) {
      return _.keys(this.props.languages);
    }

    return [];
  }

  get isControlled() {
    return controlledVocabCheck(this.controlledVocabFields);
  }

  /*
    Check whether the first filterable field is a controlled
    vocab field. This is used to determine whether "exactly equals"
    or "begins with" is used as the default filter.
  */
  get firstIsControlled() {
    return _.includes(
      _.keys(this.controlledVocabFields),
      (this.filterableFields || [[]])[0][0],
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

    Similarly, if the field-value pair is part of a "text search"
    (which will normally be handled via the search engine), it
    will force the choice of `filter` to the special value
    "text search". If the previous value of the filter had
    this, it will unset it if a non-text-search value is picked.
  */
  onChangeFieldFrom = (uniqueId) => (field, eKey = 'value') => ({ target }) => {
    this.setState((state) => ({
      formsetIndexedDatasets: {
        ...state.formsetIndexedDatasets,
        [uniqueId]: {
          ...state.formsetIndexedDatasets[uniqueId],
          [field]: target[eKey],
          ...(
            (field === 'filter_on' && this.isControlled(target[eKey])) ? {
              filter: 'exactly_equals',
            } : {}
          ),
          ...(
            (field === 'filter_on' && this.isTextSearch(target[eKey])) ? {
              filter: 'text_search',
            } : {}
          ),
          ...(
            (field === 'filter_on'
              && state.formsetIndexedDatasets[uniqueId].filter === 'text_search'
              && !this.isTextSearch(target[eKey])
            ) ? {
                filter: this.defaultFilter,
              } : {}
          ),
        },
      },
    }));
  }

  onChangeGlobalField = (fieldName, eKey = 'value') => ({ target }) => {
    this.setState((state) => ({
      formsetGlobalFiltersData: {
        ...state.formsetGlobalFiltersData,
        [fieldName]: target[eKey],
      },
    }));
  }

  isTextSearch = (fieldname) => _.includes(this.textSearchFields, fieldname)

  removeFilter = (uniqueId) => () => {
    this.setState((state) => ({
      forms: _.filter(state.forms, (form) => uniqueId !== form),
      formsetIndexedDatasets: _.omit(state.formsetIndexedDatasets, uniqueId),
      formsetIndexedErrors: _.omit(state.formsetIndexedErrors, uniqueId),
    }));
  }

  addFilter = (e) => {
    e.preventDefault();
    const newUniqueId = uuid4();
    this.setState((state) => ({
      forms: [...state.forms, newUniqueId],
      formsetIndexedDatasets: {
        ...state.formsetIndexedDatasets,
        [newUniqueId]: {
          operator: 'and',
          filter_on: (this.filterableFields || [[]])[0][0],
          filter: this.defaultFilter,
          query_string: '',
        },
      },
      formsetIndexedErrors: {
        ...state.formsetIndexedErrors,
        [newUniqueId]: {},
      },
    }));
  }

  extraFilterComponents = () => <></>

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
          this.hasLanguageConfig
            ? (
              <div className="form-group">
                <label
                  className="small search-form__filters-label"
                  htmlFor="id_form-dataset"
                >
                  {`${gettext('Diccionario')}`}
                </label>
                <div className="input-group">
                  <select
                    name="dataset"
                    className="custom-select search-form__select"
                    id="id_form-dataset"
                    value={this.state.formsetDatasetsFormData.dataset}
                    onChange={({ target }) => {
                      this.setState({
                        formsetDatasetsFormData: { dataset: target.value },
                      });
                    }}
                  >
                    {
                      _.map(
                        this.props.languages,
                        ({ label, code }) => <option value={code}>{ label }</option>,
                      )
                    }
                  </select>
                </div>
              </div>
            )
            : null
        }

        {
          this.state.forms.map((uniqueId, i) => (
            <QueryBuilderForm
              i={i}
              formsetName={this.props.formsetName}
              defaultFilter={this.defaultFilter}
              key={uniqueId}
              controlledVocabFields={this.controlledVocabFields}
              dataset={this.state.formsetIndexedDatasets[uniqueId]}
              errors={this.state.formsetIndexedErrors[uniqueId]}
              filterableFields={this.filterableFields}
              onChangeFieldFrom={this.onChangeFieldFrom(uniqueId)}
              removeFilter={this.removeFilter(uniqueId)}
              textSearchFields={this.textSearchFields}
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
          <button
            className="btn btn-primary float-right"
            id="add-filter"
            onClick={this.addFilter}
            type="button"
          >
            {`${gettext('Agregar filtro')}`}
          </button>
        </div>
      </div>
    );
  }
}
