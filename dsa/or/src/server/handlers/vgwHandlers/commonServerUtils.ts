const isPolledService = (url = '') => false

const isVppService = (url = '') => url.indexOf('/vppapi/') >= 0

const isAggregatorVendorService = (url = '') =>
    url.indexOf('/aggregatorvendorservices/') >= 0

const removeVersion = (url = '') => {
    const nonVersionUrl = url.replace('/V2.0', '')
    return nonVersionUrl
}

const replaceVppServiceUrl = (url = '') =>
    url.replace('/vppapi/', '/vppuserservice/')

const updateIfUpdateNonRegContact = (url = '') => {
    if (url.indexOf('/updateNonRegContact') >= 0) {
        return url.replace('/updateNonRegContact', '?invite=true&update=true')
    }
    return url
}

const updateIfUpdateContact = (url = '') => {
    if (url.indexOf('/updateContact') >= 0) {
        return url.replace('/updateContact', '?invite=false&update=true')
    }
    return url
}

const updateIfInviteContact = (url = '') => {
    if (url.indexOf('/inviteContact') >= 0) {
        return url.replace('/inviteContact', '?invite=true')
    }
    return url
}

const isEmailDuplicateUrl = (url = '') => url.indexOf('/emailAddress') >= 0

const removeUam = (url = '') => {
    const nonUamUrl = url.replace('/uam', '')
    const nonVersionUrl = removeVersion(nonUamUrl)
    const nonVppApiUrl = replaceVppServiceUrl(nonVersionUrl)
    const updateNonRegContactUrl = updateIfUpdateNonRegContact(nonVppApiUrl)
    const updateRegContactUrl = updateIfUpdateContact(updateNonRegContactUrl)
    const updateInviteContactUrl = updateIfInviteContact(updateRegContactUrl)
    const updateDeleteAsPostUrl = updateInviteContactUrl.replace(
        '/proxyPostToDelete',
        '',
    )
    return updateDeleteAsPostUrl
}

const isVBUVerifyUrl = (url = '') => url.indexOf('/vbuVerify') >= 0

const isDeleteAsPostUrl = (url = '') => url.indexOf('/proxyPostToDelete') >= 0

const getContactIdVendorNumberVendorTypeFromUrl = (url = '') => {
    const urlAsArr = url.split('/')
    const indexOfVendorNumber = urlAsArr.indexOf('vendorNumber') + 1
    const indexOfVendorType = urlAsArr.indexOf('vendorType') + 1
    const indexOfContactId = urlAsArr.indexOf('contactId') + 1
    return {
        contactId: urlAsArr[indexOfContactId],
        vendorNumber: urlAsArr[indexOfVendorNumber],
        vendorType: urlAsArr[indexOfVendorType],
    }
}

export {
    isPolledService,
    isVppService,
    isAggregatorVendorService,
    removeVersion,
    removeUam,
    replaceVppServiceUrl,
    isEmailDuplicateUrl,
    updateIfInviteContact,
    updateIfUpdateNonRegContact,
    updateIfUpdateContact,
    isDeleteAsPostUrl,
    getContactIdVendorNumberVendorTypeFromUrl,
    isVBUVerifyUrl,
}
