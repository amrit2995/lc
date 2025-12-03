import axios from 'axios'
// eslint-disable-next-line import/no-extraneous-dependencies
import pino from 'pino'

const logg = pino()

/* eslint-disable no-console */
type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'fatal'

export const baseLogger = pino({
    ...(['development', 'stage'].includes(process.env.NODE_ENV as string)
        ? {
              transport: {
                  target: 'pino-pretty',
                  options: {
                      colorize: true,
                  },
              },
          }
        : {}),
})

// Safe stringify for objects and errors
function safeStringify(obj: unknown): string {
    const seen = new WeakSet()
    return JSON.stringify(
        obj,
        (key, value) => {
            if (typeof value === 'object' && value !== null) {
                if (seen.has(value)) return '[Circular]'
                seen.add(value)
            }

            if (value instanceof Error) {
                return {
                    message: value.message,
                    name: value.name,
                    stack: value.stack,
                }
            }

            return value
        },
        2,
    )
}

// Special handling for AxiosError
const processAxiosLog = (meta: any): void => {
    const {message, code, config, response} = meta

    const axiosMeta = {
        message,
        code,
        url: config?.url,
        method: config?.method,
        status: response?.status,
        statusText: response?.statusText,
        responseData:
            typeof response?.data === 'string'
                ? response.data.slice(0, 500)
                : JSON.stringify(response?.data)?.slice(0, 500),
    }

    logg.info(safeStringify(axiosMeta))
}

// Main log function
function log(level: LogLevel, message: string, meta?: unknown): void {
    logg.info(message)
    if (level === 'error' && axios.isAxiosError(meta)) {
        processAxiosLog(meta)
    } else if (meta !== undefined) {
        logg.info(message, safeStringify(meta))
    }

    if (level === 'fatal') {
        process.exit(1)
    }
}

// Exported logger object
const logger = {
    debug: (msg: string, meta?: unknown) => log('debug', msg, meta),
    info: (msg: string, meta?: unknown) => log('info', msg, meta),
    warn: (msg: string, meta?: unknown) => log('warn', msg, meta),
    error: (msg: string, meta?: unknown) => log('error', msg, meta),
    fatal: (msg: string, meta?: unknown) => log('fatal', msg, meta),
}

export default logger
