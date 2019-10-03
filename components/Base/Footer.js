import React from 'react'
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import CardHeader from '@material-ui/core/CardHeader';
import CardMedia from '@material-ui/core/CardMedia';
import CardContent from '@material-ui/core/CardContent';


export default function Footer(props) {
  return (
    <footer className="page-footer grey lighten-3 black-text">
      <Grid
        container
        direction="row"
        justify="space-around"
        alignItems="center"
        style={{
          marginBottom: 20
        }}
      >
        <Grid item>
          <a className="github-button" href="https://github.com/MaayanLab/btools-ui" data-size="large" aria-label="View Source Code MaayanLab/btools-ui on GitHub">View Source Code</a><br />
          <a className="github-button" href="https://github.com/MaayanLab/btools-ui/issues" data-size="large" aria-label="Submit Bug Report MaayanLab/btools-ui on GitHub">Submit Bug Report</a>
        </Grid>
        <Grid item>
          <Card style={{
            background: '#757575',
          }}>
            <CardContent style={{marginBottom:-10}}>
              <Grid container spacing={8}>
                <Grid item>
                  <Typography variant="overline" style={{color: '#FFF'}}>
                    Powered by
                  </Typography>
                </Grid>
                <Grid item>
                  <img
                    src={`${process.env.PREFIX}/static/sigcom.ico`}
                    alt="Sigcom"
                    width={50}
                  />
                </Grid>
                <Grid item>
                  <Typography variant="h6" style={{color:"#ffde14"}}>
                    Signature<br/>Commons
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </footer>
  )
}
