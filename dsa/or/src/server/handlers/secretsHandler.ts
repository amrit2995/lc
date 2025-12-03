import secrets from '../secrets'

const getSecrets = async (request: any, response: any) => {
    const secretsObj = secrets()
    if (secretsObj.auth.nucleus === request.headers.authorization) {
        return response.json(secretsObj)
    }
    return response.status(401).json({error: 'Unauthorized!'})
}

export default getSecrets
