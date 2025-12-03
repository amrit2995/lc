import {Menu, MenuItem} from '@backyard/react'
import React, {useContext, useEffect, useState} from 'react'
import {useHistory} from 'react-router-dom'
import SideDrawContext from '../../context/SideDrawContext'
import UserAccessContext from '../../context/UserAccessContext'
import {UserAccess} from '../../initialStates/user'
import {getCurrentPage} from '../../utils/authUtils'
import {getBasePath, lowerCase, trimLowerCase} from '../../utils/commonUtils'
import SideBarIcons from '../drawerComponent/icons'
import southDeepHighlighter from '../drawerComponent/utils'
import {DrawerChildComponentProps} from './interface'
import {ChildrenItemsWrapper, SelectedWrapper} from './styles'
import getIsHasDefault from './util'

let isDefaultPageSet: boolean = false
const DrawerChildComponent = (props: DrawerChildComponentProps) => {
    const sideDrawerContext = useContext(SideDrawContext)
    const userAccess: UserAccess = useContext(UserAccessContext)
    const basePath = getBasePath()
    const hideTextWhenSideBarCollapsed = true

    const [iconAfterText, setIconAfterText] = useState('none')
    const history = useHistory()
    useEffect(() => {
        const handleRouteChange = (event: any) => {
            if (typeof event.detail === 'string') {
                history.push(`${event.detail}`)
            }
            if (typeof event.detail === 'object') {
                history.push(`${event.detail.route}`, {...event.detail.state})
            }
        }

        window.addEventListener('mfeRouteChange', handleRouteChange)
        return () =>
            window.removeEventListener('mfeRouteChange', handleRouteChange)
    }, [])

    history.listen((location) => {
        const highlightObj = southDeepHighlighter(
            location.pathname,
            props.labelConfig,
        )
        if (props.children?.length) {
            const childIndex = props.children.findIndex(
                (item) => trimLowerCase(item.label) === highlightObj?.openLabel,
            )
            if (childIndex >= 0) {
                setIconAfterText('opened')
            } else {
                setIconAfterText('closed')
            }
        }
    })

    useEffect(() => {
        const [currentPage, currentPageParams] = getCurrentPage()
        if (currentPage) {
            isDefaultPageSet = true
            history.push({
                pathname: currentPage,
                search: currentPageParams,
                state: {isInitial: true},
            })
        }

        if (props.children?.length) {
            const childWithDefault = getIsHasDefault(props.children)
            history.push({
                pathname: history.location.pathname,
                search: history.location.search,
                state: {isInitial: true},
            })
            if (
                props.label.toLowerCase() ===
                southDeepHighlighter(
                    history.location.pathname,
                    props.labelConfig,
                )?.closedLabel
            ) {
                setIconAfterText('opened')
            } else if (
                childWithDefault &&
                !isDefaultPageSet &&
                !southDeepHighlighter(
                    history.location.pathname,
                    props.labelConfig,
                ).closedLabel
            ) {
                isDefaultPageSet = true
                history.push(`${basePath}${childWithDefault.path}`, {
                    isInitial: true,
                })
                setIconAfterText('opened')
            } else {
                setIconAfterText('closed')
            }
        } else if (props.defaultPage && !isDefaultPageSet) {
            isDefaultPageSet = true
            history.push(`${basePath}${props.path}`, {isInitial: true})
        }
    }, [props.children, props.labelConfig])

    const handleOnMenuItemClick = (event: React.MouseEvent) => {
        if (props.children?.length) {
            setIconAfterText(iconAfterText === 'closed' ? 'opened' : 'closed')
        } else {
            const path = `${basePath}${event.currentTarget.id}`
            history.push(path, {
                isSame: !!(path === history?.location?.pathname),
            })
        }
    }

    const openTemplate = (
        <div className="menu-item-space-between">
            <>{props.label}</>
            <SideBarIcons text={iconAfterText} />
        </div>
    )

    const closeTemplate = hideTextWhenSideBarCollapsed ? (
        <></>
    ) : (
        <>{props.label}</>
    )

    const menuClosedClassCondition = sideDrawerContext.isHovered
        ? 'menu-item-flex-start'
        : 'menu-item-flex-center'

    const menuClosedTemplateCondition = sideDrawerContext.isHovered
        ? openTemplate
        : closeTemplate

    const childMenuDisplayCondition =
        (sideDrawerContext.isOpen && iconAfterText === 'opened') ||
        (!sideDrawerContext.isOpen &&
            sideDrawerContext.isHovered &&
            iconAfterText === 'opened')

    const selectedStyleOpenCondition =
        props?.selectedItem &&
        trimLowerCase(props?.selectedItem.openLabel) ===
            trimLowerCase(props?.label) &&
        !props.children?.length

    const selectedStyleClosedCondition =
        props?.selectedItem &&
        trimLowerCase(props?.selectedItem.closedLabel) ===
            trimLowerCase(props?.label)

    const getSelectedClass = () => {
        if (sideDrawerContext.isOpen || sideDrawerContext.isHovered) {
            if (selectedStyleOpenCondition) {
                return 'selected-border'
            }
            return 'unselected-border'
        }
        if (selectedStyleClosedCondition) {
            return 'selected-border'
        }
        return 'unselected-border'
    }

    return (
        <SelectedWrapper
            isChild={props.isChild}
            hideBorders={
                !(sideDrawerContext.isHovered || sideDrawerContext.isOpen)
            }
        >
            <div className={getSelectedClass()}>
                <MenuItem
                    color="neutral"
                    size="large"
                    id={props.path}
                    onClick={handleOnMenuItemClick}
                    shape="squared"
                >
                    <a
                        href={`${basePath}${props.path}`}
                        style={{
                            textDecoration: 'none',
                            color: 'inherit',
                            width: '100%',
                            height: '100%',
                            display: 'flex',
                            alignItems: 'center',
                            fontWeight: props.isChild ? '400' : '600',
                        }}
                        onClick={(e) => {
                            e.preventDefault()
                        }}
                    >
                        <div
                            className={
                                sideDrawerContext.isOpen
                                    ? 'menu-item-flex-start'
                                    : menuClosedClassCondition
                            }
                        >
                            <div className="icon-wrapper">
                                <SideBarIcons text={lowerCase(props.label)} />
                            </div>

                            {sideDrawerContext.isOpen
                                ? openTemplate
                                : menuClosedTemplateCondition}
                        </div>
                    </a>
                </MenuItem>
                {childMenuDisplayCondition && (
                    <Menu shape="squared">
                        {props?.children?.map((child) => {
                            if (child.isOnlyVendor) {
                                if (userAccess.isVendorUser) {
                                    return (
                                        <React.Fragment key={child.label}>
                                            <ChildrenItemsWrapper>
                                                <DrawerChildComponent
                                                    isChild
                                                    label={child.label}
                                                    path={child.path}
                                                    selectedItem={
                                                        props.selectedItem
                                                    }
                                                    defaultPage={
                                                        props.defaultPage
                                                    }
                                                    labelConfig={
                                                        props.labelConfig
                                                    }
                                                />
                                            </ChildrenItemsWrapper>
                                        </React.Fragment>
                                    )
                                }
                                return null
                            }
                            return (
                                <React.Fragment key={child.label}>
                                    <ChildrenItemsWrapper>
                                        <DrawerChildComponent
                                            isChild
                                            label={child.label}
                                            path={child.path}
                                            selectedItem={props.selectedItem}
                                            defaultPage={props.defaultPage}
                                            labelConfig={props.labelConfig}
                                        />
                                    </ChildrenItemsWrapper>
                                </React.Fragment>
                            )
                        })}
                    </Menu>
                )}
            </div>
        </SelectedWrapper>
    )
}

export default React.memo(DrawerChildComponent)
