export interface MfeTemplateProps {
    scope?: String
}

export interface UrlParamProps {
    entity?: string
    action?: string
    id?: string
}

export interface AppMapProps {
    [key: string]: AppObjProps
}

export interface AppMapValueProps {
    appMap: AppMapProps
}

export type ImporterTypes =
    | 'vendorAccessAuth'
    | 'fabrik'
    | 'helix'
    | 'vendorSupport'
    | 'vendorFAQ'

export interface AppObjProps {
    app?: string
    remoteImporter?: ImporterTypes
    url?: string
    scope?: ScopeProps
    tab?: ScopeProps
    appAction?: string
}

export interface ScopeProps {
    [key: string]: string
}
