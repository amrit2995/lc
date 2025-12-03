import {Typography} from '@backyard/react'
import React from 'react'
import LinkWrapper from './linkWrapper'
import {EntityFragmentProps} from './interface'
import {Hr, Subheader, Ul, Li} from './styles'
import {triggerOnMfeRouteChange} from '../../utils/commonUtils'

const EntityFragment: React.FC = ({
    displayEntityType,
    entityType,
    data,
    handleClear,
}: EntityFragmentProps) => {
    return (
        data?.length !== 0 && (
            <>
                <Typography>
                    <Subheader>
                        <Typography variant="h6">
                            {displayEntityType}
                        </Typography>
                    </Subheader>
                    <Ul>
                        {data?.map((i) => (
                            <Li key={i?.id}>
                                <LinkWrapper
                                    label={i?.name}
                                    onClick={() => {
                                        handleClear()
                                        triggerOnMfeRouteChange(
                                            `/lormn/dashboard/${entityType.toLowerCase()}/view/${
                                                i?.id
                                            }`,
                                        )
                                    }}
                                    to={`/lormn/dashboard/${entityType.toLowerCase()}/view/${
                                        i?.id
                                    }`}
                                />
                            </Li>
                        ))}
                    </Ul>
                </Typography>
                <Hr />
            </>
        )
    )
}

export default React.memo(EntityFragment)
