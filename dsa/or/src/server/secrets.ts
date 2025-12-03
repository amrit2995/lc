import fs from 'fs'
import path from 'path'
import logger from './plugins/logger'

const additionalConfig = {
    // Everything is in seconds
    redisTTL: {
        userExpiry: 600 * 60, // 10 hours
        checkSessionTokenThreshold: 5 * 60, // user access token update - isInValidSessionByExpiry
        sessionExpiry: 15 * 60, // 15 Minutes
    },
}

const loadSecrets: any = () => {
    const secretsPath = path.resolve(
        process.cwd(),
        process?.env?.SECRETS_PATH || '/etc/config/secrets',
    )

    let secrets = {}
    if (fs.existsSync(secretsPath)) {
        try {
            secrets = JSON.parse(fs.readFileSync(secretsPath, 'utf8'))
        } catch (err) {
            logger.error('Failed to parse secrets JSON:', err)
        }
    }

    return {...additionalConfig, ...secrets}
}

export default loadSecrets
