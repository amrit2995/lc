import hash from 'object-hash'

const sha256 = (buffer: any) => hash(buffer)

const base64URLEncode = (str: any) =>
    str
        .toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '')

const authObj = (environment: any, verifier: any, challenge: any) => {
    /* eslint-disable camelcase */
    return {
        client_id: environment.clientId,
        redirect_uri: environment.redirectURL,
        scope: environment.scope,
        response_type: 'code',
        state: undefined,
        code_verifier: verifier,
        code_challenge: challenge,
        code_challenge_method: 'S256',
    }
}

const postRedirectAuthObj = (
    clientId: string,
    redirectURL: string,
    code: string,
    state: string,
) => {
    /* eslint-disable camelcase */
    const authRequestState = localStorage.getItem(
        'appauth_current_authorization_request',
    )
    const authInitialData = JSON.parse(
        localStorage.getItem(
            `${authRequestState}_appauth_authorization_request`,
        ),
    )
    return {
        client_id: clientId,
        redirect_uri: redirectURL,
        grant_type: 'authorization_code',
        code_verifier: authInitialData?.internal?.code_verifier,
        state,
        code,
    }
}

export {authObj, base64URLEncode, postRedirectAuthObj, sha256}
