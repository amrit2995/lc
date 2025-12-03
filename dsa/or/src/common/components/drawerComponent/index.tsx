import {Drawer, DrawerBody, Menu} from '@backyard/react'
import React, {SyntheticEvent, useContext, useEffect, useState} from 'react'
import {useHistory} from 'react-router-dom'
import SideDrawContext from '../../context/SideDrawContext'
import {displayNoneCloseProps} from '../../utils/constants'
import DrawerChildComponent from '../drawerChildComponent'
import {DrawerComponentProps} from './interface'
import DrawerWrapper from './styles'
import southDeepHighlighter from './utils'
import useFetch from '../../hooks/useFetch'
import {getBasePath} from '../../utils/commonUtils'

const DrawerComponent = (props: DrawerComponentProps) => {
    const sideDrawerContext = useContext(SideDrawContext)
    const [selectedItem, setSelectedItem] = useState(null)
    const history = useHistory()
    const {value: labelConfig = {}} = useFetch({
        url: `${getBasePath()}/onering/nucleus?scope=highlighter-config`,
        noCache: true,
    })
    const handleOnHover = (e: SyntheticEvent) => {
        e.stopPropagation()
        sideDrawerContext.onHoverIn()
    }

    const handleOnHoverOut = (e: SyntheticEvent) => {
        e.stopPropagation()
        sideDrawerContext.onHoverOut()
    }

    useEffect(() => {
        history.listen((location) => {
            const highlightObj = southDeepHighlighter(
                location.pathname,
                labelConfig['south-deep-highlighter'],
            )
            setSelectedItem(highlightObj)
        })
    }, [labelConfig])

    const menuClosedCondition = sideDrawerContext.isHovered ? '260' : '65'

    return (
        <DrawerWrapper>
            <Drawer
                maxWidth={
                    sideDrawerContext.isOpen ? '260' : menuClosedCondition
                }
                shape="squared"
                size="medium"
                closeProps={displayNoneCloseProps}
                onMouseOver={handleOnHover}
                onMouseLeave={handleOnHoverOut}
            >
                <DrawerBody style={{background: '#f4f6fa'}}>
                    <Menu shape="squared">
                        {props.elements.map((element) => (
                            <DrawerChildComponent
                                key={element.label}
                                label={element.label}
                                path={element.path}
                                children={element.children}
                                selectedItem={selectedItem}
                                isChild={false}
                                defaultPage={element.defaultPage}
                                labelConfig={
                                    labelConfig['south-deep-highlighter']
                                }
                            />
                        ))}
                    </Menu>
                </DrawerBody>
            </Drawer>
        </DrawerWrapper>
    )
}

export default React.memo(DrawerComponent)
