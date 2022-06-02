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
        const project = await this.projects.findOne({
            _id: new mongo.ObjectId(projectId),
        })
        const textFiles = project.textFiles.filter((t: any) => t.id == textFileId)
        if (textFiles.length > 0) {
            for (const version of textFiles[0].codingVersions) {
                await this.removeCodingVersion(projectId, textFileId, version.id);
            }
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
    }

    public async updateTextFile(projectId: string, textFileId: string, textFileName?: string, rawText?: string) {
        const updates = {}
        if (textFileName) updates['textFiles.$.name'] = textFileName
        if (rawText) {
            const project = await this.projects.findOne({
                _id: new mongo.ObjectId(projectId)
            })
            const textFiles = project.textFiles.filter((t: any) => t.id == textFileId)
            if (textFiles.length > 0 && textFiles[0].codingVersions.length > 0) {
                return
            }
            updates['textFiles.$.text'] = rawText
        }
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
            'textFiles.id': textFileId,
        }, {
            $set: updates
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
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
        }, {
            $unset: {
                [`notes.$[].codingLines.${codingVersionId}`]: {}
            }
        })
    }

    public async updateCodingVersion(projectId: string, textFileId: string, codingVersionId: string, codingVersionName?: string) {
        const updates = {}
        if (codingVersionName) updates['textFiles.$[textFile].codingVersions.$[codingVersion].name'] = codingVersionName
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
        }, {
            $set: updates
        }, {
            arrayFilters: [
                { 'textFile.id': textFileId },
                { 'codingVersion.id': codingVersionId },
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
                'textFiles.$[].codingVersions.$[].codings': {
                    codeId: codeId,
                }
            }
        })
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
        }, {
            $pull: {
                codes: {
                    id: codeId
                }
            }
        })
        const project = await this.projects.findOne({
            _id: new mongo.ObjectId(projectId)
        })
        const children = project.codes.filter((c: any) => c.parentId == codeId)
        for (const child of children) {
            await this.removeCode(projectId, child.id)
        }
    }

    public async updateCode(projectId: string, codeId: string, codeName?: string, codeColor?: number) {
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

    public async updateNote(projectId: string, noteId: string, title?: string, text?: string) {
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
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
        }, {
            $push: {
                [`notes.$[note].codingLines.${codingVersionId}`]: lineIndex,
            }
        }, {
            arrayFilters: [
                { 'note.id': noteId },
            ]
        })
    }

    public async removeNoteFromLine(projectId: string, codingVersionId: string, lineIndex: number, noteId: string) {
        await this.projects.updateOne({
            _id: new mongo.ObjectId(projectId),
        }, {
            $pull: {
                [`notes.$[note].codingLines.${codingVersionId}`]: lineIndex,
            }
        }, {
            arrayFilters: [
                { 'note.id': noteId },
            ]
        })
    }
}
