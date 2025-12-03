import React from 'react'
import {Typography} from '@backyard/react'
import {
    FAQContainer,
    HeaderWrapper,
    SectionQuestions,
    SectionWrapper,
} from './styles'
import Question from './Question'
import useFetch from '../../hooks/useFetch'
import {getBasePath} from '../../utils/commonUtils'
import {FAQSectionItem} from './interface'

const FAQ = () => {
    const {value: faqConfig, error} = useFetch({
        url: `${getBasePath()}/onering/nucleus?scope=faq-config`,
        noCache: false,
    })

    const sections: FAQSectionItem[] =
        ((faqConfig as any)?.sections as FAQSectionItem[]) || []
    const isLoading = !error && (!faqConfig || !(faqConfig as any)?.sections)

    return (
        <FAQContainer>
            <HeaderWrapper>
                <Typography variant="h2">Frequently Asked Questions</Typography>
            </HeaderWrapper>
            {isLoading && (
                <Typography variant="body_1">Loading FAQs…</Typography>
            )}
            {error && (
                <Typography variant="body_1">
                    Unable to load FAQs right now.
                </Typography>
            )}
            {!isLoading &&
                !error &&
                sections?.map((section, index) => {
                    const sectionKey =
                        section.id ?? `${section.header}-${index}`
                    return (
                        <SectionWrapper key={sectionKey}>
                            <Typography variant="h1" size="size_18">
                                {section.header}
                            </Typography>
                            <SectionQuestions>
                                {section?.questions?.map((question, qIndex) => {
                                    const qKey =
                                        question?.id ??
                                        `${question?.question}-${qIndex}`

                                    return (
                                        <Question
                                            key={qKey}
                                            question={question}
                                        />
                                    )
                                })}
                            </SectionQuestions>
                        </SectionWrapper>
                    )
                })}
        </FAQContainer>
    )
}

export default FAQ
