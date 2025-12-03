import React from 'react'
import {Redirect} from 'react-router-dom'
import {getBasePath} from '../utils/commonUtils'

const basePath = getBasePath()

const RedirectComponent = () => (
    <>
        <Redirect to={`${basePath}/`} />
    </>
)

export default React.memo(RedirectComponent)
