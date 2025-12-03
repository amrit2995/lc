const makeGetCall = (url: string) => {
    return fetch(url)
        .then((res) => res.json())
        .then((response) => [null, response])
        .catch((error) => [error, null])
}

const makePostCall = (url: string, body: any) => {
    return fetch(url, {method: 'POST', body})
        .then((res) => res.json())
        .then((response) => [null, response])
        .catch((error) => [error, null])
}

export {makeGetCall, makePostCall}
