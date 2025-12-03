import React from 'react'
import {shallow} from 'enzyme'
import Forbidden from '.'

describe('<Forbidden />', () => {
    it('renders <Forbidden /> component', () => {
        const wrapper = shallow(<Forbidden />)
        expect(wrapper.length).toStrictEqual(1)
    })
})
