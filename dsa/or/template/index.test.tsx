import React from 'react';
import { shallow } from 'enzyme';
--REDUX-STORE--import --COMPONENT_NAME-- from '.';
--MOCK-STORE--
describe('<--COMPONENT_NAME-- />', () => {
    it('renders <--COMPONENT_NAME-- /> component', () => {
        const wrapper = shallow(--PROVIDER-START--<--COMPONENT_NAME-- />--PROVIDER-END--);
        expect(wrapper.length).toStrictEqual(1);
    });
});
