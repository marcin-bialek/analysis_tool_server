const http = require('http')
const nosql = require('nosql')
const socketio = require('socket.io')


class AnalysisToolServer {
    constructor() {
        this.DATABASE_FILE = process.env['DATABASE_FILE'] || 'data.nosql'
        this.SERVER_PORT = process.env['SERVER_PORT'] || 8080
    }

    start() {
        this.database = nosql.load(this.DATABASE_FILE)
        this.httpServer = new http.createServer()
        this.ioServer = socketio(this.httpServer)
        this.ioServer.on('connection', this._handleConnection.bind(this))
        this.httpServer.listen(this.SERVER_PORT, () => {
            console.log(`Listening on port ${this.SERVER_PORT}...`)
        })
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

        getProject: (client, event) => {
            console.log(event)
        },
    }
}


// main
(() => {
    const server = new AnalysisToolServer()
    server.start()
})()

