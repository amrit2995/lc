import {Typography} from '@backyard/react'
import React from 'react'
import {ContainerHeader, ForbiddenPageWrapper} from './styles'

const Forbidden = () => (
    <>
        <ForbiddenPageWrapper>
            <ContainerHeader>403</ContainerHeader>
            <Typography color="white">
                You do not have permission to use this application.
            </Typography>
        </ForbiddenPageWrapper>
    </>
)

Forbidden.propTypes = {}

export default React.memo(Forbidden)
