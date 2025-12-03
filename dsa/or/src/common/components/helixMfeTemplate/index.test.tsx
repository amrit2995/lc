import React from 'react'
import {shallow} from 'enzyme'
import HelixMfeTemplate from '.'

describe('<HelixMfeTemplate />', () => {
    it('renders <HelixMfeTemplate /> component', () => {
        const wrapper = shallow(<HelixMfeTemplate />)
        expect(wrapper.length).toStrictEqual(1)
    })
})
