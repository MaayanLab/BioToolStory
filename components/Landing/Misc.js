import React from 'react'
import dynamic from 'next/dynamic'

import Grid from '@material-ui/core/Grid'
import Card from '@material-ui/core/Card'
import Typography from '@material-ui/core/Typography'
import ListItem from '@material-ui/core/ListItem'
import Button from '@material-ui/core/Button'

import ToggleButton from '@material-ui/lab/ToggleButton'
import ToggleButtonGroup from '@material-ui/lab/ToggleButtonGroup'
import { base_scheme as meta_base_scheme, base_url as meta_base_url } from '../../util/fetch/meta'

import ReactWordcloud from 'react-wordcloud'

import { FindReplace,
  FileFind,
  LibraryBooks,
  Fingerprint,
  Web,
  Human,
  TestTube,
  ChartBubble,
  Webhook,
  Tilde,
  EmoticonCryOutline,
  DecagramOutline,
  Dna,
  CameraMeteringMatrix,
  Hammer,
  HexagonMultiple,
  Axis,
  NearMe,
  Earth } from 'mdi-material-ui'

import GenesetSearchBox from './GenesetSearchBox'

const SearchBox = dynamic(() => import('../../components/MetadataSearch/SearchBox'))

const meta_default_icon = "mdi-creation"

export const BottomLinks = ( { classes, width, ...props } ) => {
  return (
    <Grid container
      spacing={24}
      alignItems={'center'}>
      <Grid item xs={12}>
        <div className={classes.centered}>
          <Typography variant="title">
           Start using Signature Commons on your project
          </Typography>
        </div>
      </Grid>
      <Grid item xs={6} sm={3}>
        <div className={classes.centered}>
          <Grid container
            spacing={8}
            alignItems={'center'}
            direction={'column'}>
            <Grid item xs={12}>
              <Button className={`${classes.cardIcon} ${classes.GrayCardHeader}`}
                onClick={(e)=>props.handleChange(e, 'metadata')}>
                <FileFind className={classes.icon} />
              </Button>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subheader">
                  Metadata Search
              </Typography>
            </Grid>
          </Grid>
        </div>
      </Grid>
      <Grid item xs={6} sm={3}>
        <div className={classes.centered}>
          <Grid container
            spacing={8}
            alignItems={'center'}
            direction={'column'}>
            <Grid item xs={12}>
              <Button className={`${classes.cardIcon} ${classes.GrayCardHeader}`}
                onClick={(e)=>props.handleChange(e, 'signature')}>
                <FindReplace className={classes.icon} />
              </Button>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subheader">
                  Signature Search
              </Typography>
            </Grid>
          </Grid>
        </div>
      </Grid>
      <Grid item xs={6} sm={3}>
        <div className={classes.centered}>
          <Grid container
            spacing={8}
            alignItems={'center'}
            direction={'column'}>
            <Grid item xs={12}>
              <Button className={`${classes.cardIcon} ${classes.GrayCardHeader}`} href="#/Resources">
                <NearMe className={classes.icon} />
              </Button>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subheader">
                  Browse Resources
              </Typography>
            </Grid>
          </Grid>
        </div>
      </Grid>
      <Grid item xs={6} sm={3}>
        <div className={classes.centered}>
          <Grid container
            spacing={8}
            alignItems={'center'}
            direction={'column'}>
            <Grid item xs={12}>
              <Button className={`${classes.cardIcon} ${classes.GrayCardHeader}`}
                href={`${meta_base_scheme}://petstore.swagger.io/?url=${meta_base_url}/openapi.json`}>
                <Earth className={classes.icon} />
              </Button>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subheader">
                  API
              </Typography>
            </Grid>
          </Grid>
        </div>
      </Grid>
    </Grid>
  )
}

export const CountsDiv = ({ classes, width, ...props }) => {
  const { meta_counts } = props
  return (
    <Grid container
      spacing={24}
      alignItems={'center'}>
      <Grid item xs={12}>
        <div className={classes.centered}>
          <Typography variant="title">
            Search across a broad gathering of perturbations
          </Typography>
        </div>
      </Grid>
      {meta_counts.map((entry) => (
        <Grid item xs={4} sm={3} key={entry.name}>
          <div className={classes.centered}>
            { entry.icon===undefined ? <span class={`mdi ${meta_default_icon} mdi-24px`}></span>:
              <span class={`mdi ${entry.icon} mdi-24px`}></span>
            }
            <Typography variant="subheading">
              {entry.counts}
            </Typography>
            <Typography variant="caption">
              {entry.Preferred_Name}
            </Typography>
          </div>
        </Grid>
      ))}
    </Grid>
  )
}

export const StatDiv = ({ classes, width, ...props }) => {
  return (
    <Grid container
      spacing={24}
      alignItems={'center'}>
      <Grid item xs={12}>
        <Grid container
          spacing={24}
          alignItems={'center'}>
          <Grid item xs={12}>
            <div className={classes.centered}>
              <Typography variant="title">
               Explore an extensive collection of well-annotated gene-sets and signatures
              </Typography>
            </div>
          </Grid>
          <Grid item xs={4}>
            <div className={classes.centered}>
              <span class="mdi mdi-library-books mdi-24px"></span>
              <Typography variant="h5" component="h5">
                {props.LibraryNumber}
              </Typography>
              Libraries
            </div>
          </Grid>
          <Grid item xs={4}>
            <div className={classes.centered}>
              <span class="mdi mdi-fingerprint mdi-24px"></span>
              <Typography variant="h5" component="h5">
                {props.SignatureNumber}
              </Typography>
              Signatures
            </div>
          </Grid>
          <Grid item xs={4}>
            <div className={classes.centered}>
              <span class="mdi mdi-web mdi-24px"></span>
              <Typography variant="h5" component="h5">
                {Object.keys(props.resource_signatures).length}
              </Typography>
              Resources
            </div>
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  )
}

export const SearchCard = ({ classes, width, ...props }) =>{
  return (
    <Card className={`${classes.paddedCard} ${classes.topCard}`}>
      <Grid container
        spacing={24}
        direction={'column'}
        align="center"
        justify="center">
        <Grid item xs={12}>
          <div className={classes.toggleContainer}>
            <ToggleButtonGroup value={props.searchType} exclusive onChange={props.handleChange}>
              <ToggleButton value="metadata">
                <FileFind />
                Metadata Search
              </ToggleButton>
              <ToggleButton value="signature">
                <FindReplace />
                Signature Search
              </ToggleButton>
            </ToggleButtonGroup>
          </div>
        </Grid>
        <Grid item xs={12}>
          {props.searchType == 'metadata' ?
            <SearchBox
              id='metadata'
              search={props.search}
              searchChange={props.searchChange}
            /> :
            <GenesetSearchBox
              id="signature"
              onSubmit={props.submit}
              type={props.type}
              {...props}
            />
          }
        </Grid>
      </Grid>
    </Card>
  )
}

export const ListItemLink = (props) => (
  <ListItem button component="a" {...props} />
)

function getCallback(callback) {
  return function(word) {
    location.href = `#/MetadataSearch?q=${word.text}`
  }
}

const callbacks = {
  onWordClick: getCallback('onWordClick'),
}

export const WordCloud = function({ classes, record={}, ...props }) {
  const { stats } = props
  if (stats!==null) {
    const wordstats = Object.entries(stats).map(function(entry) {
      return ({ 'text': entry[0], 'value': entry[1] })
    })
    wordstats.sort((a, b) => parseFloat(b.value) - parseFloat(a.value))

    return (
      <div style={{ width: 300, height: 300, display: 'block', margin: 'auto' }}>
        <ReactWordcloud words={wordstats}
          callbacks={callbacks}
          options={{
            colors: ['#000'],
            rotations: 3,
            rotationsAngles: [0, 90],
          }} />
      </div>
    )
  } else {
    return ( <div />)
  }
}