import secrets from '../secrets'

const fs = require('fs')
const path = require('path')

const {mongodb} = secrets()
const {host, dbName, certs} = mongodb
const {ca, key} = certs

export default function init() {
    const options = {
        url: host,
        database: dbName,
    }

    const filePath = path.resolve(`${__dirname}./../certs`)
    const caPath = `${filePath}`
    // const keyPath = `${filePath}/Server.pem`

    // options.url += `&tlsCAFile=${caPath}&tlsCertificateKeyFile=${keyPath}`
    options.url += `&tlsCAFile=${caPath}`

    // fs.writeFileSync(keyPath, key)
    fs.writeFileSync(caPath, ca)

    return options
}
