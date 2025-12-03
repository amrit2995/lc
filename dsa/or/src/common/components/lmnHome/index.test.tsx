import React from 'react'
import {shallow} from 'enzyme'
import LmnHome from '.'

describe('<LmnHome />', () => {
    it('renders <LmnHome /> component', () => {
        const wrapper = shallow(<LmnHome />)
        expect(wrapper.length).toStrictEqual(1)
    })
})
