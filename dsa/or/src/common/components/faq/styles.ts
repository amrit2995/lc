import styled from 'styled-components'
import {ChevronDown, ChevronUp} from '@backyard/icons'

export const FAQContainer = styled.div`
    display: flex;
    flex-direction: column;
    gap: 24px;
    background-color: var(--bds-color-surface-subdued);
    position: relative;
    width: calc(100% + 50px);
    top: -25px;
    left: -25px;
`
export const HeaderWrapper = styled.div`
    background-color: white;
    padding: 22px;
`

export const SectionWrapper = styled.div`
    display: flex;
    flex-direction: column;
    padding: 48px;
    border: 1px solid #cbd1dd;
    border-radius: 8px;
    background-color: white;
    margin: 0 22px;
`

export const SectionQuestions = styled.div`
    display: flex;
    flex-direction: column;
`

export const QuestionWrapper = styled.div`
    display: flex;
    flex-direction: column;
`

export const QuestionHeader = styled.div`
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 8px;
    border-bottom: 1px solid #cbd1dd;
`

export const ContentWrapper = styled.div`
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 8px;
`

export const MultipleTypeContainer = styled.div`
    padding-bottom: 8px;
    display: flex;
    flex-direction: row;
    gap: 4px;
`

export const ListContentWrapper = styled.ul`
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
`

export const ExternalLink = styled.a`
    color: -webkit-link;
    cursor: pointer;
    text-decoration: underline;
`

// Icon components with consistent styling
export const StyledChevronUp = styled(ChevronUp)`
    color: #0072ce;
`

export const StyledChevronDown = styled(ChevronDown)`
    color: #0072ce;
`

export const PaddedTypography = styled.div`
    padding-bottom: 8px;
`
