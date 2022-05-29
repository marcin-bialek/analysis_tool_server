import * as mongo from 'mongodb'


export class Database {
    private static databaseName = 'atool'
    private static projectsCollectionName = 'projects'
    private client: mongo.MongoClient
    private database: mongo.Db
    private projects: mongo.Collection<mongo.Document>

    private constructor(client: mongo.MongoClient, database: mongo.Db) {
        this.client = client
        this.database = database
        this.projects = this.database.collection(Database.projectsCollectionName)
    }

    public static async connect(url: string): Promise<Database> {
        const client = await mongo.MongoClient.connect(url)
        const database = client.db(Database.databaseName)
        const collections = await database.collections()

        if (!collections.some(c => c.collectionName == Database.projectsCollectionName)) {
            await database.createCollection(Database.projectsCollectionName)
        }

        return new Database(client, database)
    }

    public async close() {
        await this.client.close()
    }

    public async getProject(id: string): Promise<any> {
        if (id.length !== 24) {
            return null
        }

        return await this.projects.findOne({
            _id: new mongo.ObjectId(id),
        })
    }

    public async insertProject(project: any): Promise<string> {
        const result = await this.projects.insertOne(project)
        return result.insertedId.toString()
    }

    public async addTextFile(projectId: string, textFile: any): Promise<void> {
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId)
        }, {
            $push: {
                textFiles: textFile,
            }
        })
    }

    public async removeTextFile(projectId: string, textFileId: string): Promise<void> {
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
        }, {
            $pull: {
                textFiles: {
                    id: textFileId
                }
            }
        })
    }

    public async addCodingVersion(projectId: string, textFileId: string, codingVersion: any): Promise<void> {
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
        }, {
            $push: {
                'textFiles.$[textFile].codingVersions': codingVersion
            }
        }, {
            arrayFilters: [
                { 'textFile.id': textFileId },
            ]
        })
    }

    public async removeCodingVersion(projectId: string, textFileId: string, codingVersionId: string) {
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
        }, {
            $pull: {
                'textFiles.$[textFile].codingVersions': {
                    id: codingVersionId,
                }
            }
        }, {
            arrayFilters: [
                { 'textFile.id': textFileId },
            ]
        })
    }

    public async addCoding(projectId: string, textFileId: string, codingVersionId: string, coding: any) {
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
        }, {
            $push: {
                'textFiles.$[textFile].codingVersions.$[codingVersion].codings': coding
            }
        }, {
            arrayFilters: [
                { 'textFile.id': textFileId },
                { 'codingVersion.id': codingVersionId },
            ],
        })
    }

    public async removeCoding(projectId: string, textFileId: string, codingVersionId: string, coding: any) {
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
        }, {
            $pull: {
                'textFiles.$[textFile].codingVersions.$[codingVersion].codings': {
                    codeId: coding.codeId,
                    start: coding.start,
                    length: coding.length,
                }
            }
        }, {
            arrayFilters: [
                { 'textFile.id': textFileId },
                { 'codingVersion.id': codingVersionId },
            ]
        })
    }

    public async addCode(projectId: string, code: any) {
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
        }, {
            $push: {
                codes: code
            }
        })
    }

    public async removeCode(projectId: string, codeId: string) {
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
        }, {
            $pull: {
                codes: {
                    id: codeId
                }
            }
        })
    }

    public async updateCode(projectId: string, codeId: string, codeName: any, codeColor: any) {
        const updates = {}
        if (codeName) updates['codes.$.name'] = codeName
        if (codeColor) updates['codes.$.color'] = codeColor
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
            'codes.id': codeId,
        }, {
            $set: updates
        })
    }

    public async addNote(projectId: string, note: any) {
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
        }, {
            $push: {
                notes: note
            }
        })
    }

    public async removeNote(projectId: string, noteId: string) {
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
        }, {
            $pull: {
                notes: {
                    id: noteId
                }
            }
        })
    }

    public async updateNote(projectId: string, noteId: string, title: any, text: any) {
        const updates = {}
        if (title) updates['notes.$.title'] = title
        if (text) updates['notes.$.text'] = text
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
            'notes.id': noteId,
        }, {
            $set: updates
        })
    }

    public async addNoteToLine(projectId: string, codingVersionId: string, lineIndex: number, noteId: string) {
        // TODO
    }
}
