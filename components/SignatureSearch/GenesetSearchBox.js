import React from 'react'
import { Switch, Route, Redirect } from 'react-router-dom'
import { call } from '../../util/call'

import ChipInput from 'material-ui-chip-input'
import { Set } from 'immutable'
import { connect } from "react-redux";
import Grid from '@material-ui/core/Grid';
import Chip from '@material-ui/core/Chip'
import { withStyles } from '@material-ui/core/styles'
import Avatar from '@material-ui/core/Avatar';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import { findSignature } from "../../util/redux/actions";

const example_geneset = 'UTP14A S100A6 SCAND1 RRP12 CIAPIN1 ADH5 MTERF3 SPR CHMP4A UFM1 VAT1 HACD3 RFC5 COTL1 NPRL2 TRIB3 PCCB TLE1 CD58 BACE2 KDM3A TARBP1 RNH1 CHAC1 MBNL2 VDAC1 TES OXA1L NOP56 HAT1 CPNE3 DNMT1 ARHGAP1 VPS28 EIF2S2 BAG3 CDCA4 NPDC1 RPS6KA1 FIS1 SYPL1 SARS CDC45 CANT1 HERPUD1 SORBS3 MRPS2 TOR1A TNIP1 SLC25A46 MAL EPCAM HDAC6 CAPN1 TNRC6B PKD1 RRS1 HP ANO10 CEP170B IDE DENND2D CAMK2B ZNF358 RPP38 MRPL19 NUCB2 GNAI1 LSR ADGRE2 PKMYT1 CDK5R1 ABL1 PILRB AXIN1 FBXL8 MCF2L DBNDD1 IGHMBP2 WIPF2 WFS1 OGFOD2 MAPK1IP1L COL11A1 REG3A SERPINA1 MYCBP2 PIGK TCAP CRADD ELK1 DNAJB2 ZBTB16 DAZAP1 MAPKAPK2 EDRF1 CRIP1 UCP3 AGR2 P4HA2'.split(' ').join('\n')
const example_geneset_weighted = 'SERPINA3,1.0 CFL1,-1.0 FTH1,0.5 GJA1,-0.5 HADHB,0.25 LDHB,-0.25 MT1X,0.4 RPL21,0.3 RPL34,0.2 RPL39,0.1 RPS15,-0.1 RPS24,-0.2 RPS27,-0.3 RPS29,-0.4 TMSB4XP8,-0.6 TTR,-0.7 TUBA1B,-0.8 ANP32B,-0.9 DDAH1,0.9 HNRNPA1P10,0.8'.split(' ').join('\n')
const example_geneset_up = 'UTP14A S100A6 SCAND1 RRP12 CIAPIN1 ADH5 MTERF3 SPR CHMP4A UFM1 VAT1 HACD3 RFC5 COTL1 NPRL2 TRIB3 PCCB TLE1 CD58 BACE2 KDM3A TARBP1 RNH1 CHAC1 MBNL2 VDAC1 TES OXA1L NOP56 HAT1 CPNE3 DNMT1 ARHGAP1 VPS28 EIF2S2 BAG3 CDCA4 NPDC1 RPS6KA1 FIS1 SYPL1 SARS CDC45 CANT1 HERPUD1 SORBS3 MRPS2 TOR1A TNIP1 SLC25A46'.split(' ').join('\n')
const example_geneset_down = 'MAL EPCAM HDAC6 CAPN1 TNRC6B PKD1 RRS1 HP ANO10 CEP170B IDE DENND2D CAMK2B ZNF358 RPP38 MRPL19 NUCB2 GNAI1 LSR ADGRE2 PKMYT1 CDK5R1 ABL1 PILRB AXIN1 FBXL8 MCF2L DBNDD1 IGHMBP2 WIPF2 WFS1 OGFOD2 MAPK1IP1L COL11A1 REG3A SERPINA1 MYCBP2 PIGK TCAP CRADD ELK1 DNAJB2 ZBTB16 DAZAP1 MAPKAPK2 EDRF1 CRIP1 UCP3 AGR2 P4HA2'.split(' ').join('\n')

const style = {
  chiplabel: {
    maxWidth: 100,
    overflow: 'hidden',
    fontSize: 10,
    textOverflow: 'ellipsis',
    '&:hover': {
      overflow: "visible",
    }
  },
  card: {
    overflow: 'auto',
    maxHeight: 200,
    marginBottom: 10,
  }
}

const mapStateToProps = state => {
  return {
    loading: state.loading_signature,
    ui_values: state.serverSideProps.ui_values
  }
};

function mapDispatchToProps(dispatch) {
  return {
    // matchEntity: input => dispatch(matchEntity(input)),
    // initializeSignatureSearch: input => dispatch(initializeSignatureSearch(input)),
    submit: input => dispatch(findSignature(input)),
    // updateResolvedEntities: input => dispatch(updateResolvedEntities(input)),
  };
}

const Geneset = (props) => (
    <div className="row">
      <div className="col s12 center">
        <div className="switch">
          <label style={{ color: '#FFF',
            fontWeight: 'bold' }}>
            Gene Set or Full Signature
            <input
              type="checkbox"
              checked={false}
              onChange={() => {
                props.toggleInput("Rank")
              }
              }
            />
            <span className="lever"></span>
            Up and Down Gene Sets
          </label>
        </div>
      </div>
      <div className="col s12">
        <div className="input-field">
          <textarea
            id="geneset"
            placeholder={props.ui_values.LandingText.geneset_placeholder || 'Genes that are regulated in signature or overlap with gene set.'}
            style={{
              height: 200,
              overflow: 'auto',
              background: '#f7f7f7',
            }}
            value={props.input.geneset}
            onChange={(e) => {
              const input = {
                ...props.input,
                geneset: e.target.value,
              }
              props.updateInput(input)
            }}
          ></textarea>
        </div>
      </div>
    </div>
  )

  const UpDownGeneset = (props) => (
    <div className="row">
      <div className="col s12 center">
        <div className="switch">
          <label style={{ color: '#FFF',
            fontWeight: 'bold' }}>
            Gene Set or Full Signature
            <input
              type="checkbox"
              checked={true}
              onChange={() => {
                props.toggleInput("Overlap")
              }
              }
            />
            <span className="lever"></span>
            Up and Down Gene Sets
          </label>
        </div>
      </div>
      <div className="col s6">
        <div className="input-field">
          <textarea
            id="up_geneset"
            placeholder={props.ui_values.LandingText.up_genes_placeholder || 'Genes that are up-regulated in signature or overlap with gene set.'}
            style={{
              height: 200,
              overflow: 'auto',
              background: '#f7f7f7',
            }}
            value={props.input.up_geneset}
            onChange={(e) => {
              const input = {
                ...props.input,
                up_geneset: e.target.value,
              }
              props.updateInput(input)
            }}
          ></textarea>
        </div>
      </div>
      <div className="col s6">
        <div className="input-field">
          <textarea
            id="down_geneset"
            placeholder={props.ui_values.LandingText.down_genes_placeholder || 'Genes that are down-regulated in signature or overlap with gene set.'}
            style={{
              height: 200,
              overflow: 'auto',
              background: '#f7f7f7',
            }}
            value={props.input.down_geneset}
            onChange={(e) => {
              const input = {
                ...props.input,
                down_geneset: e.target.value,
              }
              props.updateInput(input)
            }}
          ></textarea>
        </div>
      </div>
    </div>
  )

  const SearchBox = (props) => {
    if (props.input.type === "Overlap"){
      return(<Geneset {...props}/>)
    }else if (props.input.type === "Rank"){
      return(<UpDownGeneset {...props}/>)
    }else {
      return <Redirect to="/not-found" />
    }
  }

class GenesetSearchBox extends React.Component {


  // componentDidMount = () => {
  //   if (this.props.location.state!==undefined &&
  //     this.props.location.state.input!==undefined) {
  //     this.props.updateInput(this.props.location.state.input)
  //   }else {
  //     this.toggleInput(this.props.match.params.type)
  //   }
  // }

  // componentDidUpdate = (prevProps, prevState) => {
  //   const old_type = prevProps.match.params.type
  //   const current_type = this.props.match.params.type
  //   const old_state = prevProps.location.state
  //   const current_state = this.props.location.state
  //   if (current_state!==undefined && current_state.input!==undefined){
  //     console.log(current_state)
  //     console.log(old_state)
  //     if (old_state === undefined || old_state.input === undefined){
  //       this.props.updateInput(current_state.input)
  //     }else if (old_state.input.type!==current_state.input.type){
  //       this.props.updateInput(current_state.input)
  //     }else if (current_state.input.type === "Overlap" &&
  //       current_state.input.geneset !== old_state.input.geneset){
  //       console.log("here")
  //       this.props.updateInput(current_state.input)
  //     }else if (current_state.input.type === "Rank" &&
  //       (current_state.input.up_geneset !== old_state.input.up_geneset ||
  //        current_state.input.down_geneset !== old_state.input.down_geneset)){
  //       this.props.updateInput(current_state.input)
  //     } 
  //   }else if (old_type !== current_type){
  //     if (this.props.location.state!==undefined &&
  //       this.props.location.state.input!==undefined) {
  //       this.props.updateInput(this.props.location.state.input)
  //     }else {
  //       this.toggleInput(this.props.match.params.type)
  //     }
  //   }
  // }


  isEmpty = () => {
    if (this.props.input === undefined) return true
    if (this.props.input.type === 'Overlap') {
      if (this.props.input.geneset === undefined) return true
      if (this.props.input.geneset === '') return true
    } else if (this.props.input.type === 'Rank') {
      if (this.props.input.up_geneset === '') return true
      if (this.props.input.up_geneset === undefined) return true
      if (this.props.input.down_geneset === '') return true
      if (this.props.input.down_geneset === undefined) return true
    }
    return false
  }


  render() {
    return (
      <div className="row">
        <SearchBox {...this.props} />
        <div className="col s12 center">
          <button
            className={'btn waves-effect waves-light' + (this.isEmpty() || this.props.loading ? ' disabled' : '')} type="submit" name="action"
            onClick={call(this.props.submit, this.props.input)}
          >
            { this.props.loading ? 
                <React.Fragment>
                  Searching &nbsp;
                  <i className="mdi mdi-spin mdi-loading" />
                </React.Fragment>: 
                <React.Fragment>
                  Search
                  <i className="material-icons right">send</i>
                </React.Fragment>
            }

          </button>
          <br /><br />
        </div>
      </div>
    )
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(withStyles(style)(GenesetSearchBox))
