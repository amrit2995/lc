import graphQlPlugin from '@<url>/helix-graphql-express-plugin'

import schema from './graphQlOptions'

/**
 * Overlay Lowe's Node.js framework defaults with your applications
 * overrides and configuration.
 */

export default {
    server: {
        /**
         * Note: Whatever inside app property will send it to client side for hydrate.
         * If anything needs only for serverside then create and keep it in separate property...
         */
        // port: 2999,
        app: {
            api: {
                host: process.env.services_host || '',
                cdnUrl: process.env.cdn_url || '',
                domain: process.env.domain || '',
                pharosUrl:
                    process.env.pharos_url ||
                    '<url>',
            },
            featureflags: {
                /**
                 * Don't delete enableSSR, enableDynamicImports flags. Its used inside the helix-core package.
                 */
                enableSSR: process.env.enableSSR !== 'false' && true,
                enablePharos: process.env.enablePharos === 'true' || false,
                enableDynamicImports:
                    process.env.enableDynamicImports !== 'false' && true,
                esiEnabled: process.env.esiEnabled === 'true' || false,
                enableGraphQLSSR:
                    process.env.enableGraphQLSSR === 'true' || true,
            },
            constants: {
                pharosName: 'one-ring',
            },
        },
    },
    register: {
        plugins: [
            // {
            //     plugin: i18next,
            //     options: getI18Next(serverConfig),
            // },

            {
                plugin: graphQlPlugin,
                options: {
                    serverOptions: {
                        schema,
                    },
                    middlewareOptions: {},
                },
            },
        ],
    },
}
