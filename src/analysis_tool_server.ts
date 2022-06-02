import * as https from 'https'
import * as http from 'http'
import * as fs from 'fs'
import * as io from 'socket.io'
import { Database } from './database'


export interface AnalysisToolServerConfig {
    databaseUrl: string
    port: number
    tlsCertPath?: string
    tlsKeyPath?: string
    passphrase?: string
}


interface Client extends io.Socket {
    clientId: string
    username: string
    projectId: string
    sendEvent(event: any): void
    broadcastToProject(event: any): void
    broadcastClientsToProject(): void
}


type EventHandler = (client: Client, event: any) => void


export class AnalysisToolServer {
    private config: AnalysisToolServerConfig
    private database: Database
    private httpServer: http.Server | https.Server
    private ioServer: io.Server

    public constructor(config: AnalysisToolServerConfig) {
        this.config = config
    }

    public async start() {
        this.database = await Database.connect(this.config.databaseUrl)
        this.createHttpServer()
        this.createIoServer()
        this.httpServer.listen(this.config.port, () => {
            console.log(`Listening on port ${this.config.port}...`)
        })
    }

    private createHttpServer() {
        if (this.config.tlsCertPath && this.config.tlsKeyPath) {
            console.log('Using HTTPS')
            this.httpServer = https.createServer({
                cert: fs.readFileSync(this.config.tlsCertPath),
                key: fs.readFileSync(this.config.tlsKeyPath),
                passphrase: this.config.passphrase,
            })
        }
        else {
            this.httpServer = http.createServer()
        }
    }

    private createIoServer() {
        this.ioServer = io(this.httpServer)
        this.ioServer.on('connection', this.handleConnection.bind(this))
    }

    private handleConnection(client: Client) {
        client.sendEvent = (event: any) => {
            client.emit('event', event)
        }

        client.broadcastToProject = (event: any) => {
            if (client.projectId) {
                client.broadcast.to(client.projectId).emit('event', event)
            }
        }

        client.broadcastClientsToProject = () => {
            const clients = this.ioServer.clients().connected
            Object.keys(client.rooms).forEach(name => {
                const room = this.ioServer.sockets.adapter.rooms[name]
                const roomClients = Object.keys(room.sockets)
                    .map(id => clients[id])
                    .reduce((m, client: Client) => {
                        if (client.clientId && client.username) {
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

        client.on('event', async event => {
            try {
                if (event.name in this.eventHandlers) {
                    await this.eventHandlers[event.name].call(this, client, event)
                }
                else {
                    console.log(`Unknown event: ${event.name}`)
                }
            }
            catch (error) {
                console.log(error)
            }
        })

        client.on('disconnect', () => {
            client.broadcastClientsToProject()
        })
    }

    private eventHandlers: { [name: string]: EventHandler } = {
        hello: async (client, event) => {
            client.clientId = event.clientId
            client.username = event.username
        },

        getProject: async (client, event) => {
            const project = await this.database.getProject(event.passcode)

            if (project) {
                client.projectId = event.passcode
                client.join(client.projectId, error => {
                    if (!error) {
                        client.broadcastClientsToProject()
                        client.sendEvent({
                            name: 'project',
                            project: project,
                        })
                    }
                })
            }
            else {
                client.sendEvent({
                    name: 'project',
                    project: null,
                })
            }
        },

        publishProject: async (client, event) => {
            const id = await this.database.insertProject(event.project)
            client.projectId = id
            client.join(id, error => {
                if (!error) {
                    client.broadcastClientsToProject()
                    client.sendEvent({
                        name: 'published',
                        passcode: id,
                    })
                }
            })
        },

        textFileAdd: async (client, event) => {
            if (client.projectId) {
                client.broadcastToProject(event)
                await this.database.addTextFile(client.projectId, event.textFile)
            }
        },

        textFileRemove: async (client, event) => {
            if (client.projectId) {
                client.broadcastToProject(event)
                await this.database.removeTextFile(client.projectId, event.textFileId)
            }
        },

        textFileUpdate: async (client, event) => {
            if (client.projectId) {
                client.broadcastToProject(event)
                await this.database.updateTextFile(
                    client.projectId,
                    event.textFileId,
                    event.textFileName,
                    event.rawText,
                )
            }
        },

        codingVersionAdd: async (client, event) => {
            if (client.projectId) {
                client.broadcastToProject(event)
                await this.database.addCodingVersion(
                    client.projectId,
                    event.textFileId,
                    event.codingVersion
                )
            }
        },

        codingVersionRemove: async (client, event) => {
            if (client.projectId) {
                client.broadcastToProject(event)
                await this.database.removeCodingVersion(
                    client.projectId,
                    event.textFileId,
                    event.codingVersionId
                )
            }
        },

        codingVersionUpdate: async (client, event) => {
            if (client.projectId) {
                client.broadcastToProject(event)
                await this.database.updateCodingVersion(
                    client.projectId,
                    event.textFileId,
                    event.codingVersionId,
                    event.codingVersionName,
                )
            }
        },

        codingAdd: async (client, event) => {
            if (client.projectId) {
                client.broadcastToProject(event)
                await this.database.addCoding(
                    client.projectId,
                    event.textFileId,
                    event.codingVersionId,
                    event.coding
                )
            }
        },

        codingRemove: async (client, event) => {
            if (client.projectId) {
                client.broadcastToProject(event)
                await this.database.removeCoding(
                    client.projectId,
                    event.textFileId,
                    event.codingVersionId,
                    event.coding
                )
            }
        },

        codeAdd: async (client, event) => {
            if (client.projectId) {
                client.broadcastToProject(event)
                await this.database.addCode(client.projectId, event.code)
            }
        },

        codeRemove: async (client, event) => {
            if (client.projectId) {
                client.broadcastToProject(event)
                await this.database.removeCode(client.projectId, event.codeId)
            }
        },

        codeUpdate: async (client, event) => {
            if (client.projectId) {
                client.broadcastToProject(event)
                await this.database.updateCode(
                    client.projectId,
                    event.codeId,
                    event.codeName,
                    event.codeColor
                )
            }
        },

        noteAdd: async (client, event) => {
            if (client.projectId) {
                client.broadcastToProject(event)
                await this.database.addNote(client.projectId, event.note)
            }
        },

        noteRemove: async (client, event) => {
            if (client.projectId) {
                client.broadcastToProject(event)
                await this.database.removeNote(client.projectId, event.noteId)
            }
        },

        noteUpdate: async (client, event) => {
            if (client.projectId) {
                client.broadcastToProject(event)
                await this.database.updateNote(
                    client.projectId,
                    event.noteId,
                    event.title,
                    event.text,
                )
            }
        },

        noteAddToLine: async (client, event) => {
            if (client.projectId) {
                client.broadcastToProject(event)
                await this.database.addNoteToLine(
                    client.projectId,
                    event.codingVersionId,
                    event.lineIndex,
                    event.noteId,
                )
            }
        },

        noteRemoveFromLine: async (client, event) => {
            if (client.projectId) {
                client.broadcastToProject(event)
                this.database.removeNoteFromLine(
                    client.projectId,
                    event.codingVersionId,
                    event.lineIndex,
                    event.noteId,
                )
            }
        },
    }
}
