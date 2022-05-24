const http = require('http')
const mongo = require('mongodb')
const socketio = require('socket.io')


class AnalysisToolServer {
    constructor() {
        this.DATABASE_URL = process.env['DATABASE_URL'] || 'mongodb://127.0.0.1:27017/'
        this.SERVER_PORT = process.env['SERVER_PORT'] || 8080
    }

    async start() {
        await this._setupDatabase()
        this.httpServer = new http.createServer()
        this.ioServer = socketio(this.httpServer)
        this.ioServer.on('connection', this._handleConnection.bind(this))
        this.httpServer.listen(this.SERVER_PORT, () => {
            console.log(`Listening on port ${this.SERVER_PORT}...`)
        })
    }

    async _setupDatabase() {
        this.databaseClient = await mongo.MongoClient.connect(this.DATABASE_URL)
        this.database = this.databaseClient.db('atool')
        const collections = await this.database.collections()
        if(!collections.some(c => c.collectionName == 'projects')) {
            await this.database.createCollection('projects')
        }
        this.projects = this.database.collection('projects')
    }

    _handleConnection(client) {
        client.on('event', (event) => {
            try {
                const name = event.name || 'unknown'
                if(name in this._eventHandlers) {
                    this._eventHandlers[name](client, event)
                } 
                else {
                    this._eventHandlers.unknown(client, event)
                }
            }
            catch(e) {
                console.log(e)
                console.log(data)
            }
        })
        client.on('disconnect', () => {
            this._sendClients(client)
        })
    }

    _sendClients(client) {
        const clients = this.ioServer.clients().connected
        Object.keys(client.rooms).forEach(name => {
            const room = this.ioServer.sockets.adapter.rooms[name]
            const roomClients = Object.keys(room.sockets)
                .map(id => clients[id])
                .reduce((m, client) => {
                    if(client.clientId && client.username) {
                        m[client.clientId] = client.username
                    }
                    return m
                }, {})
            this.ioServer.to(name).emit('event', {
                name: 'clients',
                clients: roomClients,
            })
        })
    }

    _eventHandlers = {
        unknown: (_, event) => {
            console.log('unknown event')
            console.log(event)
        },

        hello: (client, event) => {
            client.clientId = event.clientId
            client.username = event.username
        },

        getProject: async (client, event) => {
            const passcode = event['passcode']
            if(passcode && typeof passcode == 'string' && passcode.length == 24) {
                const id = mongo.ObjectId(passcode)
                const result = await this.projects.findOne({_id: id})
                if(result) {
                    client.projectId = passcode
                    client.join(passcode, () => {
                        this._sendClients(client)
                        client.emit('event', {
                            name: 'project',
                            project: result,
                        })
                    })    
                }
            }
        },

        publishProject: async (client, event) => {
            const project = event['project']
            const result = await this.projects.insertOne(project)
            const id = result.insertedId.toString()
            client.projectId = id
            client.join(id, () => {
                this._sendClients(client)
                client.emit('event', {
                    name: 'published',
                    passcode: id,
                })
            })
        },

        textFileAdd: async (client, event) => {
            if(client.projectId) {
                client.broadcast.to(client.projectId).emit('event', event);
                await this.projects.updateOne({
                    _id: mongo.ObjectId(client.projectId),
                }, {
                    $push: {textFiles: event['textFile']}
                })
            }
        },

        textFileRemove: async (client, event) => {
            if(client.projectId) {
                client.broadcast.to(client.projectId).emit('event', event);
                await this.projects.updateOne({
                    _id: mongo.ObjectId(client.projectId),
                }, {
                    $pull: {textFiles: {id: event['textFileId']}}
                })
            }
        },

        // TODO: textFileUpdate: async (client, event) => {},

        codeAdd: async (client, event) => {
            if(client.projectId) {
                client.broadcast.to(client.projectId).emit('event', event);
                await this.projects.updateOne({
                    _id: mongo.ObjectId(client.projectId),
                }, {
                    $push: {codes: event['code']}
                })
            }
        },

        codeRemove: async (client, event) => {
            if(client.projectId) {
                client.broadcast.to(client.projectId).emit('event', event);
                await this.projects.updateOne({
                    _id: mongo.ObjectId(client.projectId),
                }, {
                    $pull: {codes: {id: event['codeId']}}
                })
            }
        },

        codeUpdate: async (client, event) => {
            if(client.projectId) {
                client.broadcast.to(client.projectId).emit('event', event);
                const updates = {}
                if(event['codeName']) updates['codes.$.name'] = event['codeName']
                if(event['codeColor']) updates['codes.$.color'] = event['codeColor']
                await this.projects.updateOne({
                    _id: mongo.ObjectId(client.projectId),
                    'codes.id': event['codeId'], 
                }, {$set: updates})
            }
        },

        noteAdd: async (client, event) => {
            if(client.projectId) {
                client.broadcast.to(client.projectId).emit('event', event);
                await this.database.collection('projects').updateOne({
                    _id: mongo.ObjectId(client.projectId),
                }, {
                    $push: {notes: event['note']}
                })
            }
        },

        noteRemove: async (client, event) => {
            if(client.projectId) {
                client.broadcast.to(client.projectId).emit('event', event);
                await this.database.collection('projects').updateOne({
                    _id: mongo.ObjectId(client.projectId),
                }, {
                    $pull: {notes: {id: event['noteId']}}
                })
            }
        },

        noteUpdate: async (client, event) => {
            if(client.projectId) {
                client.broadcast.to(client.projectId).emit('event', event);
                const updates = {}
                if(event['text']) updates['notes.$.text'] = event['text']
                await this.database.collection('projects').updateOne({
                    _id: mongo.ObjectId(client.projectId),
                    'notes.id': event['noteId'], 
                }, {$set: updates})
            }
        },
    }
}


// main
(async () => {
    const server = new AnalysisToolServer()
    await server.start()
})()

