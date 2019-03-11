import React from "react";
import { Redirect } from 'react-router';
import { Admin,
         ArrayField,
         ChipField,
         Datagrid,
         DisabledInput,
         Edit,
         EditButton,
         List,
         LongTextInput,
         ReferenceField,
         Resource,
         SimpleForm,
         SingleFieldList,
         TextField,
         TextInput,
         UrlField,
         AUTH_LOGIN,
         AUTH_LOGOUT,
         AUTH_ERROR,
         AUTH_CHECK,
         GET_ONE } from 'react-admin';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardHeader from '@material-ui/core/CardHeader';
import BlurOn from '@material-ui/icons/BlurOn';
import Fingerprint from '@material-ui/icons/Fingerprint';
import LibraryBooks from '@material-ui/icons/LibraryBooks';

import { base_url, fetch_meta } from '../../util/fetch/meta';
import { fetchJson } from '../../util/fetch/fetch';

import loopbackProvider from './loopback-provider';
import { BooleanField,
         PostFilter,
         LibraryAvatar,
         Description,
         SplitChip,
         TagsField } from './signaturehelper';
import { Dashboard } from './dashboard';


class AdminView extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      library_fields: null,
      entity_fields: null,
      signature_fields: null,
      LibNum: 140,
      LibraryNumber: "Loading...",
      SignatureNumber: "Loading...",
      EntityNumber: "Loading...",
      signature_counts: null,
      selected_db: "Libraries",
      selected_field: "Assay",
      signature_allfields: null,
      stats: null,
      status: null,
      controller: null,
      stat_controller: null,
      token: null,
      uid: "308de661-d3e2-11e8-8fe6-787b8ad942f3",
      hash: window.location.hash,
    }
    this.filterHandler = this.filterHandler.bind(this);
    this.hashChangeHandler = this.hashChangeHandler.bind(this);
    this.LibraryList = this.LibraryList.bind(this);
    this.LibraryEdit = this.LibraryEdit.bind(this);
    this.EntityList = this.EntityList.bind(this);
    this.EntityEdit = this.EntityEdit.bind(this);
    this.SignatureList = this.SignatureList.bind(this);
    this.SignatureEdit = this.SignatureEdit.bind(this);
    this.httpClient = this.httpClient.bind(this);
    this.filterForm = this.filterForm.bind(this);
    this.authProvider = this.authProvider.bind(this);
    this.NotFound = this.NotFound.bind(this);
    this.handleSelectDB = this.handleSelectDB.bind(this);
    this.handleSelectField = this.handleSelectField.bind(this);
    this.dataProvider = loopbackProvider(base_url, this.httpClient);

  }

  // const httpClient = (url, options = {}) => {
  //   if (!options.headers) {
  //       options.headers = new Headers({ Accept: 'application/json' });
  //   }
  //   const token = localStorage.getItem('token');
  //   options.headers.set('Authorization', `Basic ${this.state.token}`);
  //   return fetchUtils.fetchJson(url, options);
  // }

  filterForm(props){
    if(this.state.token===null){
      return false
    }else{
      return(
        <PostFilter
          libnum={this.state.LibNum}
          filterhandler={this.filterHandler}
        />
      )
    }
  }

  handleSelectDB(e){
    const selected = e.target.value
    let field=undefined
    let fields_loaded=undefined
    switch (selected) {
      case "Libraries":
        field="Assay"
        fields_loaded= this.state.library_fields===null? false: true
        break;
      case "Signatures":
        field="Assay"
        fields_loaded= this.state.signature_allfields===null? false: true
        break;
      case "Entities":
        field="Taxon_ID"
        fields_loaded= this.state.entity_fields===null? false: true
        break;
    }
    this.setState({
      selected_db: selected,
      selected_field: field,
      stats: null,
    }, () => {
      if(fields_loaded){
        this.fetch_stats()
      }
    })
  }

  handleSelectField(e){
    const field = e.target.value
    this.setState({
      selected_field: field,
      stats: null,
    }, () => {
      this.fetch_stats()
    })
  }

  LibraryList(props) {
    return (
      <List 
        title="Libraries"
        {...props}>
        <Datagrid>
          <LibraryAvatar
            source={"meta.Library_name"}
            title={"Library"}
            label={"Library"}
            textAlign="center"
          />
          <TextField
            source="id"
          />
          {Object.keys(this.state.library_fields).map(function(k){
            if (k.includes("Link") || k.includes("URL")){
              return(
                <UrlField key={k}
                  label={k.replace(/_/g," ")}
                  source={"meta." + k}
                />
              )
            }
            else if(["Readout","Assay"].includes(k)){
              return(
                <ChipField
                  key={k}
                  label={k.replace(/_/g," ")}
                  source={"meta." + k}
                />
              )
            }
            else if(k==="Weighted"){
              return(
                <BooleanField
                  key={k}
                  label={k.replace(/_/g," ")}
                  field={k}
                  TrueValue={"True"}
                />
              )
            }
            else if (["Perturbation_Type","Organism"].includes(k)){
              return(
                <SplitChip
                  key={k}
                  label={k.replace(/_/g," ")}
                  source={"meta." + k}
                  field={k}
                />
              )
            }
            else if (!["Icon","Library_name","Description","Spec","$validator"].includes(k)){
              return(
                <TextField
                  key={k}
                  label={k.replace(/_/g," ")}
                  source={"meta." + k}
                />
              )
            }
          })}
          <Description
            source={"meta.Description"}
            title={"Description"}
            label={"Description"}
          />
          <EditButton />
        </Datagrid>
      </List>
    )
  }

  LibraryEdit(props){
    return(
      <Edit {...props}>
        <SimpleForm>
          <DisabledInput source="id" />
          {Object.keys(this.state.library_fields).map(function(k){
            if(k!=="Description"){
              return(
                <TextInput
                  key={k}
                  label={k.replace(/_/g," ")}
                  source={"meta." + k}
                />
              )
            }
          })}
          <LongTextInput
            key={"Description"}
            label={"Description"}
            source={"meta.Description"}
          />
        </SimpleForm>
      </Edit>
    )
  }

  SignatureList(props){
    return(
      <List
        {...props}
        filters={this.filterForm(props)}
        filterDefaultValues={{"library": this.state.uid}}
        title="Signatures"
      > 
        <Datagrid>
          <TextField
            source="id"
          />
          <ReferenceField
            source="library"
            reference="libraries"
            linkType={false}
          >
            <TextField 
              source="meta.Library_name" 
              style={{width: 150}}/>
          </ReferenceField>
          {this.state.signature_fields.map(function(k){
            if(["Gene", "Disease", "Cell_Line", "Tissue", "Small_Molecule"].includes(k)){
              return(
                <ArrayField 
                  key={k}
                  label={k.replace(/_/g," ")}
                  source={"meta." + k}
                >
                  <SingleFieldList>
                    <ChipField source="Name" />
                  </SingleFieldList>
                </ArrayField>
              )
            }else if (["distil_id", "qc_tag", "pert_ids", "ctrl_ids"].includes(k)){
              return(
                <TagsField
                  key={k}
                  label={k.replace(/_/g," ")}
                  source={"meta." + k}
                  field={k}
                />
              )
            }else if(k==="Accession"){
              return(
                <ArrayField 
                  key={k}
                  label={k.replace(/_/g," ")}
                  source={"meta." + k}
                >
                  <SingleFieldList>
                    <ChipField source="ID" />
                  </SingleFieldList>
                </ArrayField>
              )
            }
            else if(k=="Description"){
              return(
                <Description
                  source={"meta.Description"}
                  title={"Description"}
                  label={"Description"}
                />
              )
            }
            else if(k!=="$validator"){
              return(
                <TextField
                  key={k}
                  label={k.replace(/_/g," ")}
                  source={"meta." + k}
                />
              )
            }
          })}
          <EditButton />
        </Datagrid> 
      </List>
    )
  }

  SignatureEdit(props){
    return(
      <Edit {...props}>
        <SimpleForm>
          <DisabledInput source="id" />
          {this.state.signature_fields.map(function(k){
            if(["distil_id", "qc_tag", "pert_ids", "ctrl_ids",
                "Gene", "Disease", "Cell_Line", "Tissue",
                "Small_Molecule", "Accession"].includes(k)){
              return(
                <LongTextInput
                  key={k}
                  label={k.replace(/_/g," ")}
                  source={"meta." + k}
                  format={v=>JSON.stringify(v, null, 2)}
                  parse={v=>JSON.parse(v)}
                />
              )
            }
            else{
              return(
                <TextInput
                  key={k}
                  label={k.replace(/_/g," ")}
                  source={"meta." + k}
                />
              )
            }
          })}
        </SimpleForm>
      </Edit>
    )
  }

  EntityList(props) {
    return (
      <List 
        title="Entities"
        {...props}>
        <Datagrid>
          <TextField
            source="id"
          />
          {Object.keys(this.state.entity_fields).map(function(k){
            if (k==="Synonyms"){
              return(
                <TagsField
                  key={k}
                  label={k.replace(/_/g," ")}
                  source={"meta." + k}
                  field={k}
                />
              )
            }
            else if(k!=="$validator"){
              return(
                <TextField
                  key={k}
                  source={"meta." + k}
                  label={k.replace(/_/g," ")}
                />
              )
            }
          })}
          <EditButton />
        </Datagrid>
      </List>
    )
  }

  EntityEdit(props){
    return(
      <Edit {...props}>
        <SimpleForm>
          <DisabledInput source="id" />
          {Object.keys(this.state.entity_fields).map(function(k){
            if (k==="Synonyms"){
              return(
                <LongTextInput
                  key={k}
                  label={k.replace(/_/g," ")}
                  source={"meta." + k}
                  format={v=>JSON.stringify(v, null, 2)}
                  parse={v=>JSON.parse(v)}
                />
              )
            }
            else{
              return(
                <TextInput
                  key={k}
                  label={k.replace(/_/g," ")}
                  source={"meta." + k}
                />
              )
            }
          })}
        </SimpleForm>
      </Edit>
    )
  }

  NotFound(props) {
    if(this.state.token){
      return(
        <Card>
          <CardHeader title="Oop! I don't know what you are looking for" />
          <CardContent>Check your link, please.</CardContent>
        </Card>
      )
    }else{
      return <Redirect to='/' />
    }
  }

  async fetch_stats(){
    if(this.state.stat_controller !== null) {
      this.state.stat_controller.abort()
      }
    try {
      const stat_controller = new AbortController()
      this.setState({
        stat_controller: stat_controller,
      })
      const headers = {'Authorization': `Basic ${this.state.token}`}
      const url = '/' + this.state.selected_db.toLowerCase() +
                  '/value_count?depth=2&filter={"fields":["' +
                  this.state.selected_field +'"]}'
      const { response: stats} = await fetch_meta(url,
                                                  undefined,
                                                  stat_controller.signal,
                                                  headers)
      let stat_vals = undefined
      if(["Cell_Line", "Disease", "Gene", "Phenotype", "Small_Molecule", "Tissue", "Virus"].includes(this.state.selected_field)){
        stat_vals = stats[this.state.selected_field + ".Name"]
      }else if(this.state.handleSelectField === "Accession"){
        stat_vals = stats[this.state.selected_field + ".ID"]
      }else{
        stat_vals = stats[this.state.selected_field]
      }
      this.setState({
        // signature_fields: signature_fields,
        stats: stat_vals
      });
    } catch(e) {
      if(e.code !== DOMException.ABORT_ERR) {
        this.setState({
          stat_status: ''
        })
      }
    }
  }

  async filterHandler(e){
      // console.log(e)
      // this.setState({
      //   SignatureList: <LinearProgress />
      // }, async () =>{
      //   const uid = Object.values(e).slice(0,36).join('')
      //   const { response: signature_fields} = await fetch_meta('/signatures/key_count?filter={"where":{"library":"'+uid+'"}}')
      //   this.get_signatures(signature_fields)
      // });
      // console.log(window.location.hash)
      // console.log(this.state.hash)
      if(this.state.controller !== null && decodeURI(window.location.hash) !== this.state.hash) {
        if(this.state.hash.includes("/signatures")){
          this.setState({
            hash: decodeURI(window.location.hash)
          })
        }
        this.state.controller.abort()
      }
      try {
        const controller = new AbortController()
        this.setState({
          status: 'Searching...',
          controller: controller,
        })
        let uid = ""
        if(e.hasOwnProperty("uid")){
          uid = e.uid
        }else{
          uid = Object.values(e).slice(0,36).join('')
        }
        const headers = {'Authorization': `Basic ${this.state.token}`}
        const { data: signature_fields} = this.dataProvider(GET_ONE, "libraries", {id: uid})
        // await fetch_meta('/libraries' + uid,
        //                                                       undefined,
        //                                                       controller.signal,
        //                                                       headers)
        this.setState({
          // signature_fields: signature_fields,
          signature_fields: signature_fields["Signature_keys"],
          uid: uid
        });
      } catch(e) {
        if(e.code !== DOMException.ABORT_ERR) {
          this.setState({
            status: e + ''
          })
        }
      }
  }

  hashChangeHandler(){
    const hash = decodeURI(window.location.hash)
    this.setState({
      hash: hash
    })
    if (hash.includes('/signatures?filter={"library"')){
      const hashparts = hash.split('"')
      if(hashparts.length > 4){
        const uid = hashparts[3]
        // const params = hashparts[4].split("&")
        // const page = params.filter((l)=>(l.includes("page")))[0].split("=")[1]
        // this.setState({
        //   urlpage: page
        // })
        this.filterHandler(uid)
      }
    }
  }

  async fetch_libfields() {
    const headers = {'Authorization': `Basic ${this.state.token}`}
    const { response: library_fields } = await fetch_meta('/libraries/key_count',
                                                          undefined,
                                                          undefined,
                                                          headers)
    this.setState({
      LibNum: library_fields.$validator,
      library_fields: library_fields,
      LibraryNumber: library_fields.$validator,
    },()=>{
      if(this.state.selected_db=="Libraries"){
        this.fetch_stats()
      }
    })
  }

  async fetch_sigfields() {
    const headers = {'Authorization': `Basic ${this.state.token}`}
    const { data: signature_fields} = await this.dataProvider(GET_ONE, "libraries", {id: this.state.uid})
    console.log(signature_fields)
    this.setState({
      signature_fields: signature_fields["Signature_keys"],
    })
    const { response: signature_allfields} = await fetch_meta('/signatures/key_count',
                                                          undefined,
                                                          undefined,
                                                          headers)
    this.setState({
      signature_allfields: signature_allfields,
      SignatureNumber: signature_allfields.$validator,
    },()=>{
      if(this.state.selected_db=="Signatures"){
        this.fetch_stats()
      }
    })
  }

  async fetch_sigallfields(){
    const headers = {'Authorization': `Basic ${this.state.token}`}
    const { response: signature_allfields} = await fetch_meta('/signatures/key_count',
                                                          undefined,
                                                          undefined,
                                                          headers)
    this.setState({
      signature_allfields: signature_allfields,
      SignatureNumber: signature_allfields.$validator,
    },()=>{
      if(this.state.selected_db=="Signatures"){
        this.fetch_stats()
      }
    })
  }

  async fetch_entityfields(){
    const headers = {'Authorization': `Basic ${this.state.token}`}
    const { response: entity_fields } = await fetch_meta('/entities/key_count',
                                                        undefined,
                                                        undefined,
                                                        headers)
    this.setState({
      entity_fields: entity_fields,
      EntityNumber: entity_fields.$validator,
    },()=>{
      if(this.state.selected_db=="Entities"){
        this.fetch_stats()
      }
    })
  }

  async fetch_sigstats() {
    const headers = {'Authorization': `Basic ${this.state.token}`}
    const { response: signature_counts} = await fetch_meta('/signatures/value_count?depth=2&filter={"fields":["Gene", "Cell_Line", "Small_Molecule", "Tissue", "Disease"]}',
                                                          undefined,
                                                          undefined,
                                                          headers)
    const sig_counts = Object.keys(signature_counts).filter(key=>key.includes(".Name"))
                                                    .reduce((stat_list, k)=>{
                                                    stat_list.push({name: k.replace(".Name", ""),
                                                                    counts:Object.keys(signature_counts[k]).length})
                                                    return(stat_list) },
                                                    [])

    sig_counts.sort((a, b) => a.name > b.name);
    this.setState({
      signature_counts: sig_counts,
    })
  }

  componentDidMount() {
    window.addEventListener("hashchange", this.hashChangeHandler);
    if (this.state.token){
      this.fetch_libfields()
      this.fetch_sigfields()
      this.fetch_sigstats()
      this.fetch_sigallfields()
      this.fetch_entityfields()
      this.fetch_stats()
    }
  }
  httpClient(url, options = {}) {
    if(!(options.hasOwnProperty("method"))){
      const link = decodeURI(url).split("%2C")
      const url_params = link.filter((l)=> (l.includes("skip")||l.includes("limit")))
                             .map((l)=>(l.split("%3A")[1]));
      const page = (url_params[0]/url_params[1]) + 1
      this.setState({
        apipage: page
      })
    }

    if (this.state.controller!== null)
      options["signal"] = this.state.controller.signal

    if (options.headers === undefined)
      options.headers = new Headers({ Accept: 'application/json' });
    
    const token = (options.token || this.state.token)
    console.log(options)
    options.headers.set('Authorization', `Basic ${token}`);
    
    return fetchJson(url, options);
  }

  async authProvider(type, params) {
    if (type === AUTH_LOGIN) {
      const token = Buffer.from(`${params.username}:${params.password}`).toString('base64')
      const headers = {'Authorization': `Basic ${token}`}
      const { response: auth_res} = await fetch_meta('/libraries/'+this.state.uid,
                                                     undefined, undefined, headers)
      if ((auth_res.hasOwnProperty("error")) && (auth_res.error.statusCode >= 400 && auth_res.error.statusCode < 500)){
        return Promise.reject()
      }else{
        this.setState({ token: token })
        // Load column names
        if(this.state.library_fields===null){
          this.fetch_libfields()
        }
        if(this.state.signature_fields===null){
          this.fetch_sigfields()
        }
        if(this.state.entity_fields===null){
          this.fetch_entityfields()
        }
        if(this.state.signature_counts===null){
          this.fetch_sigstats()
        }
        if(this.state.signature_allfields===null){
          this.fetch_sigallfields()
        }
        if(this.state.stats===null){
          this.fetch_stats()
        }
        return Promise.resolve();
      }
    }else if (type === AUTH_LOGOUT) {
        this.setState({ token: null })
        return Promise.resolve();
    }else if (type === AUTH_ERROR) {
      if (params === 'DOMException: "The operation was aborted. "'){
        const status  = params.status;
        this.setState({ token: null })
        return Promise.reject()
      }else
        return Promise.resolve()
    }else if (type === AUTH_CHECK) {
      return this.state.token ? Promise.resolve() : Promise.reject();
    }
    return Promise.reject()
  }

  render() {
      return (
        <Admin title="Signature Commons Admin Page"
               dataProvider={this.dataProvider}
               authProvider={this.authProvider}
               dashboard={(props) => <Dashboard 
                                        LibraryNumber={this.state.LibraryNumber}
                                        SignatureNumber={this.state.SignatureNumber}
                                        EntityNumber={this.state.EntityNumber}
                                        signature_counts={this.state.signature_counts}
                                        entity_fields={this.state.entity_fields}
                                        library_fields={this.state.library_fields}
                                        signature_allfields={this.state.signature_allfields}
                                        selected_db={this.state.selected_db}
                                        selected_field={this.state.selected_field}
                                        handleSelectDB={this.handleSelectDB}
                                        handleSelectField={this.handleSelectField}
                                        stats={this.state.stats}
                                        {...props}/>}
               catchAll={this.NotFound}
        >
          {this.state.library_fields===null ? <div/>:
            <Resource
              name="libraries"
              list={this.LibraryList}
              edit={this.LibraryEdit}
              icon={LibraryBooks}
            />
          }
          {this.state.signature_fields===null ? <div/>:
            <Resource
              name="signatures"
              edit={this.SignatureEdit}
              list={this.SignatureList}
              icon={Fingerprint}
            />
          }
          {this.state.entity_fields===null ? <div/>:
            <Resource
              name="entities"
              edit={this.EntityEdit}
              list={this.EntityList}
              icon={BlurOn}
            />
          }
        </Admin>
      )
  }
}

export default AdminView
