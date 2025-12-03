import React from 'react'
import {getBasePath} from '../common/utils/commonUtils'

const HeadHtml = () => (
    <>
        <link
            rel="icon"
            href={`${getBasePath()}/favicon.ico`}
            type="image/icon type"
        />
    </>
)

export default HeadHtml
