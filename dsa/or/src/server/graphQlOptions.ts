import {GraphQLObjectType, GraphQLString, GraphQLSchema} from 'graphql'

const BookType = new GraphQLObjectType({
    name: 'Book',
    fields: () => ({
        id: {
            type: GraphQLString,
        },
        name: {
            type: GraphQLString,
        },
    }),
})

const RootQuery = new GraphQLObjectType({
    name: 'RootQueryType',
    fields: {
        book: {
            type: BookType,
            args: {
                id: {
                    type: GraphQLString,
                },
            },
            resolve() {
                return {
                    id: '122',
                    name: 'test',
                    genre: 'test',
                }
            },
        },
    },
})

const schema = new GraphQLSchema({
    query: RootQuery,
})

export default schema
