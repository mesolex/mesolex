import React from 'react';
import PropTypes from 'prop-types';
import classnames from 'classnames';
import _ from 'lodash';
import Octicon from 'react-component-octicons';

const SearchForm = ({
  i,
  formsetData,
  errors,
  onChangeFieldFrom,
  removeFilter,
}) => (
  <div className="form-group">
    <div className="input-group">
      <div className="input-group-prepend">
        <select
          name={`form-${i}-operator`}
          className="custom-select"
          id={`id_form-${i}-operator`}
          value={formsetData[`form-${i}-operator`]}
          onChange={onChangeFieldFrom(`form-${i}-operator`)}
        >
          <option value="and">{i === 0 ? 'does' : 'and'}</option>
          {i === 0 ? null : <option value="or">or</option>}
          <option value="and_n">{i === 0 ? 'does not' : 'and not'}</option>
          {i === 0 ? null : <option value="or_n">or not</option>}
        </select>
        <select
          name={`form-${i}-filter_on`}
          className="custom-select"
          id={`id_form-${i}-filter_on`}
          value={formsetData[`form-${i}-filter_on`]}
          onChange={onChangeFieldFrom(`form-${i}-filter_on`)}
        >
          <option value="headword">Entrada</option>
        </select>
        <select
          name={`form-${i}-filter`}
          className="custom-select"
          id={`id_form-${i}-filter`}
          value={formsetData[`form-${i}-filter`]}
          onChange={onChangeFieldFrom(`form-${i}-filter`)}
        >
          <option value="begins_with">Empieza con</option>
          <option value="ends_with">Termina con</option>
          <option value="contains">Contiene</option>
          <option value="exactly_equals">Es exactamente igual a</option>
          <option value="regex">Expresión regular</option>
        </select>
      </div>
      <input
        name={`form-${i}-query_string`}
        className={classnames(
          'form-control',
          { 'is-invalid': (errors.query_string || []).length },
        )}
        id={`id_form-${i}-query_string`}
        type="text"
        value={formsetData[`form-${i}-query_string`]}
        onChange={onChangeFieldFrom(`form-${i}-query_string`)}
      />
      {
        i > 0 ?
          <div className="input-group-append">
            <button
              type="button"
              className="btn btn-outline-secondary"
              onClick={removeFilter}
            >
              <Octicon name="x" />
            </button>
          </div> :
          null
      }
      {
        (errors.query_string || []).length ?
          errors.query_string.map(error => (
            <div className="invalid-feedback">
              {error}
            </div>
          )) :
          null
      }
    </div>
  </div>
);

SearchForm.propTypes = {
  i: PropTypes.number.isRequired,
  formsetData: PropTypes.shape.isRequired,
  errors: PropTypes.shape.isRequired,
  onChangeFieldFrom: PropTypes.func.isRequired,
  removeFilter: PropTypes.func.isRequired,
};

export default class SearchFormSet extends React.Component {
  static propTypes = {
    formsetData: PropTypes.shape.isRequired,
    formsetErrors: PropTypes.shape.isRequired,
  }

  constructor(props) {
    super(props);
    const { formsetData, formsetErrors } = props;
    this.state = {
      formsetData,
      formsetErrors,
    };
  }

  onClickAddFilter = (e) => {
    e.preventDefault();
    this.setState(prevState => ({
      formsetData: {
        ...prevState.formsetData,
        'form-TOTAL_FORMS': (
          (parseInt(this.state.formsetData['form-TOTAL_FORMS'], 10) || 1) + 1
        ),
      },
    }));
  }

  onChangeFieldFrom = field => (e) => {
    const { target: { value } } = e;
    this.setState(prevState => ({
      formsetData: {
        ...prevState.formsetData,
        [field]: value,
      },
    }));
  }

  /*
    To remove a filter, inspect the keys on the form data and write
    a new state object by keeping key-value pairs whose key is "less than"
    the index (or has no index), throwing out the key-value pair
    corresponding to the index, and keeping decremented versions of
    key-value pairs whose key contains an index higher than i.
    Also decrement the "total forms" value.
  */
  removeFilter = i => () => {
    const formsetData = _.reduce(
      { ...this.state.formsetData },
      (acc, value, key) => {
        /*
          If this key-value pair is the "total forms" stat,
          decrement the value in the accumulator and move on.
        */
        if (key === 'form-TOTAL_FORMS') {
          acc[key] = value - 1;
          return acc;
        }

        /*
          Otherwise, start trying to find and use the index
          from the key.
        */
        const matchDigits = key.match(/\d+/g);
        /*
          No matches for digits => bail now, keeping the key-value pair.
        */
        if (!matchDigits) {
          acc[key] = value;
          return acc;
        }
        /*
          Otherwise, grab the first match (hopefully the only match,
          really!) and parse it.
        */
        const [keyIndex] = matchDigits;
        const keyNum = parseInt(keyIndex, 10);

        if (i === keyNum) {
          /*
            Is this the pair corresponding to the current index? If so,
            toss it.
          */
          return acc;
        } else if (i < keyNum) {
          /*
            Is this a pair whose key is "after" the current index?
            Decrement the index in its key name and keep it.
          */
          acc[key.replace(/\d+/g, `${keyNum - 1}`)] = value;
          return acc;
        }

        /*
          Otherwise (i.e. if this is a pair whose hey is "before"
          the current index), just keep it unchanged.
        */
        acc[key] = value;
        return acc;
      },
      {},
    );

    this.setState(prevState => ({
      ...prevState,
      formsetData,
    }));
  }

  render() {
    const count = (parseInt(this.state.formsetData['form-TOTAL_FORMS'], 10) || 1);
    return (
      <div>
        <input name="form-TOTAL_FORMS" value={count} id="id_form-TOTAL_FORMS" type="hidden" />
        <input name="form-INITIAL_FORMS" value="0" id="id_form-INITIAL_FORMS" type="hidden" />
        <input name="form-MIN_NUM_FORMS" value="0" id="id_form-MIN_NUM_FORMS" type="hidden" />
        <input name="form-MAX_NUM_FORMS" value="1000" id="id_form-MAX_NUM_FORMS" type="hidden" />

        { _.times(count, i => (
          <SearchForm
            i={i}
            formsetData={this.state.formsetData}
            errors={this.state.formsetErrors[i] || {}}
            onChangeFieldFrom={this.onChangeFieldFrom}
            removeFilter={this.removeFilter(i)}
          />
        )) }

        <div className="form-group">
          <button type="submit" className="btn btn-success">Buscar</button>
          <button className="btn btn-primary float-right" id="add-filter" onClick={this.onClickAddFilter}>Agregar filtro</button>
        </div>
      </div>
    );
  }
}
