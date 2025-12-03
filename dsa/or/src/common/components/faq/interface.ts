export interface FAQTextChild {
    contentType: 'text'
    content: string
}

export interface FAQListChild {
    contentType: 'list'
    content: string[]
}

export interface FAQLinkChild {
    label: string
    url: string
    contentType: 'link'
}

export interface FAQMultipleTypeChild {
    contentType: 'multi-type'
    children: Array<FAQTextChild | FAQLinkChild>
}

export type FAQQuestionChild =
    | FAQTextChild
    | FAQListChild
    | FAQMultipleTypeChild

export interface FAQQuestionItem {
    id?: string
    question: string
    children: FAQQuestionChild[]
}

export interface FAQSectionItem {
    id?: string
    header: string
    questions: FAQQuestionItem[]
}
