import React from 'react'
import _ from 'lodash'

const SearchForm = ({ i }) => (
  <div className='form-group'>
    <div className='input-group'>
      <div className='input-group-prepend'>
        <select name={`form-${i}-operator`} className='custom-select' id={`id_form-${i}-operator`}>
          <option value='&amp;&amp;'>AND</option>
          <option value='||'>OR</option>
        </select>
        <select name={`form-${i}-filter_on`} className='custom-select' id={`id_form-${i}-filter_on`}>
          <option value='headword'>Headword</option>
        </select>
        <select name={`form-${i}-filter`} className='custom-select' id={`id_form-${i}-filter`}>
          <option value='begins_with'>Begins with</option>
          <option value='ends_with'>Ends with</option>
          <option value='contains'>Contains</option>
          <option value='exactly_equals'>Exactly equals</option>
        </select>
      </div>
      <input name={`form-${i}-query_string`} className='form-control' id={`id_form-${i}-query_string`} type='text' />
    </div>
  </div>
)

export default class SearchFormSet extends React.Component {
  constructor (props) {
    super(props)
    this.state = {
      count: 1
    }
  }

  onClickAddFilter = (e) => {
    e.preventDefault()
    this.setState(prevState => ({
      count: prevState.count + 1
    }))
  }

  render () {
    return (
      <div>
        { _.times(this.state.count, i => <SearchForm i={i} />) }

        <div className="form-group">
            <button type="submit" className="btn btn-success">Search</button>
            <button className="btn btn-primary float-right" id="add-filter" onClick={this.onClickAddFilter}>Add filter</button>
        </div>
      </div>
    )
  }
}
