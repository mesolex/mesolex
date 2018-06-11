import React from 'react'
import classnames from 'classnames'
import _ from 'lodash'

const SearchForm = ({ i, formsetData, errors, onChangeFieldFrom }) => (
  <div className='form-group'>
    <div className='input-group'>
      <div className='input-group-prepend'>
        <select
          name={`form-${i}-operator`}
          className='custom-select'
          id={`id_form-${i}-operator`}
          value={formsetData[`form-${i}-operator`]}
          onChange={onChangeFieldFrom(`form-${i}-operator`)}
        >
          <option value='and'>and</option>
          <option value='or'>or</option>
          <option value='and_n'>and not</option>
          <option value='or_n'>or not</option>
        </select>
        <select
          name={`form-${i}-filter_on`}
          className='custom-select'
          id={`id_form-${i}-filter_on`}
          value={formsetData[`form-${i}-filter_on`]}
          onChange={onChangeFieldFrom(`form-${i}-filter_on`)}
        >
          <option value='headword'>Headword</option>
        </select>
        <select
          name={`form-${i}-filter`}
          className='custom-select'
          id={`id_form-${i}-filter`}
          value={formsetData[`form-${i}-filter`]}
          onChange={onChangeFieldFrom(`form-${i}-filter`)}
        >
          <option value='begins_with'>Begins with</option>
          <option value='ends_with'>Ends with</option>
          <option value='contains'>Contains</option>
          <option value='exactly_equals'>Exactly equals</option>
          <option value='regex'>Regular expression</option>
        </select>
      </div>
      <input
        name={`form-${i}-query_string`}
        className={classnames(
          'form-control',
          {'is-invalid': (errors.query_string || []).length},
        )}
        id={`id_form-${i}-query_string`}
        type='text'
        value={formsetData[`form-${i}-query_string`]}
        onChange={onChangeFieldFrom(`form-${i}-query_string`)}
      />
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
)

export default class SearchFormSet extends React.Component {
  constructor (props) {
    super(props)
    const { csrfToken, formsetData, formsetErrors } = props
    this.state = {
      csrfToken,
      formsetData,
      formsetErrors,
    }
  }

  onClickAddFilter = (e) => {
    e.preventDefault()
    this.setState(prevState => ({
      formsetData: {
        ...prevState.formsetData,
        'form-TOTAL_FORMS': (parseInt(this.state.formsetData['form-TOTAL_FORMS']) || 1) + 1
      }
    }))
  }

  onChangeFieldFrom = (field) => (e) => {
    const {target: {value}} = e;
    this.setState(prevState => ({
      formsetData: {
        ...prevState.formsetData,
        [field]: value,
      }
    }))
  }

  render () {
    const count = (parseInt(this.state.formsetData['form-TOTAL_FORMS']) || 1)
    return (
      <div>
        <input name="form-TOTAL_FORMS" value={count} id="id_form-TOTAL_FORMS" type="hidden" />
        <input name="form-INITIAL_FORMS" value="0" id="id_form-INITIAL_FORMS" type="hidden" />
        <input name="form-MIN_NUM_FORMS" value="0" id="id_form-MIN_NUM_FORMS" type="hidden" />
        <input name="form-MAX_NUM_FORMS" value="1000" id="id_form-MAX_NUM_FORMS" type="hidden" />
        <input name="csrfmiddlewaretoken" value={this.props.csrfToken} type="hidden" />

        { _.times(count, i => (
          <SearchForm
            i={i}
            formsetData={this.state.formsetData}
            errors={this.state.formsetErrors[i] || {}}
            onChangeFieldFrom={this.onChangeFieldFrom}
          />
        )) }

        <div className="form-group">
            <button type="submit" className="btn btn-success">Search</button>
            <button className="btn btn-primary float-right" id="add-filter" onClick={this.onClickAddFilter}>Add filter</button>
        </div>
      </div>
    )
  }
}
