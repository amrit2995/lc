import React from 'react'
import {render, screen, waitFor, fireEvent} from '@testing-library/react'
import FAQ from '.'
import * as useFetchModule from '../../hooks/useFetch'
// Import getBasePath is used in the mock

// Mock dependencies
jest.mock('../../hooks/useFetch', () => ({
    __esModule: true,
    default: jest.fn(),
}))

jest.mock('../../utils/commonUtils', () => ({
    getBasePath: jest.fn().mockReturnValue('/test-base-path'),
}))

describe('FAQ Component', () => {
    // Sample FAQ data
    const mockFAQData = {
        sections: [
            {
                id: 'data-metrics',
                header: 'Data & Metrics',
                questions: [
                    {
                        id: 'views-available',
                        question: 'What reporting views are available ?',
                        children: [
                            {
                                contentType: 'text',
                                content:
                                    'The platform provides multiple views to monitor performance.',
                            },
                            {
                                contentType: 'list',
                                content: [
                                    'Overview Screen: High-level performance metrics for all campaigns',
                                    'Campaign Performance Screen: Detailed metrics at the campaign and channel level',
                                ],
                            },
                        ],
                    },
                    {
                        id: 'metrics-available',
                        question:
                            'What types of metrics are available in the platform?',
                        children: [
                            {
                                contentType: 'text',
                                content: 'Metrics vary by screen and channel.',
                            },
                        ],
                    },
                ],
            },
        ],
    }

    beforeEach(() => {
        jest.clearAllMocks()
    })

    it('renders loading state when data is being fetched', () => {
        // Mock loading state
        ;(useFetchModule.default as jest.Mock).mockReturnValue({
            value: null,
            error: null,
        })

        render(<FAQ />)
        expect(screen.getByText('Loading FAQs…')).toBeInTheDocument()
    })

    it('renders error state when fetch fails', () => {
        // Mock error state
        ;(useFetchModule.default as jest.Mock).mockReturnValue({
            value: null,
            error: new Error('Failed to fetch'),
        })

        render(<FAQ />)
        expect(
            screen.getByText('Unable to load FAQs right now.'),
        ).toBeInTheDocument()
    })

    it('renders sections and questions when data is loaded', () => {
        // Mock successful data fetch
        ;(useFetchModule.default as jest.Mock).mockReturnValue({
            value: mockFAQData,
            error: null,
        })

        render(<FAQ />)

        // Check section headers and questions
        expect(screen.getByText('Data & Metrics')).toBeInTheDocument()
        expect(
            screen.getByText('What reporting views are available ?'),
        ).toBeInTheDocument()
        expect(
            screen.getByText(
                'What types of metrics are available in the platform?',
            ),
        ).toBeInTheDocument()
    })

    it('expands first question by default', () => {
        // Mock successful data fetch
        ;(useFetchModule.default as jest.Mock).mockReturnValue({
            value: mockFAQData,
            error: null,
        })

        render(<FAQ />)

        // First question's answer should be visible
        expect(
            screen.getByText(
                'The platform provides multiple views to monitor performance.',
            ),
        ).toBeInTheDocument()
        expect(
            screen.getByText(
                'Overview Screen: High-level performance metrics for all campaigns',
            ),
        ).toBeInTheDocument()
    })

    it('expands question when clicked', async () => {
        // Mock successful data fetch
        ;(useFetchModule.default as jest.Mock).mockReturnValue({
            value: mockFAQData,
            error: null,
        })

        render(<FAQ />)

        // Second question should be collapsed initially
        expect(
            screen.queryByText('Metrics vary by screen and channel.'),
        ).not.toBeInTheDocument()

        // Click to expand second question
        fireEvent.click(
            screen.getByText(
                'What types of metrics are available in the platform?',
            ),
        )

        await waitFor(() => {
            expect(
                screen.getByText('Metrics vary by screen and channel.'),
            ).toBeInTheDocument()
        })
    })

    it('calls useFetch with correct parameters', () => {
        ;(useFetchModule.default as jest.Mock).mockReturnValue({
            value: mockFAQData,
            error: null,
        })

        render(<FAQ />)

        expect(useFetchModule.default).toHaveBeenCalledWith({
            url: '/test-base-path/onering/nucleus?scope=faq-config',
            noCache: false,
        })
    })

    it('handles empty sections array', () => {
        ;(useFetchModule.default as jest.Mock).mockReturnValue({
            value: {sections: []},
            error: null,
        })

        render(<FAQ />)

        // Should render without crashing
        expect(
            screen.getByText('Frequently Asked Questions'),
        ).toBeInTheDocument()
    })
})
