const asyncWrap = (promise: Promise<any>) =>
    promise.then((result) => [null, result]).catch((err) => [err])

const lowerCase = (str: string) => str && str.toLowerCase()

const trimLowerCase = (str: string) => {
    if (str) {
        return str.replaceAll(' ', '').toLowerCase()
    }
    return ''
}

const replaceUnderScore = (str: string) => str && str.replace(/_/g, ' ')

const replaceSpaceWithUnderScore = (str: string) =>
    str && str.replaceAll(' ', '_')

const camelCaseToLabel = (str: string) =>
    str && str.replace(/[A-Z]/g, (txt) => ` ${txt.charAt(0)}`)

const toProperCase = (str: string) =>
    str &&
    str.replace(
        /\w\S*/g,
        (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase(),
    )

const getBasePath = () => process.env.BASE_PATH

const displayTbcAfterCharLimit = (str: string, charLimit: number) =>
    str?.length > charLimit ? `${str.slice(0, charLimit)} ...` : str

const triggerOnMfeRouteChange = (route: any) => {
    const event = new CustomEvent('mfeRouteChange', {detail: route})
    window.dispatchEvent(event)
}

const triggerOnInterceptorAccessDenied = () => {
    const event = new CustomEvent('interceptorErr403', {detail: '403'})
    window.dispatchEvent(event)
}

const encodeBase64 = (input: string): string => {
    const utf8Bytes = new TextEncoder().encode(input)
    return btoa(String.fromCharCode(...utf8Bytes))
}

/**
 * Returns the environment based on the current URL.
 * If the URL includes 'dev', returns 'dev'.
 * If the URL includes 'stage', returns 'stage'.
 * Otherwise, returns 'prod'.
 * @returns {string} The environment.
 */
const getEnv = () => {
    const url = window?.location?.href
    if (url.includes('dev')) {
        return 'dev'
    }
    if (url.includes('stage')) {
        return 'stage'
    }
    return 'prod'
}

export {
    asyncWrap,
    camelCaseToLabel,
    displayTbcAfterCharLimit,
    getBasePath,
    lowerCase,
    replaceSpaceWithUnderScore,
    replaceUnderScore,
    toProperCase,
    triggerOnInterceptorAccessDenied,
    triggerOnMfeRouteChange,
    trimLowerCase,
    encodeBase64,
    getEnv,
}
