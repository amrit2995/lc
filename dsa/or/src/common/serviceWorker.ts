// This optional code is used to register a service worker.
// register() is not called by default.

export function register(config) {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker
                .register('/helixapp/assets/sw.js', {scope: '/'})
                .then((registration) => {
                    // eslint-disable-next-line no-param-reassign
                    registration.onupdatefound = () => {
                        const installingWorker = registration.installing
                        if (installingWorker == null) {
                            return
                        }
                        installingWorker.onstatechange = () => {
                            if (installingWorker.state === 'installed') {
                                if (navigator.serviceWorker.controller) {
                                    // Execute callback
                                    if (config && config.onUpdate) {
                                        config.onUpdate(registration)
                                    }
                                } else {
                                    console.log(
                                        'Content is cached for offline use.',
                                    )

                                    // Execute callback
                                    if (config && config.onSuccess) {
                                        config.onSuccess(registration)
                                    }
                                }
                            }
                        }
                    }
                })
                .catch((registrationError) => {
                    console.log('SW registration failed: ', registrationError)
                })
        })
    }
}

export function unregister() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.ready.then((registration) => {
            registration.unregister()
        })
    }
}
