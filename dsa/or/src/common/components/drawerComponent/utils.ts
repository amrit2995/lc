import {SelectedItemProps} from '../drawerChildComponent/interface'

const nameUtil = (pathName: string) => {
    if (pathName === 'reporting') {
        return 'reports'
    }
    return ''
}

const southDeepHighlighter = (
    path: string,
    labelsConfig: Array<{paths: Array<string>; values: SelectedItemProps}> = [],
) => {
    const labels = labelsConfig.find((config: any) =>
        config.paths.some((pt: string) => path.includes(pt)),
    )
    if (labels) return labels.values
    if (path.includes('/dashboard/reporting/')) {
        const splitPath = path.split('/')
        if (splitPath[4]?.toLowerCase() === 'campaignperformance') {
            return {
                openLabel: 'campaign stats',
                closedLabel: 'campaign stats',
            }
        }
        return {
            openLabel: splitPath[4] ? splitPath[4].toLowerCase() : '',
            closedLabel: nameUtil(splitPath[3]) || '',
        }
    }
    const postSplit = path.split('/')
    return {
        openLabel: postSplit[4] ? postSplit[4].toLowerCase() : '',
        closedLabel: postSplit[3] || '',
    }
}

export default southDeepHighlighter
