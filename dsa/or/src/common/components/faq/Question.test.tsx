// @ts-nocheck
import React from 'react'
import {render, screen, fireEvent} from '@testing-library/react'
import Question from './Question'
import {FAQQuestionItem} from './interface'

describe('Question Component', () => {
    // Sample question data
    const textOnlyQuestion: FAQQuestionItem = {
        id: 'text-only',
        question: 'Text Only Question?',
        children: [
            {
                contentType: 'text',
                content: 'This is a text-only answer.',
            },
        ],
    }

    const mixedContentQuestion: FAQQuestionItem = {
        id: 'mixed-content',
        question: 'Mixed Content Question?',
        children: [
            {
                contentType: 'text',
                content: 'This is a text introduction.',
            },
            {
                contentType: 'list',
                content: ['Item 1', 'Item 2', 'Item 3'],
            },
        ],
    }

    it('renders question text correctly', () => {
        render(<Question question={textOnlyQuestion} />)
        expect(screen.getByText('Text Only Question?')).toBeInTheDocument()
    })

    it('content is hidden by default when defaultOpen is false', () => {
        render(<Question question={textOnlyQuestion} defaultOpen={false} />)
        expect(
            screen.queryByText('This is a text-only answer.'),
        ).not.toBeInTheDocument()
    })

    it('content is visible by default when defaultOpen is true', () => {
        render(<Question question={textOnlyQuestion} defaultOpen />)
        expect(
            screen.getByText('This is a text-only answer.'),
        ).toBeInTheDocument()
    })

    it('toggles content visibility when question header is clicked', () => {
        render(<Question question={textOnlyQuestion} />)

        // Content should be hidden initially
        expect(
            screen.queryByText('This is a text-only answer.'),
        ).not.toBeInTheDocument()

        // Click to expand
        fireEvent.click(screen.getByText('Text Only Question?'))
        expect(
            screen.getByText('This is a text-only answer.'),
        ).toBeInTheDocument()

        // Click again to collapse
        fireEvent.click(screen.getByText('Text Only Question?'))
        expect(
            screen.queryByText('This is a text-only answer.'),
        ).not.toBeInTheDocument()
    })

    it('renders text and list content correctly', () => {
        render(<Question question={mixedContentQuestion} defaultOpen />)

        // Check text content
        expect(
            screen.getByText('This is a text introduction.'),
        ).toBeInTheDocument()

        // Check list items
        expect(screen.getByText('Item 1')).toBeInTheDocument()
        expect(screen.getByText('Item 2')).toBeInTheDocument()
        expect(screen.getByText('Item 3')).toBeInTheDocument()
    })

    it('handles empty children array', () => {
        const emptyQuestion: FAQQuestionItem = {
            id: 'empty',
            question: 'Empty Question?',
            children: [],
        }

        render(<Question question={emptyQuestion} defaultOpen />)

        // Should render the question without crashing
        expect(screen.getByText('Empty Question?')).toBeInTheDocument()
    })

    it('handles invalid content type gracefully', () => {
        // @ts-ignore - Intentionally testing invalid data
        const invalidQuestion: FAQQuestionItem = {
            id: 'invalid',
            question: 'Invalid Question?',
            children: [
                {
                    contentType: 'invalid-type',
                    content: 'This has an invalid content type.',
                },
            ],
        }

        render(<Question question={invalidQuestion} defaultOpen />)

        // Should render the question without crashing
        expect(screen.getByText('Invalid Question?')).toBeInTheDocument()
    })
})
