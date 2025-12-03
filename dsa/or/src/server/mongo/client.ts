/* eslint-disable no-restricted-properties */
/* eslint-disable no-await-in-loop */
import {Db, MongoClient, ObjectId} from 'mongodb'
import logger from '../plugins/logger'
import secrets from '../secrets'
import mongodbOptions from './config'

const {mongodb} = secrets()
const {dbName} = mongodb

let client: MongoClient | null = null
let isConnecting = false
const MAX_RETRIES = 3

const connectToServer = async (retry = 0): Promise<MongoClient | null> => {
    if (client) return client
    if (isConnecting) {
        // Wait for ongoing connection
        while (!client && retry < MAX_RETRIES) {
            await new Promise((res) => setTimeout(res, 100))
        }
        return client
    }

    isConnecting = true
    const options = mongodbOptions()

    try {
        client = new MongoClient(options.url, {})
        await client.connect()
        logger.info('Connected to MongoDB')
        return client
    } catch (error) {
        logger.error(`MongoDB connection failed (attempt ${retry + 1}):`, error)
        client = null
        if (retry < MAX_RETRIES - 1) {
            await new Promise((res) =>
                setTimeout(res, 500 * Math.pow(2, retry)),
            )
            return connectToServer(retry + 1)
        }
        return null
    } finally {
        isConnecting = false
    }
}

const getClient = (): MongoClient => {
    if (!client)
        throw new Error(
            'MongoClient not initialized. Call connectToServer first.',
        )
    return client
}

const getDb = (db: string = dbName): Db => {
    return getClient().db(db)
}

const getCollectionInstance = (collectionName: string, db?: string) => {
    const dbClient = getDb(db || dbName)
    return dbClient.collection(collectionName)
}

const findOne = async <T>(
    collectionName: string,
    findByKey: string,
    findByValue: string,
): Promise<T | null> => {
    const collection = getCollectionInstance(collectionName)
    return collection.findOne({[findByKey]: findByValue}) as Promise<T | null>
}

const addOne = (collectionName: string, addObject: any) => {
    const collection = getCollectionInstance(collectionName)
    return collection.insertOne(addObject)
}

const editOne = (
    collectionName: string,
    updateKey: string,
    updateValue: string,
    updateObject: any,
) => {
    const collection = getCollectionInstance(collectionName)
    return collection.updateOne(
        {[updateKey]: updateValue},
        {$set: updateObject || {}},
    )
}

const findAllIn = (
    collectionName: string,
    findByKey: string,
    findByValue: Array<String>,
) => {
    const collection = getCollectionInstance(collectionName)
    return collection
        .find({[findByKey]: {$in: findByValue.map((i) => `${i}`)}})
        .toArray()
}

const findAllInObjectId = (
    collectionName: string,
    findByKey: string,
    findByValue: Array<string>,
) => {
    const collection = getCollectionInstance(collectionName)
    return collection
        .find({[findByKey]: {$in: findByValue.map((i) => new ObjectId(i))}})
        .toArray()
}

const findAllInWithBooleanFilter = (
    collectionName: string,
    findByKey: string,
    findByValue: Array<string>,
    filterKey: string,
    filterValue: boolean,
    limit: number,
) => {
    const collection = getCollectionInstance(collectionName)
    const query = {
        [filterKey]: Boolean(filterValue),
        [findByKey]: {$in: findByValue.map((i) => `${i}`)},
    }
    if (limit) {
        return collection.find(query).limit(limit).toArray()
    }
    return collection.find(query).toArray()
}

const findAll = (collectionName: string) => {
    const collection = getCollectionInstance(collectionName)
    return collection.find({}).toArray()
}

const findAllWithBoolean = (
    collectionName: string,
    filterObjKey: string,
    filterObjValue: boolean,
    limit: number,
) => {
    const collection = getCollectionInstance(collectionName)
    if (limit) {
        return collection
            .find({[filterObjKey]: Boolean(filterObjValue)})
            .limit(limit)
            .toArray()
    }
    return collection.find({[filterObjKey]: Boolean(filterObjValue)}).toArray()
}

const insertOne = async <T>(collectionName: string, data: T): Promise<void> => {
    const collection = getCollectionInstance(collectionName)
    await collection.insertOne(data)
}

const updateOne = async <T>(
    collectionName: string,
    key: string,
    keyValue: string,
    updateData: Partial<T>,
): Promise<void> => {
    const collection = getCollectionInstance(collectionName)
    await collection.updateOne(
        {[key]: keyValue},
        {$set: updateData},
        {upsert: false},
    )
}

const replaceOne = async <T>(
    collectionName: string,
    key: string,
    keyValue: string,
    newData: T,
): Promise<void> => {
    const collection = getCollectionInstance(collectionName)
    await collection.replaceOne({[key]: keyValue}, newData, {upsert: false})
}

export {
    addOne,
    connectToServer,
    editOne,
    findAll,
    findAllIn,
    findAllInWithBooleanFilter,
    findAllWithBoolean,
    findOne,
    getClient,
    getCollectionInstance,
    getDb,
    insertOne,
    updateOne,
    findAllInObjectId,
    replaceOne,
}
