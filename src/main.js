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
            this._sendClients(null)
        })
    }

    _sendClients(client) {
        const clients = this.ioServer.clients().connected
        const event = {
            name: 'clients',
            clients: Object.keys(clients).reduce((m, id) => {
                if(clients[id].clientId && clients[id].username) {
                    m[clients[id].clientId] = clients[id].username
                }
                return m
            }, {}),
        }
        if(client) {
            client.emit('event', event)
        }
        else {
            this.ioServer.emit('event', event)
            this.ioServer.em
        }
    }

    _eventHandlers = {
        unknown: (_, event) => {
            console.log('unknown event')
            console.log(event)
        },

        hello: (client, event) => {
            client.clientId = event.clientId
            client.username = event.username
            this._sendClients(null)
        },

        getClients: (client, _) => {
            this._sendClients(client)
        },

        getProject: async (client, event) => {
            const passcode = event['passcode']
            if(passcode && typeof passcode == 'string' && passcode.length == 24) {
                const id = mongo.ObjectId(passcode)
                const result = await this.projects.findOne({_id: id})
                if(result) {
                    client.emit('event', {
                        name: 'project',
                        project: result,
                    })
                }
            }
        },

        publishProject: async (client, event) => {
            const project = event['project']
            const result = await this.projects.insertOne(project)
            const id = result.insertedId.toString()
            client.emit('event', {
                name: 'published',
                passcode: id,
            })
        }
    }
}


// main
(async () => {
    const server = new AnalysisToolServer()
    await server.start()
})()

