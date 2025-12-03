import {AppMapProps, AppObjProps, ScopeProps} from './interface'

const getAppNameDetails = (
    appObj: AppMapProps,
    entity: string,
): AppObjProps => {
    if (appObj && entity) {
        if (appObj[entity]) {
            return {...appObj[entity], appAction: ''}
        }
        return {...appObj.campaignManager, appAction: entity}
    }
    return null
}

const getAppModuleFromAction = (
    scope: ScopeProps,
    appDetailsAction: string,
    action: string,
) => {
    if (appDetailsAction) {
        return scope[appDetailsAction]
    }
    return scope[action]
}

export {getAppModuleFromAction, getAppNameDetails}
