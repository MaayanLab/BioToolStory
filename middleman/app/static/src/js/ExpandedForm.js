import React from 'react'
import Grid from '@material-ui/core/Grid'
import MetadataForm from './Form'
import Collapse from '@material-ui/core/Collapse'
import CardContent from '@material-ui/core/Collapse'
import PropTypes from 'prop-types'

export const ExpandedForm = ({expanded, data, onChange, onSubmit, onError, ...props}) => {
    return (
    <Collapse in={expanded} timeout="auto" unmountOnExit >
        <CardContent style={{height:"100%", padding: 10}}>
            <Grid
            container
            direction="row"
            >
                <Grid item xs={12}>
                    <MetadataForm
                        data={data}
                        onChange={onChange}
                        onSubmit={onSubmit}
                        onError={onError}
                        {...props}
                    />
                </Grid>
            </Grid>
        </CardContent>
    </Collapse>
    )
}

ExpandedForm.propTypes = {
    expanded: PropTypes.bool,
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