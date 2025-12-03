import {resolve} from 'path'
import getSecrets from '../handlers/secretsHandler'

const faviconPath = resolve(`${__dirname}./../src/assets/logo/lmn-logo-v2.png`)
const basePath = process.env.BASE_PATH

export default [
    {
        method: 'GET',
        path: `${basePath}/management/health`,
        handler: (_req: any, res: any) =>
            res.send({health: 'OK', service: 'one-ring'}),
    },
    {
        method: 'GET',
        path: `${basePath}/probe/live`,
        handler: (_req: any, res: any) =>
            res.send({health: 'OK', service: 'one-ring'}),
    },
    {
        method: 'GET',
        path: `${basePath}/probe/ready`,
        handler: (_req: any, res: any) =>
            res.send({health: 'OK', service: 'one-ring'}),
    },
    {
        method: 'GET',
        path: `${basePath}/internal/secrets`,
        handler: getSecrets,
    },
    {
        method: 'GET',
        path: `${basePath}/favicon.ico`,
        handler: (_req: any, res: any) => res.sendFile(faviconPath),
    },
]
