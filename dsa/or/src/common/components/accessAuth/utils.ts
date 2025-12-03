const VG_USER_LIST_APP_REMOTES = {
    "<url>"
}

const VG_USER_ADD_EDIT_APP_REMOTES = {
    "<url>"
}

const getVgUserListUrl = () => {
    const url = (window.location && window.location.href) || ''
    if (url.includes('dev')) {
        return VG_USER_LIST_APP_REMOTES.dev
    }
    if (url.includes('stage')) {
        return VG_USER_LIST_APP_REMOTES.stage
    }
    return VG_USER_LIST_APP_REMOTES.prod
}

const getVgUserAddEditUrl = () => {
    const url = (window.location && window.location.href) || ''
    if (url.includes('dev')) {
        return VG_USER_ADD_EDIT_APP_REMOTES.dev
    }
    if (url.includes('stage')) {
        return VG_USER_ADD_EDIT_APP_REMOTES.stage
    }
    return VG_USER_ADD_EDIT_APP_REMOTES.prod
}

export {getVgUserAddEditUrl, getVgUserListUrl}
