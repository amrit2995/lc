/* eslint-disable import/prefer-default-export */
const mask = 'X'

export const maskName = (fullName: string) => {
    if (!fullName) return ''

    const names = fullName.trim().split(/\s+/)
    const firstName = names[0] || ''
    const lastName = names[1] || ''

    const maskedFirst =
        firstName.slice(0, 3) + mask.repeat(Math.max(0, firstName.length - 3))

    const maskedLast =
        lastName.slice(0, 3) + mask.repeat(Math.max(0, lastName.length - 3))

    return [maskedFirst, maskedLast].filter(Boolean).join(' ')
}
