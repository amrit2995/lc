import React, {useState} from 'react'
import {Typography} from '@backyard/react'
import {Link} from 'react-router-dom'
import {
    ContentWrapper,
    ListContentWrapper,
    QuestionHeader,
    QuestionWrapper,
    StyledChevronUp,
    StyledChevronDown,
    MultipleTypeContainer,
    ExternalLink,
    PaddedTypography,
} from './styles'
import {FAQQuestionItem} from './interface'

interface QuestionProps {
    question: FAQQuestionItem
    defaultOpen?: boolean
}

const Question = ({question, defaultOpen = false}: QuestionProps) => {
    const [isOpen, setIsOpen] = useState(defaultOpen)
    return (
        <QuestionWrapper>
            <QuestionHeader onClick={() => setIsOpen(!isOpen)}>
                <Typography variant="h1" size="size_16">
                    {question.question}
                </Typography>
                {isOpen ? <StyledChevronUp /> : <StyledChevronDown />}
            </QuestionHeader>
            {isOpen && (
                <ContentWrapper>
                    {question.children.map((value, index) => {
                        // Use contentType in key for better uniqueness
                        const contentKey = `${value.contentType}-${
                            question.id || ''
                        }-${index}`

                        switch (value.contentType) {
                            case 'list':
                                return (
                                    <ListContentWrapper key={contentKey}>
                                        {value.content.map(
                                            (listItem: string) => (
                                                <li>
                                                    <Typography variant="body_1">
                                                        {listItem}
                                                    </Typography>
                                                </li>
                                            ),
                                        )}
                                    </ListContentWrapper>
                                )
                            case 'multi-type':
                                return (
                                    <MultipleTypeContainer>
                                        {value?.children?.map((c) => {
                                            if (c?.contentType === 'link')
                                                return c.url.startsWith(
                                                    'http',
                                                ) ? (
                                                    <ExternalLink
                                                        target="_blank"
                                                        href={c.url}
                                                    >
                                                        {c.label}
                                                    </ExternalLink>
                                                ) : (
                                                    <Link to={c.url}>
                                                        {c.label}
                                                    </Link>
                                                )
                                            return (
                                                <PaddedTypography>
                                                    <Typography
                                                        key={contentKey}
                                                        variant="body_1"
                                                    >
                                                        {typeof c.content ===
                                                        'string'
                                                            ? c.content
                                                            : ''}
                                                    </Typography>
                                                </PaddedTypography>
                                            )
                                        })}
                                    </MultipleTypeContainer>
                                )
                            case 'text':
                                return (
                                    <PaddedTypography>
                                        <Typography
                                            key={contentKey}
                                            variant="body_1"
                                        >
                                            {typeof value.content === 'string'
                                                ? value.content
                                                : ''}
                                        </Typography>
                                    </PaddedTypography>
                                )
                            default:
                                return null
                        }
                    })}
                </ContentWrapper>
            )}
        </QuestionWrapper>
    )
}

export default Question
