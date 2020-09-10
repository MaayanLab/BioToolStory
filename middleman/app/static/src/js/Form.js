import React from 'react'
import PropTypes from 'prop-types'
import Form from '@rjsf/material-ui';
import fetch from 'node-fetch'
import { fetch_meta } from './util/fetch_meta'


const cache = {}

const getUrl = window.location;
const base_url = getUrl.protocol + "//" + getUrl.host + process.env.ROOT_PATH + "api"

export const fetch_cached_validator = async (url) => {
    if (cache[url]) return cache[url]
    // url = "https://raw.githubusercontent.com/MaayanLab/BioToolStory/master/validators/btools_tools.json"
    const m = /^\/@?dcic\/signature-commons-schema(\/v\d+)?(.*)$/.exec(url)
    if (m) {
        if (m[1] === undefined) {
          url = `https://raw.githubusercontent.com/dcic/signature-commons-schema/v1${m[2]}`
        } else {
          url = `https://raw.githubusercontent.com/dcic/signature-commons-schema${m[1]}${m[2]}`
        }
      }
    const { response } = await fetch_meta({
    endpoint: '/get_validator',
    body: {
        validator: {
        url,
        },
    },
    })
    cache[url] = response
    return cache[url]
}

export const resolveFormSchema = (validator) => {
    let formSchema = {"title": "Edit Metadata"}
    if (validator.allOf){
        const allOf = []
        for (const val of validator.allOf){
            if (val.properties){
                allOf.push(val)
            }
        }
        if (allOf.length > 1){
            formSchema["allOf"] = allOf
        } else{
            formSchema = {
                ...formSchema,
                ...allOf[0],
            }
        }
    }else if (validator.properties){
        formSchema = {...formSchema, ...val}
    } else {
        throw "Invalid Validator"
    }
    return formSchema
}

export default class MetadataForm extends React.Component {
    constructor(props){
        super(props)
        this.state = {
            schema: null
        }
    }
    componentDidMount = async () => {
        const url = this.props.data.meta["$validator"]
        const validator = await fetch_cached_validator(url)
        try {
            const schema = resolveFormSchema(validator)
            this.setState({schema})
        } catch (error) {
            console.error(error)
        }
    }

    render = () => {
        if (this.state.schema === null) return null
        const {data, ...rest} = this.props
        const formData = data.meta
        return <Form schema={this.state.schema}
                    formData={formData}
                    {...rest}
                />
    }
}

MetadataForm.propTypes = {
    // See prop types of InfoCard
    data: PropTypes.shape({
        id: PropTypes.string,
        meta: PropTypes.shape({
            $validator: PropTypes.string,
        })
    }),
    onChange: PropTypes.func,
    onSubmit: PropTypes.func,
    onError: PropTypes.func,
}