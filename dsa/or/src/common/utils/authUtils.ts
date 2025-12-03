/* eslint-disable no-plusplus */
const getCookie = (name: string) => {
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) {
        return parts.pop().split(';').shift()
    }
    return null
}
const getAccessToken = () => getCookie('Authorization')

const waitForAuthCookie = (
    maxAttempts = 3,
    delay = 200,
): Promise<string | null> => {
    return new Promise((resolve) => {
        let attempts = 0

        const check = () => {
            const token = getCookie('Authorization')
            if (token || attempts >= maxAttempts) {
                resolve(token)
            } else {
                attempts++
                setTimeout(check, delay)
            }
        }

        check()
    })
}

const setCurrentPage = () => {
    const currentPage = window.location.pathname
    const currentPageParams = window.location.search
    if (
        !currentPage.endsWith('/lormn/') &&
        !currentPage.endsWith('/lormn/dashboard/')
    ) {
        window.sessionStorage.setItem('currentPage', currentPage)
        window.sessionStorage.setItem('currentPageParams', currentPageParams)
    }
}

const getCurrentPage = (): string[] | null => {
    const pageData = window.sessionStorage.getItem('currentPage')
    const pageParams = window.sessionStorage.getItem('currentPageParams')
    if (pageData) {
        window.sessionStorage.removeItem('currentPage')
        if (pageParams) {
            window.sessionStorage.removeItem('currentPageParams')
            return [pageData.toString(), pageParams.toString()]
        }
        return [pageData.toString()]
    }
    return [null]
}

export {
    getAccessToken,
    getCookie,
    getCurrentPage,
    setCurrentPage,
    waitForAuthCookie,
}
