import React from 'react'

import TablePagination from '@material-ui/core/TablePagination'

import { makeTemplate } from '../../util/makeTemplate'
import {findMatchedSchema} from '../../util/objectMatch'
import { diffList } from "../../util/helper/misc"
import { connect } from "react-redux";
import { fetchMetaData } from "../../util/redux/actions";
import { URLFormatter, ReadURLParams } from "../../util/helper/misc";

import DataTable from "./DataTable"

export const value_by_type = {
  text: ({label, prop, data}) => {
    let val = makeTemplate(prop.text, data)
    if (val === 'undefined'){
      return null
    } else {
      return val
    }
  },
  'img': ({label, prop, data }) => {
    const src = makeTemplate(prop.src, data)
    const alt = makeTemplate(prop.alt, data)
    if ( alt === 'undefined'){
      return null
    } else {
      return {alt, src}
    }
  },
}

export const get_card_data = (data, schemas, highlight=undefined) => {
  const schema = findMatchedSchema(data, schemas)
  if (schema!==null){
    const { properties } = schema
    let scores= {}
    let tags = []
    const processed = {id: data.id}
    for (const label of Object.keys(properties)){
      const prop = properties[label]
      const val = value_by_type[prop.type]({label, prop, data, highlight})
      if (prop.name){
        processed.name = val || data.id
      }else if (prop.subtitle){
        if (val!==null) processed.subtitle = val
      }else if (prop.icon){
        if (val!==null){
          processed.icon = {...val}
        }
      }else if (prop.score){
        if (val!==null) scores[label] = {
          label,
          value: val,
          icon: prop.MDI_Icon || 'mdi-star'
        }
      }else {
        if ( val !== null) tags = [...tags, {
          label,
          value: val,
          icon: prop.MDI_Icon || 'mdi-arrow-top-right-thick',
          priority: prop.priority
        }]
      }
    }
    tags = tags.sort((a, b) => a.priority - b.priority)
    if (Object.keys(scores).length>0) processed.scores = scores
    processed.tags = tags || []
    return {original: data, processed}
  }
}

const mapStateToProps = state => {
  return {
    schemas: state.serverSideProps.schemas,
    data: state.metadata_results[state.current_table],
    ui_values:state.serverSideProps.ui_values,
    current_table: state.current_table,
    loading: state.loading,
    completed: state.completed,
    paginating: state.paginating,
    count: state.table_count[state.current_table],
    reverse_preferred_name: state.reverse_preferred_name,
    preferred_name: state.serverSideProps.ui_values.preferred_name,
  }
}

class MetadataSearchResults extends React.Component {
  constructor(props){
    super(props)
    this.state = {
      collection: [],
      sorted: null,
      page:0,
      perPage:10,
    }
  }

  componentDidMount = () => {
    const coll = this.props.data || []
    const collection = coll.map(data=>get_card_data(data, this.props.schemas))
    this.setState({
      collection
    })
  }

  sortBy = (sorted) => {
    const collection = this.props.collection
    collection = collection.sort((a, b) => a.processed.scores[sorted].value - b.processed.scores[sorted].value)
    this.setState({
      collection,
      sorted,
    })
  }

  onChipClick = (value) => {
    const search = [...this.props.search, value]
  }

  handleChangeRowsPerPage = (e) => {
    const param_str = this.props.location.search
    this.setState({
      perPage: e.target.value,
    }, () => {
      const {page, perPage} = this.state
      const param_str = this.props.location.search
      let params = ReadURLParams(param_str, this.props.reverse_preferred_name)
      params = {
        ...params,
        limit: perPage,
        skip: page * perPage
      }
      const current_table = this.props.match.params.table || this.props.preferred_name["signatures"]
      const query = URLFormatter({...params, current_table})
      this.props.history.push({
        pathname: `/MetadataSearch/${current_table}`,
        search: `?q=${query}`
      })
    })
  }

  handleChangePage = (event, page) => {
    this.setState({
      page,
    }, () => {
      const {page, perPage} = this.state
      const param_str = this.props.location.search
      let params = ReadURLParams(param_str, this.props.reverse_preferred_name)
      params = {
        ...params,
        limit: perPage,
        skip: page * perPage
      }
      const current_table = this.props.match.params.table || this.props.preferred_name["signatures"]
      const query = URLFormatter({...params, current_table})
      this.props.history.push({
        pathname: `/MetadataSearch/${current_table}`,
        search: `?q=${query}`
      })
    })
  }



  componentDidUpdate = (prevProps) => {
    const old = prevProps.data || []
    const curr = this.props.data || []
    const old_list = old.map(i=>i.id)
    const new_list = curr.map(i=>i.id)
    if (diffList(old_list, new_list)){
      const collection = this.props.data.map(data=>get_card_data(data, this.props.schemas))
      this.setState({
        collection,
      })
    }
  }

  render = () => (
    <React.Fragment>
      <DataTable schemas={this.props.schemas}
        ui_values={this.props.ui_values}
        {...this.state}
        loaded={this.props.completed && !this.props.loading && !this.props.paginating}
        sortingFunction={this.sortBy}
        current_table={this.props.reverse_preferred_name[this.props.match.params.table]}
      />
      <div align="right">
        <TablePagination
          page={this.state.page}
          rowsPerPage={this.state.perPage}
          count={this.props.count || 0}
          onChangePage={(event, page) => this.handleChangePage(event, page)}
          onChangeRowsPerPage={this.handleChangeRowsPerPage}
          component="div"
        />
      </div>
    </React.Fragment>

  )
}

export default connect(mapStateToProps)(MetadataSearchResults)
