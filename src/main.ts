import { AnalysisToolServer } from "./analysis_tool_server"


(async () => {
    const server = new AnalysisToolServer({
        databaseUrl: process.env['DATABASE_URL'] || 'mongodb://127.0.0.1:27017/',
        port: process.env['SERVER_PORT'] ? parseInt(process.env['SERVER_PORT']) : 8080,
        tlsCertPath: process.env['TLS_CERT_PATH'],
        tlsKeyPath: process.env['TLS_KEY_PATH'],
        passphrase: process.env['TLS_PASSPHRASE']
    })

    await server.start()
})()

