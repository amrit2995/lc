import {ElementProps} from '../sideDrawer/interface'

const getIsHasDefault = (children: ElementProps[]) => {
    if (children?.length) {
        const defaultPage = children.find((item) => item.defaultPage)
        if (defaultPage?.path) {
            return defaultPage
        }
    }
    return null
}

export default getIsHasDefault
